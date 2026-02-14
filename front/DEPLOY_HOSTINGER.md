# Guía de Despliegue del Frontend en Hostinger

Esta guía te ayudará a desplegar el frontend React en Hostinger.

## 📋 Prerequisitos

1. Cuenta en Hostinger con acceso a cPanel
2. Dominio configurado: `centroprofesionaldocente.com`
3. Backend funcionando en Render: `https://cenprod-backend.onrender.com`
4. Node.js instalado localmente (para construir el proyecto)

## 🚀 Paso 1: Configurar Variables de Entorno

### 1.1 Crear archivo `.env.production`

Ya está creado en `front/.env.production` con:
```
VITE_API_URL=https://cenprod-backend.onrender.com
```

Si tu backend tiene otra URL, actualiza este archivo.

## 🔧 Paso 2: Construir el Frontend

### 2.1 Instalar dependencias (si no lo has hecho)

```bash
cd cenprod-certificates/front
npm install
```

### 2.2 Construir para producción

```bash
npm run build
```

Esto generará la carpeta `dist/` con todos los archivos estáticos listos para producción.

### 2.3 Verificar el build

Deberías ver algo como:
```
dist/
├── assets/
│   ├── index-[hash].js
│   ├── index-[hash].css
│   └── logo-[hash].png
└── index.html
```

## 📤 Paso 3: Subir a Hostinger

### 3.1 Acceder a File Manager en cPanel

1. Inicia sesión en cPanel de Hostinger
2. Ve a **"File Manager"**
3. Navega a `public_html/` (o la carpeta raíz de tu dominio)

### 3.2 Subir archivos

**Opción A: Subir carpeta completa (recomendado)**

1. Comprime la carpeta `dist/` en un archivo ZIP
2. En File Manager, sube el ZIP a `public_html/`
3. Extrae el ZIP
4. Mueve todos los archivos de `dist/` a `public_html/`
5. Elimina la carpeta `dist/` vacía y el ZIP

**Opción B: Subir archivos individuales**

1. Sube todos los archivos de `dist/` directamente a `public_html/`
2. Asegúrate de mantener la estructura de carpetas:
   - `public_html/index.html`
   - `public_html/assets/` (con todos los archivos JS, CSS, imágenes)

### 3.3 Verificar permisos

Asegúrate de que los archivos tengan permisos correctos:
- Archivos: `644`
- Carpetas: `755`

En File Manager, puedes cambiar permisos haciendo click derecho → "Change Permissions"

## 📁 Paso 4: Crear Carpeta para Certificados PDFs

### 4.1 Crear carpeta de uploads

En File Manager, dentro de `public_html/`:

1. Crea la carpeta `uploads/`
2. Dentro de `uploads/`, crea `certificados/`
3. Estructura final: `public_html/uploads/certificados/`

### 4.2 Configurar permisos

La carpeta `uploads/certificados/` debe tener permisos `755` para que el backend pueda escribir archivos.

## 🔧 Paso 5: Configurar .htaccess (OBLIGATORIO)

**IMPORTANTE**: El archivo `.htaccess` es **OBLIGATORIO** para que React Router funcione correctamente.

1. El archivo `.htaccess` ya está creado en `front/.htaccess`
2. **DEBES subirlo a `public_html/`** en Hostinger
3. Asegúrate de que el archivo se llame exactamente `.htaccess` (con el punto al inicio)

**Verificación en Hostinger:**
- En File Manager, asegúrate de que puedas ver archivos ocultos (archivos que empiezan con `.`)
- Si no ves el `.htaccess`, activa "Show Hidden Files" en File Manager
- El archivo debe estar en la raíz: `public_html/.htaccess`

**Si el archivo no funciona:**
- Verifica que `mod_rewrite` esté habilitado en Hostinger (contacta soporte si es necesario)
- Verifica los permisos del archivo (debe ser `644`)

## ✅ Paso 6: Verificar el Despliegue

### 6.1 Verificar que el sitio carga

Visita: `https://centroprofesionaldocente.com`

Deberías ver la página de inicio o la página de verificación.

### 6.2 Verificar que las rutas funcionan

Prueba estas URLs:
- `https://centroprofesionaldocente.com/verificar`
- `https://centroprofesionaldocente.com/login`
- `https://centroprofesionaldocente.com/panel`

### 6.3 Verificar conexión con backend

1. Abre la consola del navegador (F12)
2. Intenta hacer login
3. Verifica que las peticiones vayan a `https://cenprod-backend.onrender.com/api/...`
4. No deberían aparecer errores de CORS

## 🔄 Paso 7: Actualizar CORS en Backend (si es necesario)

Si ves errores de CORS, verifica que en Render tengas configurado:

```
BASE_URL=https://centroprofesionaldocente.com
```

Y que el backend permita tu dominio en CORS (ya debería estar configurado).

## 📝 Notas Importantes

### Sobre las actualizaciones

Cada vez que hagas cambios en el frontend:

1. Ejecuta `npm run build` localmente
2. Sube los nuevos archivos de `dist/` a Hostinger
3. Reemplaza los archivos antiguos

### Sobre las variables de entorno

- Las variables de entorno (como `VITE_API_URL`) se "bakean" en el build
- Si cambias la URL del backend, necesitas reconstruir el frontend
- No puedes cambiar variables de entorno después del build sin reconstruir

### Sobre el almacenamiento de PDFs

- Los PDFs se guardarán en `public_html/uploads/certificados/YYYY/MM/`
- Asegúrate de que esta carpeta tenga permisos de escritura
- El backend en Render puede subir archivos vía FTP/SFTP si lo configuras

## 🐛 Solución de Problemas

### Error: "Cannot GET /panel"

**Solución**: Crea el archivo `.htaccess` con las reglas de rewrite (Paso 5)

### Error: CORS en el navegador

**Solución**: Verifica que `BASE_URL` en Render esté configurado correctamente

### Error: 404 en assets (JS, CSS)

**Solución**: Verifica que la carpeta `assets/` esté en `public_html/assets/` y tenga los archivos correctos

### El sitio carga pero no se conecta al backend

**Solución**: 
1. Verifica que `VITE_API_URL` esté en `.env.production`
2. Reconstruye el frontend: `npm run build`
3. Verifica en la consola del navegador qué URL está usando

## 📞 Siguiente Paso

Una vez que el frontend esté funcionando:
1. Prueba el login con las credenciales de admin
2. Prueba crear un certificado
3. Prueba verificar un certificado
4. Verifica que los PDFs se generen y guarden correctamente
