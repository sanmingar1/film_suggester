#!/usr/bin/env python3
"""
Script para obtener datos reales de películas desde TMDB API
y crear los archivos CSV necesarios para el sistema de recomendación.
"""

import requests
import pandas as pd
import json
import time
from pathlib import Path

# Configuración
TMDB_API_KEY = input("Ingresa tu TMDB API Key: ").strip()
BASE_URL = "https://api.themoviedb.org/3"
DATA_DIR = Path(__file__).parent.parent / "data"

# Crear directorio si no existe
DATA_DIR.mkdir(exist_ok=True)

def fetch_popular_movies(num_pages=10):
    """Obtiene películas populares de TMDB"""
    print(f"\n🎬 Obteniendo películas populares (páginas: {num_pages})...")
    movies = []

    for page in range(1, num_pages + 1):
        url = f"{BASE_URL}/movie/popular"
        params = {
            "api_key": TMDB_API_KEY,
            "page": page,
            "language": "en-US"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            movies.extend(data['results'])
            print(f"   Página {page}/{num_pages} - {len(data['results'])} películas obtenidas")
            time.sleep(0.25)  # Respetar rate limits
        except Exception as e:
            print(f"   ⚠️  Error en página {page}: {e}")
            continue

    print(f"   ✅ Total: {len(movies)} películas")
    return movies

def fetch_movie_details(movie_id):
    """Obtiene detalles completos de una película"""
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"   ⚠️  Error obteniendo detalles de movie {movie_id}: {e}")
        return None

def fetch_movie_keywords(movie_id):
    """Obtiene keywords de una película"""
    url = f"{BASE_URL}/movie/{movie_id}/keywords"
    params = {"api_key": TMDB_API_KEY}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('keywords', [])
    except Exception as e:
        print(f"   ⚠️  Error obteniendo keywords de movie {movie_id}: {e}")
        return []

def fetch_movie_credits(movie_id):
    """Obtiene créditos (cast y crew) de una película"""
    url = f"{BASE_URL}/movie/{movie_id}/credits"
    params = {"api_key": TMDB_API_KEY}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return {
            'cast': data.get('cast', [])[:5],  # Top 5 actores
            'crew': [c for c in data.get('crew', []) if c.get('job') == 'Director']
        }
    except Exception as e:
        print(f"   ⚠️  Error obteniendo créditos de movie {movie_id}: {e}")
        return {'cast': [], 'crew': []}

def create_movies_metadata(movies):
    """Crea el archivo movies_metadata.csv"""
    print("\n📝 Creando movies_metadata.csv...")

    metadata_list = []
    for movie in movies:
        # Obtener detalles completos
        details = fetch_movie_details(movie['id'])
        if not details:
            continue

        metadata = {
            'id': movie['id'],
            'original_title': movie.get('original_title', ''),
            'overview': movie.get('overview', ''),
            'poster_path': movie.get('poster_path', ''),
            'genres': json.dumps([{'name': g['name']} for g in details.get('genres', [])]),
            'vote_average': movie.get('vote_average', 0),
            'tagline': details.get('tagline', '')
        }
        metadata_list.append(metadata)
        time.sleep(0.1)

    df = pd.DataFrame(metadata_list)
    df.to_csv(DATA_DIR / "movies_metadata.csv", index=False)
    print(f"   ✅ {len(df)} películas guardadas")
    return df

def create_keywords(movies):
    """Crea el archivo keywords.csv"""
    print("\n🏷️  Creando keywords.csv...")

    keywords_list = []
    for movie in movies:
        keywords = fetch_movie_keywords(movie['id'])
        keywords_formatted = json.dumps([{'name': k['name']} for k in keywords[:5]])  # Top 5

        keywords_list.append({
            'id': movie['id'],
            'keywords': keywords_formatted
        })
        time.sleep(0.1)

    df = pd.DataFrame(keywords_list)
    df.to_csv(DATA_DIR / "keywords.csv", index=False)
    print(f"   ✅ {len(df)} entradas guardadas")
    return df

