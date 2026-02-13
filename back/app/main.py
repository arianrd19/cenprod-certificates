from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

from app.routers import public, admin, auth
from app.core.config import settings

limiter = Limiter(key_func=get_remote_address)

# Validar SECRET_KEY en producción
if os.getenv('ENVIRONMENT', 'development') == 'production':
    if settings.SECRET_KEY == 'dev_key_change_this':
        raise ValueError("SECRET_KEY debe estar configurado en producción. Configure la variable de entorno SECRET_KEY.")
    if settings.ADMIN_PASSWORD == 'admin123':
        raise ValueError("ADMIN_PASSWORD debe estar configurado en producción. Configure la variable de entorno ADMIN_PASSWORD.")

app = FastAPI(
    title="Sistema de Certificados con QR",
    description="API para gestión de certificados con integración a Google Sheets",
    version="1.0.0",
    docs_url="/docs" if os.getenv('ENVIRONMENT', 'development') != 'production' else None,
    redoc_url="/redoc" if os.getenv('ENVIRONMENT', 'development') != 'production' else None,
)

# CORS - Configuración para producción y desarrollo
allowed_origins = []
if os.getenv('ENVIRONMENT', 'development') == 'production':
    # En producción, solo permitir el dominio real
    if settings.BASE_URL:
        allowed_origins.append(settings.BASE_URL)
        # También permitir versión con www
        if settings.BASE_URL.startswith('https://'):
            allowed_origins.append(settings.BASE_URL.replace('https://', 'https://www.'))
else:
    # En desarrollo, permitir localhost
    allowed_origins.extend([
        "http://localhost:3000",
        "http://localhost:5173",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["Content-Type"],
    max_age=3600,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware para agregar headers de seguridad
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Headers de seguridad
    response.headers["X-Content-Type-Options"] = "nosniff"

    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Exception handler para errores de validación (422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Maneja errores de validación de Pydantic sin exponer información sensible"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error.get("loc", []))
        msg = error.get("msg", "Error de validación")
        errors.append(f"{field}: {msg}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "; ".join(errors) if errors else "Error de validación en los datos enviados"
        }
    )

# Exception handler global para errores no manejados
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Maneja errores no esperados sin exponer información sensible"""
    # En producción, no exponer detalles del error
    is_production = os.getenv('ENVIRONMENT', 'development') == 'production'
    detail = "Error interno del servidor" if is_production else str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail}
    )

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(public.router, prefix="/api/public", tags=["public"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

# Importar router de compras
from app.routers import compras
app.include_router(compras.router, prefix="/api/admin", tags=["compras"])

# Importar router de clientes
from app.routers import clientes
app.include_router(clientes.router, prefix="/api/admin", tags=["clientes"])


@app.get("/")
def root():
    return {"message": "Sistema de Certificados API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}
