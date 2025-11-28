"""
Test directo del optimizer real con NVIDIA NIMs
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from llm_integration import optimize_search_query
import chromadb
from sentence_transformers import SentenceTransformer

print("="*60)
print("TEST DEL OPTIMIZER REAL + BÚSQUEDA")
print("="*60)

# Cargar recursos
model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path='./chroma_db')
collection = client.get_collection(name='movies')

# Queries de prueba
test_queries = [
    "película de terror",
    "Jumanji",
    "comedia romántica",
    "acción con explosiones"
]

for query in test_queries:
    print(f"\n{'='*60}")
    print(f"📝 Query original: '{query}'")
    print("🤖 Optimizando con NVIDIA NIMs...")
    
    # Llamar al optimizer real
    optimized = optimize_search_query(query)
    
    print(f"✨ Query optimizada:")
    print(f"   {optimized}")
    
    # Hacer búsqueda con query optimizada
    embedding = model.encode(optimized).tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=5
    )
    
    print("\n🎬 Top 5 resultados:")
    for i, (meta, dist) in enumerate(zip(results['metadatas'][0], results['distances'][0]), 1):
        similarity = (1 - dist) * 100
        print(f"  {i}. {meta['title']} - {similarity:.1f}%")
