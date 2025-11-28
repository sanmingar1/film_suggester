#!/usr/bin/env python3
"""
Script de inicialización de la base de datos.
Ejecuta el proceso de ingesta si la base de datos no existe.
"""
import os
import subprocess
import sys
from pathlib import Path

def setup_database():
    
    chroma_db = Path("chroma_db")
    
    # Verificar si ya existe la base de datos
    if chroma_db.exists() and any(chroma_db.iterdir()):
        print("✅ Base de datos ya existe, omitiendo setup...")
        return True
    
    print("="*60)
    print("🔧 INICIALIZANDO FILM SUGGESTER AI")
    print("="*60)
    print("\n📊 Generando base de datos vectorial...")
    print("   (Esto solo ocurre la primera vez, ~2-3 minutos)\n")
    
    try:
        # Verificar que existe movies_clean.csv
        if not Path("data/movies_clean.csv").exists():
            print("❌ Error: No se encuentra data/movies_clean.csv")
            print("   El dataset debe estar incluido en el repositorio.")
            return False
        
        # Ejecutar ingesta
        result = subprocess.run(
            [sys.executable, "src/02_ingest.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ Base de datos creada exitosamente!")
            return True
        else:
            print(f"\n❌ Error durante la ingesta:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
