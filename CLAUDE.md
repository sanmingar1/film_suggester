# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Film Suggester is a semantic movie search application built with RAG (Retrieval Augmented Generation) architecture. It uses multilingual embeddings for semantic search in ChromaDB and enhances results with NVIDIA NIMs LLM recommendations.

The application is in Spanish and uses a Streamlit web interface for movie discovery.

## Development Workflow

### Initial Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Download datasets to data/ directory
# Required files: movies_metadata.csv, keywords.csv, credits.csv,
#                 links.csv, ratings.csv (or ratings_small.csv)
```

### Data Pipeline (must run in order)
```bash
# 1. Clean and combine datasets
python src/01_clean_data.py
# Output: data/movies_clean.csv

# 2. Generate embeddings and populate ChromaDB
python src/02_ingest.py
# Output: chroma_db/ directory with vector database
```

### Running the Application
```bash
# Start Streamlit web interface
streamlit run app.py
```

## Architecture

### Core Components

**app.py** - Streamlit web application
- Loads `Alibaba-NLP/gte-multilingual-base` model for semantic search
- Connects to ChromaDB persistent storage
- Implements 3-step search pipeline:
  1. Query optimization with LLM (expand search terms)
  2. Semantic search in ChromaDB (retrieves 20 candidates)
  3. Re-ranking with hybrid scoring (60% similarity + 40% user rating)
- Generates AI recommendations using NVIDIA NIMs

**src/01_clean_data.py** - Data preprocessing pipeline
- Merges multiple CSV datasets (movies_metadata, keywords, credits, links, ratings)
- Parses JSON fields (genres, cast, keywords)
- Integrates MovieLens ratings with TMDB metadata
- Creates enriched text for embeddings (title + overview + genres + cast + keywords + ratings)
- Filters movies without synopsis
- Output: `data/movies_clean.csv`

**src/02_ingest.py** - Vector database ingestion
- Loads cleaned data from `data/movies_clean.csv`
- Generates embeddings using `Alibaba-NLP/gte-multilingual-base`
- Stores in ChromaDB at `./chroma_db/`
- Processes up to MAX_MOVIES (default: 50,000) in batches of 100

**src/llm_integration.py** - NVIDIA NIMs LLM integration
- `optimize_search_query()`: Expands user queries with related terms in Spanish
- `enrich_movie_recommendations()`: Generates personalized movie analysis and recommendations
- Model: `deepseek-ai/deepseek-r1`
- NOTE: Contains hardcoded NVIDIA API key (should be moved to environment variable)

### Data Flow

1. User enters search query in Spanish → `optimize_search_query()` expands it
2. Optimized query → encoded with `gte-multilingual-base` embedding model
3. ChromaDB returns top 20 results by cosine similarity
4. Re-ranking applies hybrid score: `(similarity × 0.6) + (normalized_rating × 0.4)`
5. Top 6 results → `enrich_movie_recommendations()` generates AI analysis
6. Display results with match scores and AI insights

### Key Technical Details

**Embedding Model**: `Alibaba-NLP/gte-multilingual-base`
- State-of-the-art for multilingual RAG tasks
- 10x faster inference than decoder-based models
- Supports up to 8,192 tokens (excellent for long movie descriptions)
- 305M parameters, 768 dimensions
- Native Spanish support (70+ languages)
- Cached in Streamlit with `@st.cache_resource`

**Vector Database**: ChromaDB (Persistent)
- Collection name: `movies`
- Stores: embeddings, metadata (title, overview, rating, vote_average), documents
- Location: `./chroma_db/`

**Hybrid Scoring**:
- Prioritizes ml_rating (MovieLens user ratings, 0-5 scale) over vote_average (TMDB ratings, 0-10 scale)
- Normalizes rating to 0-1 range before combining with similarity
- Formula: `final_score = similarity * 0.6 + norm_rating * 0.4`

**LLM Integration**:
- Provider: NVIDIA NIMs
- Model: `deepseek-ai/deepseek-r1`
- Used for query optimization and result enrichment
- Temperature: 0.4 for query optimization, 0.7 for recommendations

## Important Notes

- The data/ directory starts empty (contains only .gitkeep) - datasets must be downloaded separately
- ChromaDB connection can fail if database is corrupted - user should reload page (F5) to reconnect
- Streamlit caching (@st.cache_resource) ensures model and DB are loaded only once
- All diagnostic/test scripts in root directory are development tools, not part of production flow
- API key in llm_integration.py should be refactored to use environment variables for security
