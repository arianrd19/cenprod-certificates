# Configuración de Base de Datos en Hostinger

## Paso 1: Crear Base de Datos en Hostinger

### Opción A: Usando phpMyAdmin (Recomendado - Más fácil)

1. **Accede a cPanel de Hostinger**
   - Ve a tu panel de control de Hostinger
   - Busca la sección "Bases de datos" o "Databases"

2. **Crear Base de Datos MySQL**
   - Click en "MySQL Databases" o "Crear Base de Datos"
   - Nombre sugerido: `cenprod_db` o `usuario_cenprod`
   - Click en "Crear"

3. **Crear Usuario de Base de Datos**
   - En la misma sección, crea un nuevo usuario
   - Usuario sugerido: `cenprod_user`
   - Contraseña: Genera una segura (guárdala)
   - Click en "Crear Usuario"

4. **Asignar Privilegios**
   - Asigna el usuario a la base de datos
   - Marca "ALL PRIVILEGES" (todos los privilegios)
   - Click en "Hacer Cambios"

5. **Acceder a phpMyAdmin**
   - Ve a "phpMyAdmin" en cPanel
   - Selecciona tu base de datos recién creada

6. **Importar Schema**
   - Click en la pestaña "SQL"
   - Copia y pega el contenido de `database/schema.sql`
   - Click en "Continuar"
   - ✅ Deberías ver "La consulta se ejecutó correctamente"

### Opción B: Usando Línea de Comandos (SSH)

Si tienes acceso SSH a Hostinger:

```bash
# Conectarte a MySQL
mysql -u usuario -p

# Crear base de datos
CREATE DATABASE cenprod_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Crear usuario (si no lo creaste desde cPanel)
CREATE USER 'cenprod_user'@'localhost' IDENTIFIED BY 'tu_password_segura';

# Asignar privilegios
GRANT ALL PRIVILEGES ON cenprod_db.* TO 'cenprod_user'@'localhost';
FLUSH PRIVILEGES;

# Usar la base de datos
USE cenprod_db;

# Importar schema
SOURCE /ruta/a/database/schema.sql;
```

## Paso 2: Configurar .env

Edita tu archivo `back/.env`:

```env
# Base de datos MySQL en Hostinger
# Formato: mysql+pymysql://usuario:password@host:puerto/nombre_db
DATABASE_URL=mysql+pymysql://cenprod_user:tu_password@localhost:3306/cenprod_db

# Almacenamiento local (Hostinger)
STORAGE_TYPE=local
STORAGE_PATH=/home/usuario/public_html/uploads/certificados
BASE_STORAGE_URL=https://centroprofesionaldocente.com/uploads/certificados
```

**Nota importante:** En Hostinger, el host suele ser `localhost` y el nombre de la base de datos incluye el prefijo de usuario. Por ejemplo:
- Si tu usuario de Hostinger es `usuario123`
- La base de datos será: `usuario123_cenprod`
- El usuario de DB será: `usuario123_cenprod_user`

## Paso 3: Crear Carpeta para PDFs

### Desde cPanel File Manager:

1. Ve a "File Manager" en cPanel
2. Navega a `public_html`
3. Crea carpeta: `uploads/certificados`
4. Click derecho → "Change Permissions" → Marca `755`

### O desde SSH:

```bash
cd ~/public_html
mkdir -p uploads/certificados
chmod 755 uploads/certificados
```

## Paso 4: Inicializar Base de Datos

Desde tu máquina local o servidor:

```bash
cd back
python database/init_db.py
```

Esto creará:
- ✅ Todas las tablas
- ✅ Usuario admin por defecto

## Paso 5: Verificar Conexión

Prueba la conexión:

```bash
cd back
python -c "from app.database.database import engine; engine.connect(); print('✅ Conexión exitosa')"
```

## Solución de Problemas

### Error: "Access denied"
- Verifica usuario y contraseña en `.env`
- Asegúrate de que el usuario tenga todos los privilegios

### Error: "Unknown database"
- Verifica que la base de datos existe
- Verifica el nombre en `DATABASE_URL`

### Error: "Can't connect to MySQL server"
- Verifica que el host sea `localhost` (no la IP)
- Verifica que MySQL esté corriendo

### Error de permisos en carpeta uploads
- Asegúrate de que la carpeta tenga permisos 755
- El usuario del servidor web debe poder escribir

## Estructura Final en Hostinger

```
/home/usuario/
├── public_html/
│   ├── uploads/
│   │   └── certificados/
│   │       ├── 2024/
│   │       │   ├── 01/
│   │       │   └── 02/
│   │       └── 2025/
│   └── (tu aplicación)
└── (otros archivos)
```

## URLs de Acceso

- **phpMyAdmin**: `https://tudominio.com/phpmyadmin` o desde cPanel
- **Base de datos**: `localhost:3306` (solo desde el servidor)
- **PDFs públicos**: `https://centroprofesionaldocente.com/uploads/certificados/2024/01/CERT-001.pdf`
