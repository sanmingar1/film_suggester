"""
Script para listar modelos disponibles en NVIDIA NIMs
"""
from openai import OpenAI

NVIDIA_API_KEY = "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"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

try:
    client = OpenAI(
        base_url=NVIDIA_BASE_URL,
        api_key=NVIDIA_API_KEY
    )
    
    print("🔍 Listando modelos disponibles en NVIDIA NIMs...\n")
    
    models = client.models.list()
    
    print(f"Total de modelos encontrados: {len(models.data)}\n")
    
    # Buscar modelos de DeepSeek
    deepseek_models = [m for m in models.data if 'deepseek' in m.id.lower()]
    
    if deepseek_models:
        print("🎯 Modelos DeepSeek encontrados:")
        for model in deepseek_models:
            print(f"   - {model.id}")
    else:
        print("⚠️ No se encontraron modelos DeepSeek específicamente")
        print("\n📋 Primeros 20 modelos disponibles:")
        for i, model in enumerate(models.data[:20], 1):
            print(f"   {i}. {model.id}")
    
except Exception as e:
    print(f"❌ Error al listar modelos: {e}")
