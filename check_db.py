import chromadb

client = chromadb.PersistentClient(path='./chroma_db')
try:
    collection = client.get_collection('movies')
    print(f'✅ Colección encontrada con {collection.count()} películas')
except Exception as e:
    print(f'❌ Error: {e}')
