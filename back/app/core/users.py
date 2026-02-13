"""
Sistema de usuarios - Almacenamiento en memoria
Solo una cuenta de administrador, sin hash de contraseñas para simplificar
"""
from typing import Dict, Optional
from app.core.config import settings

# Almacenamiento en memoria - solo el admin
users_db: Dict[str, Dict] = {
    settings.ADMIN_EMAIL: {
        "email": settings.ADMIN_EMAIL,
        "password": settings.ADMIN_PASSWORD,  # Sin hash, comparación directa
        "role": "admin",
        "active": True
    }
}


def get_user(email: str) -> Optional[Dict]:
    """Obtiene un usuario por email"""
    return users_db.get(email)


def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Autentica un usuario - comparación directa de contraseña"""
    user = get_user(email)
    if not user:
        return None
    # Comparación directa (sin hash)
    if password != user["password"]:
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
        "password": password,  # Sin hash
        "role": role,
        "active": True
    }
    users_db[email] = user
    return user


def update_user_status(email: str, active: bool):
    """Activa o desactiva un usuario"""
    get_users_db()  # Asegurar que esté inicializado
    user = get_user(email)
    if not user:
        raise ValueError(f"Usuario {email} no encontrado")
    user["active"] = active
