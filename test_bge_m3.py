"""
Test BGE-M3 model performance
"""
import chromadb
from sentence_transformers import SentenceTransformer

print("="*60)
print("🧪 TEST: BGE-M3 MODEL")
print("="*60)

# Cargar modelo
print("\nCargando modelo BGE-M3...")
model = SentenceTransformer('BAAI/bge-m3')
client = chromadb.PersistentClient(path='./chroma_db')
collection = client.get_collection(name='movies')

print(f"📊 Total películas: {collection.count()}")

# Queries de prueba
test_queries = [
    "película de terror psicológico",
    "comedia romántica",
    "Toy Story",
    "highly rated horror classics"
]

for query in test_queries:
    print(f"\n{'='*60}")
    print(f"🔍 Query: '{query}'")
    
    # Sin prefijos (BGE-M3 no los necesita)
    query_embedding = model.encode(query).tolist()
    
    # Buscar
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )
    
    print("Top 5 resultados:")
    for i, (meta, dist) in enumerate(zip(results['metadatas'][0], results['distances'][0]), 1):
        similarity = (1 - dist) * 100
        rating = meta.get('rating', 0.0)
        print(f"  {i}. {meta['title']} | Sim: {similarity:.1f}% | Rating: {rating:.1f}")
