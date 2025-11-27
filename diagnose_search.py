"""
Script de diagnóstico para verificar la búsqueda semántica
"""
import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd

# Conectar a ChromaDB
client = chromadb.PersistentClient(path='./chroma_db')
collection = client.get_collection(name='movies')

# Cargar modelo
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

print("="*60)
print("🔍 DIAGNÓSTICO DE BÚSQUEDA SEMÁNTICA")
print("="*60)

# 1. Verificar cuántas películas hay
total = collection.count()
print(f"\n📊 Total de películas en ChromaDB: {total}")

# 2. Ver algunos ejemplos de datos
print("\n📝 Ejemplos de datos almacenados:")
sample = collection.peek(limit=3)
for i, (doc, meta) in enumerate(zip(sample['documents'], sample['metadatas']), 1):
    print(f"\n--- Película {i} ---")
    print(f"Título: {meta['title']}")
    print(f"Text completo: {doc[:200]}...")

# 3. Buscar películas de terror directamente en el CSV
print("\n" + "="*60)
print("🎭 VERIFICANDO PELÍCULAS DE TERROR EN EL CSV ORIGINAL")
print("="*60)

df = pd.read_csv('data/movies_clean.csv')
print(f"Total películas en CSV limpio: {len(df)}")

# Buscar películas que tengan "Horror" o "Terror" en géneros
horror_movies = df[df['genres_text'].str.contains('Horror', case=False, na=False)]
print(f"\n🎃 Películas con género Horror: {len(horror_movies)}")
if len(horror_movies) > 0:
    print("Ejemplos:")
    for i, row in horror_movies.head(5).iterrows():
        print(f"  - {row['title']} | Géneros: {row['genres_text']}")

# 4. Hacer búsqueda semántica de prueba
print("\n" + "="*60)
print("🔍 PRUEBA DE BÚSQUEDA SEMÁNTICA")
print("="*60)

queries = [
    "película de terror",
    "horror movie scary",
    "Terror miedo suspense"
]

for query in queries:
    print(f"\n🔎 Query: '{query}'")
    query_embedding = model.encode(query).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )
    
    print("Top 5 resultados:")
    for i, (meta, dist) in enumerate(zip(results['metadatas'][0], results['distances'][0]), 1):
        similarity = (1 - dist) * 100
        print(f"  {i}. {meta['title']} - Similitud: {similarity:.1f}%")

# 5. Verificar si películas de terror están en ChromaDB
print("\n" + "="*60)
print("🎃 VERIFICANDO SI HAY PELÍCULAS DE TERROR EN CHROMADB")
print("="*60)

# Obtener todas las películas (limitado a las primeras 1000 por rendimiento)
all_results = collection.get(limit=1000, include=['metadatas', 'documents'])

horror_count = 0
horror_examples = []

for doc, meta in zip(all_results['documents'], all_results['metadatas']):
    # Buscar "Horror", "Terror", o "Suspense" en el documento
    doc_lower = doc.lower()
    if 'horror' in doc_lower or 'terror' in doc_lower or 'scary' in doc_lower:
        horror_count += 1
        if len(horror_examples) < 5:
            horror_examples.append((meta['title'], doc[:150]))

print(f"Películas con palabras relacionadas a terror en las primeras 1000: {horror_count}")
if horror_examples:
    print("\nEjemplos:")
    for title, doc in horror_examples:
        print(f"  - {title}")
        print(f"    Text: {doc}...")
        print()
