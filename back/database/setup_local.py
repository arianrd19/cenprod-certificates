"""
Script para configurar base de datos local (SQLite) para desarrollo
Ejecutar: python database/setup_local.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from app.database.models import Base
from app.core.config import settings
from app.database.crud import create_usuario, get_usuario_by_email
from app.database.database import SessionLocal

def setup_local_db():
    """Configura base de datos SQLite local para desarrollo"""
    print("Configurando base de datos local (SQLite)...")
    
    # Usar SQLite para desarrollo local
    db_path = Path(__file__).parent.parent / "cenprod_local.db"
    database_url = f"sqlite:///{db_path}"
    
    print(f"Base de datos: {db_path}")
    
    # Crear engine
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},  # Necesario para SQLite
        echo=False
    )
    
    # Crear tablas
    print("\nCreando tablas...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Tablas creadas")
    
    # Crear usuario admin
    # Necesitamos crear una sesión manualmente
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    db = Session()
    
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
    
    print(f"\n[OK] Base de datos local configurada en: {db_path}")
    print("\nPara usar esta base de datos, agrega a tu .env:")
    print(f"DATABASE_URL=sqlite:///{db_path.relative_to(Path.cwd())}")

if __name__ == "__main__":
    setup_local_db()
