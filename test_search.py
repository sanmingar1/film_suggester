"""
Test rápido de búsqueda con modelo original
"""
import chromadb
from sentence_transformers import SentenceTransformer

# Cargar modelo ORIGINAL (el que funciona)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Conectar a ChromaDB
client = chromadb.PersistentClient(path='./chroma_db')
collection = client.get_collection(name='movies')

print(f"Total películas en ChromaDB: {collection.count()}")

# Test de búsquedas
test_queries = [
    "Jumanji",
    "película de terror",
    "Toy Story",
    "acción"
]

for query in test_queries:
    print(f"\n🔍 Búsqueda: '{query}'")
    
    # Generar embedding con modelo multilingüe
    query_embedding = model.encode(query).tolist()
    
    # Buscar
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )
    
    print("Top 5 resultados:")
    for i, (meta, dist) in enumerate(zip(results['metadatas'][0], results['distances'][0]), 1):
        similarity = (1 - dist) * 100
        print(f"  {i}. {meta['title']} - Similitud: {similarity:.1f}%")