def create_credits(movies):
    """Crea el archivo credits.csv"""
    print("\n🎭 Creando credits.csv...")

    credits_list = []
    for movie in movies:
        credits = fetch_movie_credits(movie['id'])

        cast_formatted = json.dumps([{'name': c['name']} for c in credits['cast']])
        crew_formatted = json.dumps([{'name': c['name'], 'job': c['job']} for c in credits['crew']])

        credits_list.append({
            'id': movie['id'],
            'cast': cast_formatted,
            'crew': crew_formatted
        })
        time.sleep(0.1)

    df = pd.DataFrame(credits_list)
    df.to_csv(DATA_DIR / "credits.csv", index=False)
    print(f"   ✅ {len(df)} entradas guardadas")
    return df

def create_links(movies):
    """Crea el archivo links.csv"""
    print("\n🔗 Creando links.csv...")

    links_list = []
    for movie in movies:
        # Obtener detalles para conseguir imdb_id
        details = fetch_movie_details(movie['id'])
        if not details:
            continue

        imdb_id = details.get('imdb_id', '').replace('tt', '') if details.get('imdb_id') else ''

        links_list.append({
            'movieId': movie['id'],
            'imdbId': imdb_id,
            'tmdbId': movie['id']
        })
        time.sleep(0.1)

    df = pd.DataFrame(links_list)
    df.to_csv(DATA_DIR / "links.csv", index=False)
    print(f"   ✅ {len(df)} enlaces guardados")
    return df

def create_ratings(movies, num_users=50):
    """Crea el archivo ratings.csv con ratings simulados basados en vote_average"""
    print(f"\n⭐ Creando ratings.csv ({num_users} usuarios simulados)...")

    import random
    ratings_list = []

    for user_id in range(1, num_users + 1):
        # Cada usuario califica entre 5-15 películas aleatorias
        num_ratings = random.randint(5, 15)
        sampled_movies = random.sample(movies, min(num_ratings, len(movies)))

        for movie in sampled_movies:
            # Basar el rating en vote_average de TMDB con algo de variación
            base_rating = movie.get('vote_average', 5) / 2  # Convertir de 0-10 a 0-5
            variation = random.uniform(-0.5, 0.5)
            rating = max(0.5, min(5.0, base_rating + variation))
            rating = round(rating * 2) / 2  # Redondear a .0 o .5

            timestamp = int(time.time()) - random.randint(0, 31536000)  # Último año

            ratings_list.append({
                'userId': user_id,
                'movieId': movie['id'],
                'rating': rating,
                'timestamp': timestamp
            })

    df = pd.DataFrame(ratings_list)
    df.to_csv(DATA_DIR / "ratings.csv", index=False)
    print(f"   ✅ {len(df)} ratings guardados")
    return df

def main():
    print("=" * 60)
    print("🎬 OBTENCIÓN DE DATOS DESDE TMDB API")
    print("=" * 60)

    # Validar API key
    print("\n🔑 Validando API key...")
    test_url = f"{BASE_URL}/configuration"
    try:
        response = requests.get(test_url, params={"api_key": TMDB_API_KEY})
        response.raise_for_status()
        print("   ✅ API key válida")
    except Exception as e:
        print(f"   ❌ Error: API key inválida o problema de conexión")
        print(f"   Detalle: {e}")
        return

    # Obtener películas populares
    movies = fetch_popular_movies(num_pages=10)  # ~200 películas

    if not movies:
        print("❌ No se pudieron obtener películas")
        return

    # Crear todos los archivos CSV
    create_movies_metadata(movies)
    create_keywords(movies)
    create_credits(movies)
    create_links(movies)
    create_ratings(movies, num_users=50)

    print("\n" + "=" * 60)
    print("✨ PROCESO COMPLETADO CON ÉXITO")
    print("=" * 60)
    print(f"📁 Archivos creados en: {DATA_DIR}")
    print(f"📊 Total de películas: {len(movies)}")
    print("\n📋 Próximos pasos:")
    print("   1. python src/01_clean_data.py")
    print("   2. python src/02_ingest.py")
    print("   3. streamlit run app.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
