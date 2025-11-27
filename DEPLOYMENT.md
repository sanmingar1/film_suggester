# 🚀 Guía de Despliegue en Hugging Face Spaces

## 📋 Prerequisitos

1. Cuenta en [Hugging Face](https://huggingface.co)
2. NVIDIA NIMs API Key ([obtener aquí](https://build.nvidia.com/))

## 🔧 Pasos de Despliegue

### 1. Crear el Space

1. Ve a https://huggingface.co/spaces
2. Click en "Create new Space"
3. Configura:
   - **Name**: `film-suggester-ai` (o el nombre que prefieras)
   - **License**: MIT
   - **SDK**: Streamlit
   - **Hardware**: CPU Basic (gratis)

### 2. Clonar el Repositorio del Space

```bash
# Clonar el Space vacío
git clone https://huggingface.co/spaces/TU_USUARIO/film-suggester-ai
cd film-suggester-ai

# Añadir tu proyecto como remote
git remote add local /home/santiago/Escritorio/film_suggester

# Traer archivos del proyecto
git fetch local
git merge local/main --allow-unrelated-histories
```

### 3. Preparar Archivos

Asegúrate de tener estos archivos:

```
film-suggester-ai/
├── README.md              ✅ (con metadata YAML)
├── app.py                 ✅
├── requirements.txt       ✅
├── src/
│   ├── llm_integration.py ✅
│   └── ...
├── chroma_db/            ⚠️ (ver nota abajo)
└── data/
    └── .gitkeep
```

**⚠️ Importante:** La carpeta `chroma_db/` (base de datos vectorial) debe incluirse porque HF no puede regenerarla automáticamente. **Solución:**

```bash
# Añadir chroma_db al repositorio
git add -f chroma_db/
git commit -m "Add pre-built vector database"
```

### 4. Configurar Secrets

En la interfaz web de tu Space:

1. Ve a "Settings" → "Repository secrets"
2. Añade:
   - **Name**: `NVIDIA_API_KEY`
   - **Value**: `tu_api_key_aqui`
3. Click "Add Secret"

### 5. Subir a Hugging Face

```bash
git add .
git commit -m "Initial deployment to HF Spaces"
git push origin main
```

### 6. Esperar el Build

El Space se construirá automáticamente. Puedes ver los logs en la pestaña "Build logs".

⏱️ **Tiempo estimado**: 5-10 minutos (primera vez)

---

## 🐛 Troubleshooting

### Error: "Module not found"
→ Verifica que `requirements.txt` tenga todas las dependencias

### Error: "NVIDIA_API_KEY not found"
→ Configura el secret en Settings → Repository secrets

### Error: "ChromaDB collection not found"
→ Asegúrate de incluir `chroma_db/` en el repositorio

### La app es lenta
→ Considera upgradearte a CPU/GPU mejorado en Settings

---

## 🔄 Actualizar el Space

Cada vez que hagas cambios:

```bash
git add .
git commit -m "Descripción de cambios"
git push origin main
```

El Space se reconstruirá automáticamente.

---

## 📊 Monitoreo

- **Logs**: Pestaña "Logs" en tu Space
- **Métricas**: Settings → Analytics
- **Duplicar**: Los usuarios pueden "Duplicate" tu Space para usarlo

---

## 💡 Optimizaciones Opcionales

### Reducir Tamaño de ChromaDB

Si `chroma_db/` es muy grande (>100MB):

```python
# En src/02_ingest.py
MAX_MOVIES = 5000  # Reducir dataset
```

Luego regenera:
```bash
rm -rf chroma_db
python src/02_ingest.py
```

### Usar GPU (Opcional, $$$)

Para embeddings más rápidos:
1. Settings → Hardware → Upgrade to GPU
2. Costo: ~$0.60/hora

---

## ✅ Checklist Final

- [ ] README.md tiene metadata YAML correcta
- [ ] requirements.txt está completo
- [ ] chroma_db/ está incluido en el repo
- [ ] NVIDIA_API_KEY configurado en Secrets
- [ ] La app funciona localmente
- [ ] Git push completado
- [ ] Space está público y funcionando

---

¡Tu aplicación estará disponible en: `https://huggingface.co/spaces/TU_USUARIO/film-suggester-ai`! 🎉
