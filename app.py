import streamlit as st
import os
import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb

# Añadir el directorio src al path para imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Auto-setup para HF Spaces (solo primera vez)
if not Path("chroma_db").exists() or not any(Path("chroma_db").iterdir()):
    with st.spinner("🔧 Inicializando base de datos (solo primera vez, ~2 min)..."):
        import subprocess
        subprocess.run([sys.executable, "setup.py"], check=False)

# Importar funciones de LLM
from llm_integration import enrich_movie_recommendations, optimize_search_query

# Configuración de página
st.set_page_config(
    page_title="Film Suggester AI",
    page_icon="🎬",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .movie-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
        border: 1px solid #475569;
    }
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.5);
    }
    .movie-icon {
        font-size: 48px;
        float: left;
        margin-right: 15px;
    }
    .movie-title {
        font-size: 20px;
        font-weight: bold;
        color: #f1f5f9;
        margin-bottom: 8px;
    }
    .match-score {
        background: linear-gradient(90deg, #10b981, #059669);
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .card-content {
        overflow: hidden;
    }
    .ai-recommendation {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        border-left: 4px solid #a78bfa;
    }
    .ai-badge {
        background: rgba(255, 255, 255, 0.2);
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_models():
    """
    Carga el modelo y conecta a ChromaDB.
    Se ejecuta solo una vez gracias a @st.cache_resource
    """
    # Añadir print para invalidar cache si cambia el código
    print("🔄 (Re)Cargando modelos y conexión a DB...")
    # Modelo SOTA para RAG multilingüe: 10x más rápido, soporta hasta 8192 tokens
    model = SentenceTransformer('Alibaba-NLP/gte-multilingual-base', trust_remote_code=True)
    
    # Conectar a ChromaDB
    client = chromadb.PersistentClient(path='./chroma_db')
    collection = client.get_collection(name='movies')
    
    return model, collection

# Cargar recursos (solo se ejecuta una vez)
try:
    model, collection = load_models()
except Exception as e:
    st.error(f"Error conectando con la base de datos: {e}")
    st.stop()

# Título de la aplicación
st.title("🎬 Film Suggester AI")
st.markdown("Encuentra tu próxima película favorita usando búsqueda semántica avanzada.")

# Barra de búsqueda
query = st.text_input(
    "¿Qué tipo de película buscas?",
    placeholder="Ej: película de terror psicológica de los 90",
    label_visibility="collapsed"
)

# Búsqueda
if query:
    # PASO 1: Optimizar query con LLM
    with st.spinner("🤖 Optimizando tu búsqueda con IA..."):
        optimized_query = optimize_search_query(query)
    
    # Mostrar queries si son diferentes
    if optimized_query.lower().strip() != query.lower().strip():
        st.info(f"💡 **Query original:** {query}\n\n🎯 **Query optimizada por IA:** {optimized_query}")
    
    # PASO 2: Búsqueda semántica con query optimizada
    with st.spinner("🎬 Buscando las mejores coincidencias..."):
        # Convertir consulta OPTIMIZADA a vector
        query_embedding = model.encode(optimized_query).tolist()
        
        try:
            # Buscar en ChromaDB (pedir 20 para re-ranking)
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=20
            )
        except Exception as e:
            st.error("⚠️ Error de conexión con la base de datos. Por favor, recarga la página (F5) para restablecer la conexión.")
            print(f"Error query: {e}")
            st.stop()
    
    # Mostrar resultados
    st.markdown("---")
    st.subheader(f"🎯 Resultados para: *'{query}'*")
    
    if results and results['metadatas'] and len(results['metadatas'][0]) > 0:
        raw_metadatas = results['metadatas'][0]
        raw_distances = results['distances'][0]
        
        # Lógica de Re-ranking (Similitud + Rating)
        scored_results = []
        for meta, dist in zip(raw_metadatas, raw_distances):
            similarity = max(0, 1 - dist)
            
            # Obtener rating (prioridad: ml_rating > vote_average)
            # Nota: ml_rating viene como 'rating' en metadata
            rating = float(meta.get('rating', 0.0))
            if rating == 0:
                # Si no hay rating de usuarios, usar TMDB (escala 10 -> 5)
                rating = float(meta.get('vote_average', 0.0)) / 2.0
            
            # Normalizar rating (0-1)
            norm_rating = min(max(rating / 5.0, 0), 1)
            
            # Score final: 60% similitud, 40% rating
            # Esto asegura que salgan películas relevantes PERO buenas
            final_score = (similarity * 0.6) + (norm_rating * 0.4)
            
            scored_results.append({
                'metadata': meta,
                'distance': dist,
                'final_score': final_score,
                'rating': rating
            })
            
        # Ordenar por score final descendente
        scored_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Tomar top 6
        top_results = scored_results[:6]
        
        metadatas = [r['metadata'] for r in top_results]
        distances = [r['distance'] for r in top_results]
        
        # Preparar datos para LLM
        movie_results = []
        for metadata, distance in zip(metadatas, distances):
            match_score = max(0, (1 - distance) * 100)
            movie_results.append({
                'title': metadata['title'],
                'overview': metadata['overview'],
                'genres': metadata.get('genres_text', 'N/A'),
                'similarity': match_score
            })
        
        # PASO 3: Generar recomendación con LLM
        with st.spinner("🤖 Generando recomendaciones personalizadas con IA..."):
            ai_recommendation = enrich_movie_recommendations(query, movie_results)
        
        # Mostrar recomendación del LLM
        st.markdown(f"""
        <div class="ai-recommendation">
            <span class="ai-badge">🤖 RECOMENDACIÓN IA - NVIDIA NIMs + DeepSeek</span>
            <div style="margin-top: 10px; line-height: 1.6;">
                {ai_recommendation}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎬 Películas Encontradas")
        
        # Crear grid de 3 columnas
        for i in range(0, len(metadatas), 3):
            cols = st.columns(3)
            
            for j in range(3):
                idx = i + j
                if idx < len(metadatas):
                    metadata = metadatas[idx]
                    distance = distances[idx]
                    
                    # Calcular match score (1 - distance) * 100
                    match_score = max(0, (1 - distance) * 100)
                    
                    with cols[j]:
                        # Crear tarjeta con HTML
                        card_html = f"""
                        <div class="movie-card">
                            <div class="card-content">
                                <span class="movie-icon">🍿</span>
                                <div class="movie-title">{metadata['title']}</div>
                                <span class="match-score">🎯 {match_score:.1f}% Match</span>
                            </div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        # Expander para la sinopsis
                        with st.expander("📖 Leer trama"):
                            st.write(metadata['overview'])
        
    else:
        st.warning("⚠️ No se encontraron resultados")
else:
    # Mensaje inicial cuando no hay búsqueda
    st.info("👆 Escribe lo que buscas en el cuadro de búsqueda para comenzar")
    
    st.markdown("---")
    st.markdown("### 💡 Ejemplos de búsqueda:")
    
    examples_cols = st.columns(2)
    with examples_cols[0]:
        st.markdown("""
        - "Una película triste sobre pérdida"
        - "Comedia romántica en París"
        - "Acción y explosiones en el espacio"
        """)
    with examples_cols[1]:
        st.markdown("""
        - "Thriller psicológico con giros"
        - "Aventuras de piratas"
        - "Historia de amor imposible"
        """)
