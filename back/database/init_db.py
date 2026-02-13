"""
Script para inicializar la base de datos
Ejecutar: python database/init_db.py
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Agregar el directorio back al path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Cargar variables de entorno desde .env
load_dotenv()

def init_db():
    """Crea todas las tablas"""
    # Verificar si DATABASE_URL está configurado
    database_url = os.getenv('DATABASE_URL')
    
    # Verificar si DATABASE_URL está configurado (no es el valor por defecto)
    default_url = 'mysql+pymysql://usuario:password@localhost:3306/cenprod_db'
    is_default = not database_url or database_url.strip() == default_url.strip()
    
    if is_default:
        print("[ADVERTENCIA] DATABASE_URL no configurado o usando valores por defecto")
        print("\nPara configurar la base de datos:")
        print("1. Edita el archivo .env en la carpeta back/")
        print("2. Configura DATABASE_URL con tus credenciales:")
        print("   DATABASE_URL=mysql+pymysql://usuario:password@localhost:3306/nombre_db")
        print("\nSi aun no tienes la base de datos en Hostinger:")
        print("   - Ve a cPanel -> MySQL Databases")
        print("   - Crea base de datos y usuario")
        print("   - Importa database/schema.sql desde phpMyAdmin")
        print("\nEl sistema funcionara con Google Sheets hasta que configures la DB")
        return False
    
    try:
        from app.database.database import engine, Base
        from app.database.models import Cliente, Certificado, Mencion, Usuario
        from app.core.config import settings
        from app.database.crud import create_usuario, get_usuario_by_email
        from app.database.database import SessionLocal
        
        print("Conectando a la base de datos...")
        print(f"   URL: {database_url.split('@')[0]}@***")  # Ocultar password
        
        # Probar conexión
        engine.connect()
        print("[OK] Conexion exitosa")
        
        print("\nCreando tablas...")
        Base.metadata.create_all(bind=engine)
        print("[OK] Tablas creadas exitosamente")
        
        # Crear usuario admin por defecto si no existe
        db = SessionLocal()
        try:
            admin = get_usuario_by_email(db, settings.ADMIN_EMAIL)
            if not admin:
                print(f"\nCreando usuario admin: {settings.ADMIN_EMAIL}")
                create_usuario(
                    db,
                    email=settings.ADMIN_EMAIL,
                    password=settings.ADMIN_PASSWORD,
                    role='admin'
                )
                print("[OK] Usuario admin creado")
            else:
                print(f"[OK] Usuario admin ya existe: {settings.ADMIN_EMAIL}")
        finally:
            db.close()
        
        print("\n[OK] Base de datos inicializada correctamente")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        print("\nVerifica:")
        print("   1. Que la base de datos exista en Hostinger")
        print("   2. Que el usuario y contraseña sean correctos")
        print("   3. Que el usuario tenga todos los privilegios")
        print("   4. Que MySQL este corriendo")
        print("\nPuedes usar phpMyAdmin para verificar la conexion")
        return False

if __name__ == "__main__":
    success = init_db()
    if not success:
        sys.exit(1)
