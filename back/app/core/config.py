import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from typing import Optional

load_dotenv()  # carga .env en local; en Render no estorba

ROOT = Path(__file__).resolve().parent.parent.parent


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key_change_this')
    BASE_URL = os.getenv('BASE_URL', 'https://centroprofesionaldocente.com')
    ALGORITHM = os.getenv('ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    
    # Admin Default
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    
    # Sesión
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.getenv('SESSION_SECONDS', '3600'))
    )

    # IDs de Sheets
    SHEETS = {
        'certificados': {
            'id': os.getenv('GOOGLE_SHEET_ID', '15sZo9tyeF-hw0Pgd8YrDgJBNkUPXBF0u6BTEj8-p3Fw'),
            'worksheets': {
                'certificados': 'certificados',  # nombre de la hoja/worksheet original
                'certificados_qr': 'CERTIFICADOS QR'  # hoja donde se guardan los certificados con datos del cliente
            },
        },
        'compras': {
            'id': os.getenv('GOOGLE_SHEET_ID', '15sZo9tyeF-hw0Pgd8YrDgJBNkUPXBF0u6BTEj8-p3Fw'),
            'worksheets': {
                'compras': 'compras'  # hoja de compras/ventas de certificados
            },
        },
        'menciones': {
            'id': os.getenv('GOOGLE_SHEET_MENCIONES_ID', '1zaFo7ZJq0yAIjNwcTWJiCr3odCzs6ZYL_ibRE8yrkeM'),
            'worksheets': {
                'registro': 'MENCIONES'  # hoja de menciones con estructura: NRO, ESPECIALIDAD, P. CERTIFICADO, MENCIÓN, HORAS, F. INICIO, F. TÉRMINO, F. EMISIÓN
            },
        },
        'clientes': {
            'id': os.getenv('GOOGLE_SHEET_ID', '15sZo9tyeF-hw0Pgd8YrDgJBNkUPXBF0u6BTEj8-p3Fw'),
            'worksheets': {
                'clientes': 'CLIENTES'  # hoja de clientes
            },
        },
    }

    # Resuelve credenciales de Google en este orden:
    # 1) GOOGLE_SA_FILE (ruta a archivo: /etc/secrets/sa.json en Render, ./service_account.json en local)
    # 2) GOOGLE_APPLICATION_CREDENTIALS (convención Google)
    # 3) ./service_account.json si existe (solo local)
    # 4) path/service_account.json si existe (solo local)
    # Resuelve credenciales de Google verificando existencia
    SERVICE_ACCOUNT_FILE = None
    for candidate in [
        os.getenv('GOOGLE_SA_FILE'),
        os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
        os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE'),
        str(ROOT / 'service_account.json'),
        str(ROOT / 'path' / 'service_account.json')
    ]:
        if candidate and os.path.exists(candidate):
            SERVICE_ACCOUNT_FILE = str(candidate)
            break
    
    # Fallback para log de error si nada existe
    if not SERVICE_ACCOUNT_FILE:
        SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SA_FILE') or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    # Alternativa: JSON completo en env (si algún entorno lo usa)
    SERVICE_ACCOUNT_JSON = os.getenv('GOOGLE_SERVICE_ACCOUNT')
    # También soportar Base64 (más seguro para variables de entorno)
    SERVICE_ACCOUNT_JSON_B64 = os.getenv('GOOGLE_SERVICE_ACCOUNT_B64')


# Instancia global de configuración
settings = Config()
