"""
Verificar contenido de documentos en ChromaDB
"""
import chromadb

client = chromadb.PersistentClient(path='./chroma_db')
collection = client.get_collection(name='movies')

print(f"Total: {collection.count()}")
print("\nEjemplos:")
results = collection.peek(limit=3)
for doc in results['documents']:
    print(f"--- DOC END ---\n...{doc[-300:]}\n")
