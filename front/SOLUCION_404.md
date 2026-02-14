# Solución para Error 404 en Rutas

Si estás viendo errores 404 al acceder a rutas como `/login`, `/panel`, etc., pero la página principal (`/`) sí funciona, el problema es que el `.htaccess` no está funcionando correctamente.

## 🔍 Diagnóstico

El error 404 significa que el servidor no está redirigiendo las rutas a `index.html`. Esto puede deberse a:

1. El archivo `.htaccess` no existe en `public_html/`
2. El archivo `.htaccess` no tiene el contenido correcto
3. `mod_rewrite` no está habilitado en Hostinger
4. Los permisos del archivo son incorrectos

## ✅ Solución Paso a Paso

### Paso 1: Verificar que `.htaccess` existe

1. En **File Manager** de Hostinger, ve a `public_html/`
2. **Activa "Show Hidden Files"** (Mostrar archivos ocultos)
   - En File Manager, busca la opción "Settings" o "Configuración"
   - Activa "Show Hidden Files (dotfiles)"
3. Verifica que veas el archivo `.htaccess`
4. Si NO existe, súbelo desde `front/.htaccess`

### Paso 2: Verificar contenido del `.htaccess`

Abre el archivo `.htaccess` en Hostinger y verifica que tenga exactamente este contenido (versión simplificada):

```apache
RewriteEngine On
RewriteBase /

RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d

RewriteRule ^(.*)$ /index.html [L]
```

**IMPORTANTE**: Esta es la versión más simple y compatible. Si esta no funciona, el problema es que `mod_rewrite` no está habilitado en Hostinger.

### Paso 3: Verificar permisos

El archivo `.htaccess` debe tener permisos `644`:
- Click derecho en el archivo → "Change Permissions"
- Marca: `644` (Owner: Read+Write, Group: Read, Public: Read)

### Paso 4: Verificar que `index.html` existe

Asegúrate de que `public_html/index.html` existe y tiene el contenido correcto.

### Paso 5: Probar

1. Limpia la caché del navegador (Ctrl+Shift+Delete)
2. Visita: `https://centroprofesionaldocente.com/login`
3. Debería cargar correctamente

## 🆘 Si Sigue Sin Funcionar

### Opción A: Contactar a Hostinger

Contacta al soporte de Hostinger y pregunta:

1. ¿Está `mod_rewrite` habilitado en mi plan de hosting?
2. ¿Pueden verificar que mi archivo `.htaccess` esté funcionando?
3. ¿Hay alguna restricción que impida usar `.htaccess`?

### Opción B: Verificar en cPanel

1. En cPanel, busca "Apache Handlers" o "Apache Modules"
2. Verifica que `mod_rewrite` esté listado y habilitado

### Opción C: Usar subdirectorio (Alternativa)

Si `mod_rewrite` no está disponible, podemos configurar la app para que funcione desde un subdirectorio, pero esto requiere cambios en el código.

## 📝 Notas Importantes

- El archivo `.htaccess` es **sensible a mayúsculas/minúsculas**
- Debe llamarse exactamente `.htaccess` (con el punto al inicio)
- Debe estar en la raíz de `public_html/`
- No debe tener extensión (no `.htaccess.txt`)

## 🔄 Después de Corregir

Una vez que el `.htaccess` funcione:

1. Todas las rutas deberían funcionar: `/login`, `/panel`, `/verificar`, etc.
2. El React Router manejará las rutas correctamente
3. No deberías ver más errores 404
