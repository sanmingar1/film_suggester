import pandas as pd
import json
import os

# Configuración de archivos
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Archivos de entrada
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
MOVIES_FILE = os.path.join(DATA_DIR, 'movies_metadata.csv')
KEYWORDS_FILE = os.path.join(DATA_DIR, 'keywords.csv')
CREDITS_FILE = os.path.join(DATA_DIR, 'credits.csv')

# Archivo de salida
OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'data', 'movies_clean.csv')

def parse_json_field(field, key_to_extract='name', max_items=None):
    """
    Parsea un campo JSON y extrae valores específicos.
    
    Args:
        field: Campo JSON como string
        key_to_extract: Clave a extraer de cada elemento (ej: 'name')
        max_items: Número máximo de items a extraer (None = todos)
    
    Returns:
        String con valores separados por comas
    """
    try:
        if pd.isna(field) or field == '':
            return ''
        
        data = json.loads(field.replace("'", '"'))
        
        if not isinstance(data, list):
            return ''
        
        values = [item.get(key_to_extract, '') for item in data if isinstance(item, dict)]
        
        if max_items:
            values = values[:max_items]
        
        return ', '.join(str(v) for v in values if v)
    
    except:
        return ''

def clean_and_combine_data():
    """
    Combina múltiples CSV, extrae información enriquecida y crea dataset limpio.
    """
    print("="*60)
    print("🎬 COMBINANDO DATASETS DE PELÍCULAS")
    print("="*60)
    
    # 1. Cargar movies_metadata.csv
    print("\n📂 Cargando movies_metadata.csv...")
    if not os.path.exists(MOVIES_FILE):
        print(f"❌ ERROR: No encuentro '{MOVIES_FILE}'")
        return
    
    # Usar low_memory=False para evitar warnings de tipos mixtos
    df_movies = pd.read_csv(MOVIES_FILE, low_memory=False)
    print(f"   ✅ Cargadas {len(df_movies):,} películas")
    
    df_movies = df_movies[pd.to_numeric(df_movies['id'], errors='coerce').notnull()]
    df_movies['id'] = df_movies['id'].astype(float).astype(int).astype(str)
    
    # 2. Cargar keywords.csv
    print("\n📂 Cargando keywords.csv...")
    if os.path.exists(KEYWORDS_FILE):
        df_keywords = pd.read_csv(KEYWORDS_FILE)
        df_keywords['id'] = df_keywords['id'].astype(str)
        print(f"   ✅ Cargadas {len(df_keywords):,} entradas de keywords")
        
        # Merge con movies
        df_movies = df_movies.merge(df_keywords, on='id', how='left')
        print(f"   🔗 Merge completado")
    else:
        print(f"   ⚠️  No encontrado (continuando sin keywords)")
        df_movies['keywords'] = ''
    
    # 3. Cargar credits.csv
    print("\n📂 Cargando credits.csv...")
    if os.path.exists(CREDITS_FILE):
        df_credits = pd.read_csv(CREDITS_FILE)
        df_credits['id'] = df_credits['id'].astype(str)
        print(f"   ✅ Cargadas {len(df_credits):,} entradas de credits")
        
        # Merge con movies
        df_movies = df_movies.merge(df_credits, on='id', how='left')
        print(f"   🔗 Merge completado")
    else:
        print(f"   ⚠️  No encontrado (continuando sin credits)")
        df_movies['cast'] = ''
        df_movies['crew'] = ''
    
    
    print(f"\n📊 Total películas después de merge: {len(df_movies):,}")
    
    # 4. Eliminar duplicados basados en ID
    print("\n🔄 Eliminando IDs duplicados...")
    initial_count = len(df_movies)
    df_movies = df_movies.drop_duplicates(subset=['id'], keep='first')
    duplicates_removed = initial_count - len(df_movies)
    if duplicates_removed > 0:
        print(f"   ❌ Removidos: {duplicates_removed:,} duplicados")
    print(f"   ✅ Películas únicas: {len(df_movies):,}")
    
    # 5. Filtrar películas sin overview (campo crítico)
    print("\n🧹 Filtrando películas sin sinopsis...")
    initial_count = len(df_movies)
    df_movies = df_movies[df_movies['overview'].notna()]
    df_movies = df_movies[df_movies['overview'].str.strip() != '']
    removed = initial_count - len(df_movies)
    print(f"   ❌ Removidas: {removed:,} películas sin overview")
    print(f"   ✅ Restantes: {len(df_movies):,} películas")
    
    print("\n📊 Cargando ratings y links...")
    # try:
    # Cargar links para mapear MovieLens ID -> TMDB ID
    links_df = pd.read_csv(os.path.join(DATA_DIR, 'links.csv'))
    links_df = links_df.dropna(subset=['tmdbId'])
    links_df['tmdbId'] = links_df['tmdbId'].astype(int).astype(str)
    links_df['movieId'] = links_df['movieId'].astype(str)
    
    # Cargar ratings (usando el archivo grande si existe, sino el pequeño)
    ratings_file = os.path.join(DATA_DIR, 'ratings.csv')
    if not os.path.exists(ratings_file):
        ratings_file = os.path.join(DATA_DIR, 'ratings_small.csv')
        
    print(f"   Leyendo ratings desde {os.path.basename(ratings_file)}...")
    # Leer solo columnas necesarias para ahorrar memoria
    ratings_df = pd.read_csv(ratings_file, usecols=['movieId', 'rating'])
    ratings_df['movieId'] = ratings_df['movieId'].astype(str)
    
    # Agrupar ratings por película
    print("   Agrupando ratings...")
    ratings_agg = ratings_df.groupby('movieId')['rating'].agg(['mean', 'count']).reset_index()
    ratings_agg.columns = ['movieId', 'ml_rating', 'ml_count']
    
    # Unir ratings con links
    ratings_final = pd.merge(ratings_agg, links_df[['movieId', 'tmdbId']], on='movieId', how='inner')
    
    # Agrupar por tmdbId para evitar duplicados (algunos tmdbId tienen múltiples movieId)
    print("   Consolidando ratings por TMDB ID...")
    ratings_final = ratings_final.groupby('tmdbId').agg({
        'ml_rating': 'mean',
        'ml_count': 'sum'
    }).reset_index()
    
    # Unir con dataframe principal
    print("   Fusionando ratings con metadatos...")
    df_movies = pd.merge(df_movies, ratings_final[['tmdbId', 'ml_rating', 'ml_count']], 
                       left_on='id', right_on='tmdbId', how='left')
    
    print(f"   ✅ Ratings integrados para {len(ratings_final):,} películas")
    
    print("\n🔧 Procesando campos JSON...")
    
    # Extraer nombres de géneros
    print("   📌 Procesando géneros...")
    df_movies['genres_text'] = df_movies['genres'].apply(
        lambda x: parse_json_field(x, 'name')
    )
    
    # Extraer keywords
    print("   📌 Procesando keywords...")
    df_movies['keywords_text'] = df_movies['keywords'].apply(
        lambda x: parse_json_field(x, 'name', max_items=10)
    )
    
    # Extraer nombres de actores principales (top 5)
    print("   📌 Procesando cast...")
    df_movies['cast_text'] = df_movies['cast'].apply(
        lambda x: parse_json_field(x, 'name', max_items=5)
    )
    
    # 6. Crear campo text_to_embed enriquecido
    print("\n🔗 Creando campo de texto enriquecido...")
    
    def create_enriched_text(row):
        """Combina toda la información relevante en un texto natural"""
        parts = []
        
        # Título y Sinopsis integrados
        title = row.get('original_title', '')
        overview = row.get('overview', '')
        
        if pd.notna(title) and pd.notna(overview):
            parts.append(f"{title}. {overview}")
        elif pd.notna(overview):
            parts.append(overview)
            
        # Géneros de forma natural
        genres = row.get('genres_text', '')
        if genres:
            parts.append(f"Esta es una película de {genres}.")
            
        # Cast
        cast = row.get('cast_text', '')
        if cast:
            parts.append(f"Protagonizada por {cast}.")
            
        # Keywords
        keywords = row.get('keywords_text', '')
        if keywords:
            parts.append(f"Trata sobre: {keywords}.")
            
        if pd.notna(row.get('ml_rating')) and row.get('ml_count', 0) > 10:
            rating = round(row['ml_rating'], 1)
            parts.append(f"Tiene una calificación de usuarios de {rating} sobre 5.")
            
        # Tagline
        tagline = row.get('tagline', '')
        if pd.notna(tagline) and str(tagline).strip():
            parts.append(f"{tagline}")
            
        return ' '.join(parts)
    
    df_movies['text_to_embed'] = df_movies.apply(create_enriched_text, axis=1)
    print("   ✅ Campo text_to_embed creado")
    
    # 7. Seleccionar columnas finales
    print("\n📋 Seleccionando columnas finales...")
    final_columns = [
        'id',
        'original_title',
        'overview',
        'poster_path',
        'genres_text',
        'cast_text',
        'keywords_text',
        'vote_average',
        'ml_rating',
        'ml_count',
        'text_to_embed'
    ]
    
    # Verificar que todas las columnas existan
    available_columns = [col for col in final_columns if col in df_movies.columns]
    df_clean = df_movies[available_columns].copy()
    
    # Renombrar para consistencia
    df_clean = df_clean.rename(columns={'original_title': 'title'})
    
    # 8. Guardar dataset limpio
    print(f"\n💾 Guardando dataset limpio en '{OUTPUT_FILE}'...")
    df_clean.to_csv(OUTPUT_FILE, index=False)
    
    # 9. Estadísticas finales
    print("\n" + "="*60)
    print("✨ PROCESO COMPLETADO CON ÉXITO")
    print("="*60)
    print(f"📊 Total películas en dataset limpio: {len(df_clean):,}")
    print(f"📁 Archivo guardado: {OUTPUT_FILE}")
    
    # Mostrar estadísticas de enriquecimiento
    has_genres = (df_clean['genres_text'] != '').sum()
    has_cast = (df_clean['cast_text'] != '').sum()
    has_keywords = (df_clean['keywords_text'] != '').sum()
    
    print(f"\n📈 Estadísticas de enriquecimiento:")
    print(f"   🎭 Películas con géneros: {has_genres:,} ({has_genres/len(df_clean)*100:.1f}%)")
    print(f"   🎬 Películas con cast: {has_cast:,} ({has_cast/len(df_clean)*100:.1f}%)")
    print(f"   🏷️  Películas con keywords: {has_keywords:,} ({has_keywords/len(df_clean)*100:.1f}%)")
    
    # Mostrar ejemplo de texto enriquecido
    print(f"\n📝 Ejemplo de texto enriquecido:")
    print(f"   {df_clean['text_to_embed'].iloc[0][:300]}...")
    print("="*60)
    
    return df_clean

if __name__ == "__main__":
    clean_and_combine_data()