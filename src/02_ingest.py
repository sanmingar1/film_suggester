import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import os

# Configuración - Rutas relativas al directorio raíz del proyecto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # Directorio padre de 'src'

CSV_FILE = os.path.join(PROJECT_ROOT, 'data', 'movies_clean.csv')
CHROMA_DB_DIR = os.path.join(PROJECT_ROOT, 'chroma_db')
COLLECTION_NAME = 'movies'
MODEL_NAME = 'Alibaba-NLP/gte-multilingual-base'  # SOTA para RAG multilingüe, 10x más rápido
MAX_MOVIES = 50000

def ingest_movies():
    """
    Carga películas, genera embeddings y los almacena en ChromaDB.
    """
    
    # 1. Verificar que existe el archivo CSV limpio
    if not os.path.exists(CSV_FILE):
        print(f"❌ ERROR: No encuentro '{CSV_FILE}'. Ejecuta primero 01_clean_data.py")
        return
    
    print("="*60)
    print("🎬 INICIANDO INGESTA DE PELÍCULAS A CHROMADB")
    print("="*60)
    
    # 2. Cargar datos limpios
    print(f"\n📂 Cargando datos desde '{CSV_FILE}'...")
    df = pd.read_csv(CSV_FILE)
    print(f"   Total de películas disponibles: {len(df)}")
    
    # Limitar a las primeras 1000 películas
    df = df.head(MAX_MOVIES)
    print(f"   Procesando las primeras {len(df)} películas")
    
    # 3. Cargar modelo de embeddings
    print(f"\n🤖 Cargando modelo de embeddings: {MODEL_NAME}")
    print("   (Esto puede tardar un poco la primera vez...)")
    model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)
    print("   ✅ Modelo cargado correctamente")
    
    # 4. Inicializar ChromaDB con persistencia
    print(f"\n💾 Inicializando ChromaDB en carpeta '{CHROMA_DB_DIR}'...")
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    
    # Eliminar colección si ya existe (para evitar duplicados)
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"   ♻️  Colección '{COLLECTION_NAME}' existente eliminada")
    except:
        pass
    
    # Crear nueva colección
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Movie embeddings for semantic search"}
    )
    print(f"   ✅ Colección '{COLLECTION_NAME}' creada")
    
    # 5. Generar embeddings e insertar en ChromaDB
    print(f"\n🔄 Generando embeddings e insertando en ChromaDB...")
    print(f"   Progreso:")
    
    # Procesar en lotes para mejor rendimiento
    batch_size = 100
    total_movies = len(df)
    
    for i in range(0, total_movies, batch_size):
        batch_df = df.iloc[i:i+batch_size]

        # Generar embeddings para este lote
        texts = batch_df['text_to_embed'].tolist()
        embeddings = model.encode(texts, show_progress_bar=False)
        
        # Preparar datos para ChromaDB
        ids = [str(row['id']) for _, row in batch_df.iterrows()]
        metadatas = [
            {
                'title': str(row['title']),
                'poster_path': str(row['poster_path']) if pd.notna(row['poster_path']) else '',
                'overview': str(row['overview'])[:500],
                'rating': float(row['ml_rating']) if pd.notna(row.get('ml_rating')) else 0.0,
                'vote_average': float(row['vote_average']) if pd.notna(row.get('vote_average')) else 0.0
            }
            for _, row in batch_df.iterrows()
        ]
        documents = texts  # El texto original también se guarda
        
        # Insertar en ChromaDB
        collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        # Mostrar progreso
        progress = min(i + batch_size, total_movies)
        percentage = (progress / total_movies) * 100
        print(f"   [{progress}/{total_movies}] {percentage:.1f}% completado")
    
    # 6. Resumen final
    print("\n" + "="*60)
    print("✨ INGESTA COMPLETADA CON ÉXITO")
    print("="*60)
    print(f"📊 Películas procesadas: {len(df)}")
    print(f"💾 Base de datos: {CHROMA_DB_DIR}/")
    print(f"📦 Colección: {COLLECTION_NAME}")
    print(f"🔍 Total de embeddings: {collection.count()}")
    print("="*60)
    
    # Verificación rápida
    print("\n🧪 Verificación rápida:")
    sample_result = collection.peek(limit=1)
    if sample_result and sample_result['metadatas']:
        print(f"   Ejemplo de película: '{sample_result['metadatas'][0]['title']}'")
        print("   ✅ Los datos se guardaron correctamente")
    
    return collection

if __name__ == "__main__":
    ingest_movies()
