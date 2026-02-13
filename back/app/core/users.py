"""
Sistema de usuarios - Almacenamiento en memoria
"""
from typing import Dict, Optional
from app.core.security import get_password_hash, verify_password
from app.core.config import settings

# Almacenamiento en memoria - inicializar lazy para evitar problemas con bcrypt al importar
users_db: Dict[str, Dict] = {}

def _init_users_db():
    """Inicializa la base de datos de usuarios (lazy initialization)"""
    if not users_db:
        # Asegurar que la contraseña no sea demasiado larga (bcrypt tiene límite de 72 bytes)
        admin_password = settings.ADMIN_PASSWORD
        if len(admin_password.encode('utf-8')) > 72:
            admin_password = admin_password[:72]
        
        users_db[settings.ADMIN_EMAIL] = {
            "email": settings.ADMIN_EMAIL,
            "password": get_password_hash(admin_password),
            "role": "admin",
            "active": True
        }
    return users_db

# Inicializar al importar
_init_users_db()


def get_user(email: str) -> Optional[Dict]:
    """Obtiene un usuario por email"""
    return users_db.get(email)


def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Autentica un usuario"""
    user = get_user(email)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    if not user.get("active", True):
        return None
    return user


def create_user(email: str, password: str, role: str) -> Dict:
    """Crea un nuevo usuario (solo admin puede hacer esto)"""
    if get_user(email):
        raise ValueError(f"El usuario {email} ya existe")
    
    user = {
        "email": email,
        "password": get_password_hash(password),
        "role": role,
        "active": True
    }
    users_db[email] = user
    return user


def update_user_status(email: str, active: bool):
    """Activa o desactiva un usuario"""
    user = get_user(email)
    if not user:
        raise ValueError(f"Usuario {email} no encontrado")
    user["active"] = active
