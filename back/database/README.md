# Base de Datos - Sistema de Certificados

## Opciones de Almacenamiento

### Opción 1: Hostinger (Recomendada para MVP)

**Ventajas:**
- ✅ Ya tienes el hosting
- ✅ MySQL/PostgreSQL incluidos
- ✅ Almacenamiento de archivos en servidor
- ✅ Costo bajo
- ✅ Control total

**Implementación:**
1. Crear base de datos MySQL en Hostinger
2. Subir PDFs a carpeta `uploads/certificados/` en el servidor
3. Guardar rutas en la base de datos

**Configuración:**
```env
# .env
DATABASE_URL=mysql://usuario:password@hostinger.com:3306/nombre_db
STORAGE_TYPE=local
STORAGE_PATH=/home/usuario/public_html/uploads/certificados
BASE_STORAGE_URL=https://centroprofesionaldocente.com/uploads/certificados
```

### Opción 2: AWS S3 (Recomendada para producción)

**Ventajas:**
- ✅ Escalable
- ✅ CDN incluido
- ✅ Backups automáticos
- ✅ Muy confiable

**Desventajas:**
- ❌ Costos (pero muy bajos para empezar)
- ❌ Configuración adicional

**Configuración:**
```env
# .env
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=tu_key
AWS_SECRET_ACCESS_KEY=tu_secret
AWS_BUCKET_NAME=cenprod-certificados
AWS_REGION=us-east-1
```

### Opción 3: Google Drive (Consistente con Sheets)

**Ventajas:**
- ✅ Ya usas Google Sheets
- ✅ Integración fácil
- ✅ 15GB gratis

**Desventajas:**
- ❌ Límites de API
- ❌ Menos control

## Migración desde Google Sheets

El sistema puede funcionar con ambos:
- Google Sheets como backup/reportes
- Base de datos como fuente principal

## Estructura de Carpetas para PDFs

```
uploads/
├── certificados/
│   ├── 2024/
│   │   ├── 01/
│   │   │   ├── CERT-001.pdf
│   │   │   └── CERT-002.pdf
│   │   └── 02/
│   └── 2025/
└── menciones/
    └── ...
```
