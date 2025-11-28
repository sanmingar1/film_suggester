"""
Test del nuevo optimizer con descripciones
"""
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path='./chroma_db')
collection = client.get_collection(name='movies')

print("="*60)
print("TEST CON DESCRIPCIONES RICAS EN INGLÉS")
print("="*60)

# Simulando lo que el LLM generaría
test_cases = [
    ("Jumanji", "An adventure movie about a magical jungle board game that comes to life with exciting action and family-friendly fun."),
    ("película de terror", "A horror movie that creates fear and suspense through scary scenes, supernatural elements, and psychological tension. The film features frightening moments, mysterious atmosphere, and thriller elements that keep viewers on edge."),
    ("acción", "An action movie filled with intense fight scenes, explosions, car chases, and thrilling combat sequences that keep viewers engaged with non-stop excitement."),
    ("comedia romántica", "A romantic comedy about love and relationships with funny moments and heartwarming scenes. The story follows characters falling in love while dealing with humorous situations and emotional connections."),
]

for original, description in test_cases:
    print(f"\n📝 Query original: '{original}'")
    print(f"📖 Descripción generada:")
    print(f"   {description[:80]}...")
    
    # Buscar con descripción
    query_embedding = model.encode(description).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )
    
    print("Top 5 resultados:")
    for i, (meta, dist) in enumerate(zip(results['metadatas'][0], results['distances'][0]), 1):
        similarity = (1 - dist) * 100
        print(f"  {i}. {meta['title']} - {similarity:.1f}%")
