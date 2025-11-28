"""
Módulo para integración con NVIDIA NIMs LLM
"""
from openai import OpenAI
import os

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")

MODEL_NAME = "deepseek-ai/deepseek-r1"  # Modelo LLM

def get_llm_client():
    """Crea y retorna cliente de NVIDIA NIMs"""
    return OpenAI(
        base_url=NVIDIA_BASE_URL,
        api_key=NVIDIA_API_KEY
    )

def optimize_search_query(user_query):
    """
    Optimiza la query expandiéndola con términos relacionados.
    
    Args:
        user_query: Query original del usuario
    
    Returns:
        Query optimizada expandida
    """
    
    prompt = f"""Eres un experto en búsqueda de películas. Expande la siguiente consulta con términos y conceptos relacionados para una mejor búsqueda semántica.

Consulta: "{user_query}"

Tareas:
1. Identifica el género, temas y elementos clave
2. Agrega sinónimos y conceptos relacionados en español
3. Crea una descripción enriquecida (2-3 oraciones)

Ejemplo:
Input: "película de terror"
Output: "Película de terror con miedo, suspenso y elementos sobrenaturales. Film de horror con escenas aterradoras, atmósfera tenebrosa y tensión psicológica que mantiene al espectador en vilo."

Responde SOLO con la consulta expandida."""

    try:
        client = get_llm_client()
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Eres un experto en búsqueda de películas que expande queries para mejor búsqueda semántica."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=200,
            top_p=0.9
        )
        
        if response and response.choices and len(response.choices) > 0:
            message = response.choices[0].message
            
            if hasattr(message, 'content') and message.content:
                optimized = message.content.strip().strip('"').strip("'")
                return optimized
        
        return user_query
    
    except Exception as e:
        print(f"Error optimizando query: {e}")
        return user_query


def enrich_movie_recommendations(query, movie_results):
    """
    Enriquece los resultados de búsqueda con recomendaciones generadas por LLM.
    
    Args:
        query: La consulta de búsqueda del usuario
        movie_results: Lista de películas encontradas con sus metadatos
    
    Returns:
        Texto enriquecido con análisis y recomendaciones del LLM
    """
    
    # Preparar contexto con las películas encontradas
    movies_context = "\n\n".join([
        f"Película {i+1}: {movie['title']}\n"
        f"Sinopsis: {movie['overview']}\n"
        f"Géneros: {movie.get('genres', 'N/A')}\n"
        f"Similitud: {movie['similarity']:.1f}%"
        for i, movie in enumerate(movie_results[:3])  # Top 3 películas
    ])
    
    # Crear prompt para el LLM
    prompt = f"""Actúa como un experto crítico de cine y recomendador de películas.

El usuario buscó: "{query}"

Basándote en estas películas encontradas mediante búsqueda semántica:

{movies_context}

Por favor:
1. Analiza brevemente por qué estas películas coinciden con la búsqueda del usuario
2. Resume los temas o géneros comunes
3. Da una recomendación personalizada sobre cuál ver primero y por qué
4. Sugiere qué tipo de espectador disfrutaría más de cada película

Sé conciso pero informativo (máximo 150 palabras)."""

    try:
        client = get_llm_client()
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Eres un experto crítico de cine que da recomendaciones personalizadas y perspicaces."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2048,
            top_p=0.9
        )
        
        # Extraer contenido con mejor manejo
        if response and response.choices and len(response.choices) > 0:
            message = response.choices[0].message
            
            # Intentar extraer el contenido
            content = None
            if hasattr(message, 'content') and message.content:
                content = message.content
            elif hasattr(message, 'text') and message.text:
                content = message.text
            
            if content:
                return content
            else:
                return f"⚠️ Respuesta recibida pero sin contenido. Estructura: {str(message)[:200]}"
        else:
            return "⚠️ No se recibió respuesta válida del modelo"
    
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"⚠️ Error al generar recomendación: {str(e)}\n\nDetalle: {error_detail[:300]}"

def get_movie_insight(movie_title, movie_overview):
    """
    Genera un insight breve sobre una película específica.
    
    Args:
        movie_title: Título de la película
        movie_overview: Sinopsis de la película
    
    Returns:
        Insight generado por el LLM
    """
    
    prompt = f"""Película: {movie_title}

Sinopsis: {movie_overview}

En una sola frase corta (máximo 20 palabras), describe la esencia o tema principal de esta película."""

    try:
        client = get_llm_client()
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=50
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return ""
