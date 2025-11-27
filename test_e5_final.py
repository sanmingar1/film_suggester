"""
Test FINAL con multilingual-e5-base + prefijos + texto natural
"""
import chromadb
from sentence_transformers import SentenceTransformer

print("="*60)
print("🧪 TEST FINAL: E5-BASE + PREFIJOS + TEXTO NATURAL")
print("="*60)

# Cargar modelo
model = SentenceTransformer('intfloat/multilingual-e5-base')
client = chromadb.PersistentClient(path='./chroma_db')
collection = client.get_collection(name='movies')

print(f"\n📊 Total películas: {collection.count()}")

# Queries de prueba
test_queries = [
    "película de terror",
    "comedia romántica",
    "acción con explosiones",
    "Jumanji",
    "Toy Story",
    "drama sobre la guerra",
    "highly rated horror movie"  # Test para ratings
]

for query in test_queries:
    print(f"\n{'='*60}")
    print(f"🔍 Query: '{query}'")
    
    # IMPORTANTE: Añadir prefijo query:
    query_text = f"query: {query}"
    query_embedding = model.encode(query_text).tolist()
    
    # Buscar
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )
    
    print("Top 5 resultados:")
    for i, (meta, dist) in enumerate(zip(results['metadatas'][0], results['distances'][0]), 1):
        similarity = (1 - dist) * 100
        print(f"  {i}. {meta['title']} - {similarity:.1f}%")
