#!/usr/bin/env python3
"""
Script de ayuda para preparar el service_account.json para Render
Convierte el JSON a una sola línea para copiar en variables de entorno
"""
import json
import sys
from pathlib import Path

def prepare_service_account_json():
    """Convierte service_account.json a formato de una línea para Render"""
    
    # Buscar el archivo service_account.json
    possible_paths = [
        Path('path/service_account.json'),
        Path('service_account.json'),
        Path('../path/service_account.json'),
    ]
    
    json_path = None
    for path in possible_paths:
        if path.exists():
            json_path = path
            break
    
    if not json_path:
        print("ERROR: No se encontro service_account.json")
        print("   Buscado en:")
        for path in possible_paths:
            print(f"   - {path}")
        sys.exit(1)
    
    try:
        # Leer el JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convertir a una sola línea
        json_one_line = json.dumps(data, separators=(',', ':'))
        
        print("OK: Service Account JSON preparado para Render")
        print("\n" + "="*80)
        print("COPIA ESTO EN LA VARIABLE DE ENTORNO 'GOOGLE_SERVICE_ACCOUNT' EN RENDER:")
        print("="*80)
        print(json_one_line)
        print("="*80)
        print("\nInstrucciones:")
        print("1. Copia todo el texto de arriba (desde { hasta })")
        print("2. Ve a Render Dashboard -> Tu Servicio -> Environment")
        print("3. Agrega nueva variable:")
        print("   Key: GOOGLE_SERVICE_ACCOUNT")
        print("   Value: (pega el JSON completo)")
        print("4. Guarda y redespliega")
        
        # También guardar en un archivo
        output_file = Path('service_account_one_line.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_one_line)
        
        print(f"\nTambien guardado en: {output_file}")
        print("   (Puedes abrir este archivo y copiar su contenido)")
        
    except json.JSONDecodeError as e:
        print(f"ERROR: El archivo JSON no es valido: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == '__main__':
    prepare_service_account_json()
