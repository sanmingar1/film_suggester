"""
Test con queries mejoradas manualmente (simulando el LLM optimizer)
"""
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path='./chroma_db')
collection = client.get_collection(name='movies')

print("="*60)
print("TEST CON QUERIES BILINGÜES (SIMULANDO OPTIMIZER)")
print("="*60)

# Queries MEJORADAS con términos en inglés
test_cases = [
    ("Jumanji", "Jumanji adventure jungle family"),
    ("película de terror", "horror movie scary suspense thriller terror miedo"),
    ("acción", "action movie explosions fight car chase"),
    ("comedia romántica", "romantic comedy romance love funny"),
]

for original, optimized in test_cases:
    print(f"\n📝 Original: '{original}'")
    print(f"🎯 Optimizada: '{optimized}'")
    
    # Buscar con query optimizada
    query_embedding = model.encode(optimized).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )
    
    print("Top 5 resultados:")
    for i, (meta, dist) in enumerate(zip(results['metadatas'][0], results['distances'][0]), 1):
        similarity = (1 - dist) * 100
        print(f"  {i}. {meta['title']} - {similarity:.1f}%")
