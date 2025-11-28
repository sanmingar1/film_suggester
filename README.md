# 🎬 Film Suggester AI

Sistema inteligente de recomendación de películas que combina búsqueda semántica avanzada con análisis de lenguaje natural para ofrecer recomendaciones precisas y personalizadas.

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#-descripción-del-proyecto)
- [Características Principales](#-características-principales)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Pipeline de Datos](#-pipeline-de-datos)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Despliegue](#-despliegue)
- [Licencia](#-licencia)

## 🎯 Descripción del Proyecto

Film Suggester AI es una aplicación web desarrollada para ayudar a los usuarios a descubrir películas basándose en descripciones en lenguaje natural. A diferencia de los sistemas tradicionales de búsqueda por palabras clave, este sistema utiliza modelos de embeddings multilingües y técnicas de inteligencia artificial para entender el contexto y las intenciones del usuario.

El sistema puede procesar consultas como:
- "película de terror psicológica de los 90"
- "comedia romántica ligera para ver en pareja"
- "acción intensa con explosiones y persecuciones"
- "drama sobre pérdida y superación personal"

Y devuelve recomendaciones relevantes junto con análisis generado por modelos de lenguaje que explican por qué cada película se ajusta a la búsqueda.

## ✨ Características Principales

### 🔍 Búsqueda Semántica Multilingüe
- Modelo `multilingual-e5-base` para búsqueda vectorial en español e inglés
- Comprensión del contexto y significado, no solo palabras clave
- Soporte para descripciones abstractas y consultas complejas

### 🤖 Optimización de Consultas con IA
- Expansión automática de queries mediante NVIDIA NIMs + DeepSeek-R1
- Enriquecimiento de búsquedas con términos relacionados
- Mejora de precisión en resultados

### ⭐ Sistema de Re-ranking Inteligente
- Combinación de similitud semántica (60%) con calificaciones de usuarios (40%)
- Priorización de películas bien valoradas que también sean relevantes
- Balance entre precisión y calidad

### 📊 Dataset Enriquecido
- Más de 44,000 películas procesadas
- Integración de datos de MovieLens y TMDB
- Ratings de usuarios reales para mejor ranking
- Metadatos completos: géneros, cast, keywords, sinopsis

### 🎨 Interfaz Moderna
- Diseño responsive con Streamlit
- Tarjetas visuales con porcentajes de coincidencia
- Recomendaciones personalizadas generadas por IA
- Experiencia de usuario intuitiva

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐
│   Usuario       │
│  (Consulta en   │
│   español)      │
└────────┬────────┘
         │
         v
┌────────────────────────────────────┐
│   1. OPTIMIZACIÓN DE QUERY (LLM)  │
│   - NVIDIA NIMs + DeepSeek-R1      │
│   - Expansión con términos         │
└────────┬───────────────────────────┘
         │
         v
┌───────────────────────────────────────────────────────┐
│   2. BÚSQUEDA SEMÁNTICA                               │
│   - Embedding con 'Alibaba-NLP/gte-multilingual-base' │
│   - Query en ChromaDB                                 │
│   - Top 20 candidatos                                 │
└───────────────────────────────────────────────────────┘
         │
         v
┌────────────────────────────────────┐
│   3. RE-RANKING                    │
│   - 60% similitud semántica        │
│   - 40% rating de usuarios         │
│   - Top 6 resultados finales       │
└────────┬───────────────────────────┘
         │
         v
┌────────────────────────────────────┐
│   4. ANÁLISIS CON IA               │
│   - Generación de recomendaciones  │
│   - Explicación de coincidencias   │
│   - Sugerencias personalizadas     │
└────────┬───────────────────────────┘
         │
         v
┌────────────────────┐
│   Resultados       │
│   + Análisis       │
└────────────────────┘
```

## 🛠️ Tecnologías Utilizadas

### Frontend
- **Streamlit 1.28+**: Framework para aplicaciones web interactivas en Python
- **HTML/CSS**: Estilos personalizados para tarjetas y diseño visual

### Backend
- **Python 3.8+**: Lenguaje principal
- **Sentence Transformers**: Generación de embeddings semánticos
- **ChromaDB**: Base de datos vectorial para búsqueda eficiente
- **Pandas**: Procesamiento y limpieza de datos

### Modelos de IA
- **multilingual-e5-base**: Modelo de embeddings multilingüe (Inglés/Español)
- **NVIDIA NIMs API**: Infraestructura para modelos de lenguaje
- **DeepSeek-R1**: Modelo LLM para optimización y análisis

### Fuentes de Datos
- **MovieLens**: Ratings de usuarios reales (27M+ ratings)
- **TMDB (The Movie Database)**: Metadatos de películas

## 📦 Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- 4GB+ de espacio en disco (para modelos y datos)
- Conexión a internet (primera ejecución)

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <tu-repositorio>
cd film_suggester
```

2. **Crear entorno virtual (recomendado)**
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

Las dependencias principales son:
- `streamlit>=1.28.0`: Framework web
- `sentence-transformers>=2.2.0`: Modelos de embeddings
- `chromadb>=0.4.0`: Base de datos vectorial
- `openai>=1.0.0`: Cliente para NVIDIA NIMs API
- `pandas>=2.0.0`: Procesamiento de datos

## ⚙️ Configuración

### 1. Variables de Entorno

Crea un archivo `.env` en el directorio raíz basándote en `.env.example`:

```bash
cp .env.example .env
```

Edita `.env` con tu API key de NVIDIA:

```env
NVIDIA_API_KEY=tu_clave_api_aqui
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
```

**Obtener API Key de NVIDIA:**
1. Visita [NVIDIA NIMs](https://build.nvidia.com/)
2. Crea una cuenta o inicia sesión
3. Genera una API key en el panel de control
4. Copia la clave al archivo `.env`

### 2. Preparar Datos

El proyecto incluye los datos de MovieLens y TMDB en el directorio `data/`. Si necesitas regenerar los datos limpios:

**Paso 1: Limpiar y combinar datos**
```bash
python src/01_clean_data.py
```

Este script:
- Combina `movies_metadata.csv`, `keywords.csv`, `credits.csv`
- Integra ratings de MovieLens
- Genera descripciones enriquecidas
- Crea `data/movies_clean.csv`

**Paso 2: Generar embeddings**
```bash
python src/02_ingest.py
```

Este script:
- Carga el modelo `multilingual-e5-base`
- Genera embeddings para todas las películas
- Almacena vectores en ChromaDB
- Crea el directorio `chroma_db/`

> **Nota**: El proceso completo puede tardar 5-10 minutos en la primera ejecución.

## 🚀 Uso

### Ejecución Local

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Interfaz de Usuario

1. **Búsqueda**: Escribe tu consulta en lenguaje natural en el cuadro de búsqueda
2. **Procesamiento**: El sistema optimizará tu query automáticamente
3. **Resultados**: Verás:
   - Recomendación personalizada generada por IA
   - 6 películas con porcentaje de coincidencia
   - Sinopsis expandibles
4. **Interacción**: Click en "📖 Leer trama" para ver la sinopsis completa

### Ejemplos de Búsquedas

**Búsquedas por género:**
- "thriller psicológico con giros inesperados"
- "comedia familiar apropiada para niños"
- "ciencia ficción con viajes en el tiempo"

**Búsquedas por temas:**
- "película sobre amistad y lealtad"
- "historia de superación personal"
- "amor imposible en tiempos de guerra"

**Búsquedas por ambiente:**
- "película oscura y depresiva"
- "aventura emocionante y divertida"
- "drama intenso que haga llorar"

**Búsquedas específicas:**
- "acción de los 80s con Schwarzenegger"
- "animación japonesa sobre crecimiento"
- "western clásico en blanco y negro"

## 📊 Pipeline de Datos

### Flujo Completo del Procesamiento

```
RAW DATA
   │
   ├─ movies_metadata.csv  (45k+ películas)
   ├─ keywords.csv         (palabras clave)
   ├─ credits.csv          (cast y crew)
   ├─ links.csv            (IDs entre sistemas)
   └─ ratings.csv          (27M+ ratings)
   │
   v
[01_clean_data.py]
   │
   ├─ Merge de todos los CSV
   ├─ Limpieza de duplicados
   ├─ Parseo de campos JSON
   ├─ Agregación de ratings por película
   ├─ Creación de texto enriquecido
   │
   v
movies_clean.csv
   │
   └─ Columnas:
      ├─ id, title, overview
      ├─ genres_text, cast_text, keywords_text
      ├─ vote_average (TMDB), ml_rating (usuarios)
      └─ text_to_embed (descripción enriquecida)
   │
   v
[02_ingest.py]
   │
   ├─ Carga modelo multilingual-e5-base
   ├─ Genera embeddings (768 dimensiones)
   ├─ Almacena en ChromaDB
   │   └─ Índice HNSW para búsqueda rápida
   │
   v
chroma_db/
   └─ Base de datos vectorial lista para consultas
```

### Formato del Texto Enriquecido

Para cada película, se genera una descripción en lenguaje natural que incluye:

```
[Título]. [Sinopsis]. Esta es una película de [géneros]. 
Protagonizada por [actores principales]. Trata sobre: [keywords]. 
Tiene una calificación de usuarios de [rating] sobre 5.
```

Ejemplo:
```
Inception. A thief who steals corporate secrets... Esta es una 
película de Action, Science Fiction, Mystery. Protagonizada por 
Leonardo DiCaprio, Joseph Gordon-Levitt, Ellen Page. Trata sobre: 
dream, subconscious, heist. Tiene una calificación de usuarios 
de 4.3 sobre 5.
```

## 📂 Estructura del Proyecto

```
film_suggester/
│
├── app.py                    # Aplicación principal Streamlit
├── setup.py                  # Script de inicialización automática
├── requirements.txt          # Dependencias de Python
├── .env.example              # Plantilla de variables de entorno
├── .gitignore                # Archivos ignorados por Git
│
├── src/                      # Código fuente
│   ├── 01_clean_data.py      # Limpieza y combinación de datos
│   ├── 02_ingest.py          # Generación de embeddings y DB
│   ├── llm_integration.py    # Integración con NVIDIA NIMs
│   └── fetch_tmdb_data.py    # Utilidad para obtener datos TMDB
│
├── data/                     # Datos de películas
│   ├── movies_metadata.csv   # Metadatos base
│   ├── keywords.csv          # Palabras clave
│   ├── credits.csv           # Cast y crew
│   ├── links.csv             # Enlaces entre sistemas
│   ├── ratings.csv           # Ratings de usuarios
│   └── movies_clean.csv      # Dataset procesado
│
├── chroma_db/                # Base de datos vectorial (generada)
│   └── [archivos de ChromaDB]
│
├── tests/                    # Tests del proyecto
│   ├── test_search.py
│   ├── test_ranking.py
│   └── ...
│
├── scripts/                  # Scripts de utilidad
│   ├── list_nvidia_models.py
│   ├── diagnose_search.py
│   └── ...
│
└── venv/                     # Entorno virtual (opcional)
```

### Descripción de Archivos Principales

**`app.py`**
- Interfaz Streamlit
- Lógica de búsqueda y re-ranking
- Integración de todos los componentes
- Manejo de caché de modelos

**`src/01_clean_data.py`**
- Combinación de datasets CSV
- Parseo de campos JSON
- Agregación de ratings
- Generación de texto enriquecido

**`src/02_ingest.py`**
- Carga del modelo de embeddings
- Procesamiento por lotes
- Creación de base de datos vectorial
- Validación de datos

**`src/llm_integration.py`**
- Cliente de NVIDIA NIMs API
- Función de optimización de queries
- Generación de recomendaciones
- Manejo de errores y reintentos

**`src/fetch_tmdb_data.py`**
- Utilidad para obtener datos frescos de TMDB
- Creación de CSVs desde cero
- Manejo de rate limits de la API

## 🌐 Despliegue

### Despliegue en Streamlit Cloud

1. **Preparar repositorio en GitHub**
   - Push del código a GitHub
   - Incluir `data/` en el repositorio

2. **Conectar con Streamlit Cloud**
   - Visita [streamlit.io/cloud](https://streamlit.io/cloud)
   - Conecta tu repositorio de GitHub
   - Selecciona `app.py` como archivo principal

3. **Configurar secretos**
   - En Advanced settings > Secrets:
   ```toml
   NVIDIA_API_KEY = "tu_clave_aqui"
   NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
   ```

4. **Deploy**
   - Click en "Deploy"
   - La app estará lista en minutos

### Consideraciones de Despliegue

**Recursos necesarios:**
- RAM: 2GB mínimo (4GB recomendado)
- Disco: 2GB para modelos + datos
- CPU: 2 cores recomendado

**Optimizaciones:**
- Ajustar `MAX_MOVIES` en `02_ingest.py` para reducir tamaño de DB
- Usar modelos más pequeños si hay limitaciones de memoria
- Implementar caché de queries frecuentes

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo LICENSE para más detalles.

## 🙏 Agradecimientos

- **MovieLens**: Por proporcionar datasets de ratings reales
  - [grouplens.org/datasets/movielens/](https://grouplens.org/datasets/movielens/)
  
- **TMDB**: Por los metadatos completos de películas
  - [themoviedb.org](https://www.themoviedb.org/)
  
- **Equipo de Sentence Transformers**: Por el modelo multilingual-e5
  - [huggingface.co/intfloat/multilingual-e5-base](https://huggingface.co/intfloat/multilingual-e5-base)
  
- **NVIDIA**: Por proporcionar acceso a NIMs API y modelos LLM
  - [nvidia.com/en-us/ai/](https://www.nvidia.com/en-us/ai/)

---

**Desarrollado con ❤️ usando Python y Streamlit**
