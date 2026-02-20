"""
Sistema de usuarios - Almacenamiento en memoria
Contrasenas almacenadas con hash PBKDF2-SHA256
"""
import base64
import hashlib
import hmac
import os
from typing import Dict, Optional
from app.core.config import settings

# Formato: pbkdf2_sha256$<iteraciones>$<salt_b64>$<hash_b64>
_PBKDF2_PREFIX = "pbkdf2_sha256"
_PBKDF2_ITERATIONS = 210000


def _is_password_hashed(password: str) -> bool:
    return isinstance(password, str) and password.startswith(f"{_PBKDF2_PREFIX}$")


def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    salt_b64 = base64.b64encode(salt).decode("ascii")
    hash_b64 = base64.b64encode(dk).decode("ascii")
    return f"{_PBKDF2_PREFIX}${_PBKDF2_ITERATIONS}${salt_b64}${hash_b64}"


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        algo, iter_str, salt_b64, hash_b64 = stored_hash.split("$", 3)
        if algo != _PBKDF2_PREFIX:
            return False
        iterations = int(iter_str)
        salt = base64.b64decode(salt_b64.encode("ascii"))
        expected = base64.b64decode(hash_b64.encode("ascii"))
        calculated = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(calculated, expected)
    except Exception:
        return False


def _normalize_password_for_store(password: str) -> str:
    return password if _is_password_hashed(password) else _hash_password(password)


# Almacenamiento en memoria - solo el admin
users_db: Dict[str, Dict] = {
    settings.ADMIN_EMAIL: {
        "email": settings.ADMIN_EMAIL,
        "password": _normalize_password_for_store(settings.ADMIN_PASSWORD),
        "role": "admin",
        "active": True,
    }
}


def get_user(email: str) -> Optional[Dict]:
    """Obtiene un usuario por email"""
    return users_db.get(email)


def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Autentica usuario verificando hash; migra formato legado en memoria."""
    user = get_user(email)
    if not user:
        return None

    stored_password = user.get("password", "")
    valid_password = False

    if _is_password_hashed(stored_password):
        valid_password = _verify_password(password, stored_password)
    else:
        # Compatibilidad retroactiva: aceptar password legado y migrar a hash.
        valid_password = hmac.compare_digest(password, str(stored_password))
        if valid_password:
            user["password"] = _hash_password(password)

    if not valid_password:
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
        "password": _hash_password(password),
        "role": role,
        "active": True,
    }
    users_db[email] = user
    return user


def update_user_status(email: str, active: bool):
    """Activa o desactiva un usuario"""
    user = get_user(email)
    if not user:
        raise ValueError(f"Usuario {email} no encontrado")
    user["active"] = active
