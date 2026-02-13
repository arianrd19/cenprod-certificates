# Guía de Migración a Producción (Hostinger)

## Cuando subas el backend a Hostinger

### Paso 1: Importar Schema en Hostinger

1. Accede a **phpMyAdmin** desde cPanel de Hostinger
2. Selecciona la base de datos: `u508077754_cenprod_db`
3. Ve a la pestaña **"SQL"**
4. Copia y pega el contenido completo de `back/database/schema.sql`
5. Click en **"Continuar"**
6. ✅ Deberías ver "La consulta se ejecutó correctamente"

### Paso 2: Configurar .env en Hostinger

Cuando subas el código a Hostinger, crea el archivo `.env` con:

```env
# Database (localhost desde el servidor funciona)
DATABASE_URL=mysql+pymysql://u508077754_cenprod_user:ASD123$@localhost:3306/u508077754_cenprod_db

# Storage (ruta absoluta en Hostinger)
STORAGE_TYPE=local
STORAGE_PATH=/home/u508077754/domains/centroprofesionaldocente.com/public_html/uploads/certificados
BASE_STORAGE_URL=https://centroprofesionaldocente.com/uploads/certificados

# Application
BASE_URL=https://centroprofesionaldocente.com
SECRET_KEY=tu-secret-key-super-segura
```

### Paso 3: Crear Carpeta de Uploads

Desde **File Manager** en cPanel o por SSH:

```bash
cd ~/public_html
mkdir -p uploads/certificados
chmod 755 uploads/certificados
```

### Paso 4: Inicializar Base de Datos

Desde el servidor de Hostinger (SSH o ejecutar script):

```bash
cd /ruta/a/tu/back
python database/init_db.py
```

Esto creará el usuario admin si no existe.

## Resumen de Configuración

| Entorno | Base de Datos | Almacenamiento |
|---------|---------------|----------------|
| **Local (Desarrollo)** | SQLite (`cenprod_local.db`) | Carpeta local `uploads/` |
| **Hostinger (Producción)** | MySQL (`u508077754_cenprod_db`) | `/public_html/uploads/` |

## Migración de Datos

Si tienes datos en la base de datos local y quieres migrarlos:

1. Exporta desde SQLite local
2. Importa a MySQL en Hostinger usando phpMyAdmin

O usa el sistema híbrido: Google Sheets como respaldo y sincronización.
