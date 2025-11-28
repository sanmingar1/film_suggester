"""
Test ranking logic
"""
import chromadb
from sentence_transformers import SentenceTransformer

print("="*60)
print("🧪 TEST RANKING: SIMILITUD + RATING")
print("="*60)

# Cargar modelo
model = SentenceTransformer('Alibaba-NLP/gte-multilingual-base')
client = chromadb.PersistentClient(path='./chroma_db')
collection = client.get_collection(name='movies')

queries = [
    "película de terror",
    "Toy Story",
    "highly rated horror movie"
]

for query in queries:
    print(f"\n🔍 Query: '{query}'")
    
    query_embedding = model.encode(f"query: {query}").tolist()
    
    # Pedir 20 resultados
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=20
    )
    
    raw_metadatas = results['metadatas'][0]
    raw_distances = results['distances'][0]
    
    scored_results = []
    for meta, dist in zip(raw_metadatas, raw_distances):
        similarity = max(0, 1 - dist)
        
        rating = float(meta.get('rating', 0.0))
        if rating == 0:
            rating = float(meta.get('vote_average', 0.0)) / 2.0
        
        norm_rating = min(max(rating / 5.0, 0), 1)
        
        # Score final
        final_score = (similarity * 0.6) + (norm_rating * 0.4)
        
        scored_results.append({
            'title': meta['title'],
            'rating': rating,
            'similarity': similarity,
            'final_score': final_score
        })
        
    # Ordenar
    scored_results.sort(key=lambda x: x['final_score'], reverse=True)
    
    print("Top 5 Re-ranked:")
    for i, res in enumerate(scored_results[:5], 1):
        print(f"  {i}. {res['title']} | Rating: {res['rating']:.1f} | Sim: {res['similarity']:.2f} | Score: {res['final_score']:.3f}")
