---
title: Film Suggester AI
emoji: 🎬
colorFrom: purple
colorTo: blue
sdk: streamlit
sdk_version: "1.28.0"
app_file: app.py
pinned: false
license: mit
---

# 🎬 Film Suggester AI

Sistema de recomendación de películas potenciado por IA que combina búsqueda semántica multilingüe con análisis LLM.

## 🌟 Características

- **🔍 Búsqueda Semántica Avanzada**: Utiliza `multilingual-e5-base` para búsqueda vectorial en español e inglés
- **🤖 Optimización con LLM**: NVIDIA NIMs + DeepSeek para expandir y mejorar las consultas
- **⭐ Re-ranking Inteligente**: Combina similitud semántica (60%) con calificaciones de usuarios (40%)
- **📊 Dataset Enriquecido**: 44k+ películas con ratings de MovieLens integrados

## 🚀 Demo

Prueba la aplicación directamente en este Space. Algunas consultas de ejemplo:

- "película de terror psicológico de los 90"
- "comedia romántica ligera"
- "acción con explosiones y persecuciones"

## 🛠️ Tecnologías

- **Frontend**: Streamlit
- **Embeddings**: Sentence Transformers (multilingual-e5-base)
- **Vector DB**: ChromaDB
- **LLM**: NVIDIA NIMs API (DeepSeek-R1)
- **Datos**: MovieLens + TMDB

## ⚙️ Configuración Local

1. Clona el repositorio
```bash
git clone https://github.com/TU_USUARIO/film_suggester
cd film_suggester
```

2. Instala dependencias
```bash
pip install -r requirements.txt
```

3. Configura variables de entorno
```bash
cp .env.example .env
# Edita .env con tu NVIDIA_API_KEY
```

4. Ejecuta los scripts de preparación
```bash
python src/01_clean_data.py  # Limpiar datos
python src/02_ingest.py      # Generar embeddings
```

5. Lanza la aplicación
```bash
streamlit run app.py
```

## 📝 Licencia

MIT License - Ver archivo LICENSE para más detalles

## 🙏 Créditos

- Datos de películas: [MovieLens](https://grouplens.org/datasets/movielens/)
- Modelo de embeddings: [Multilingual-E5](https://huggingface.co/intfloat/multilingual-e5-base)
- LLM API: [NVIDIA NIMs](https://www.nvidia.com/en-us/ai/)
