# Checklist de Verificación - Frontend en Hostinger

## ✅ Verificación Rápida

### 1. Archivos en `public_html/`

Verifica que tengas estos archivos en la raíz de `public_html/`:

```
public_html/
├── .htaccess          ← OBLIGATORIO (archivo oculto, empieza con punto)
├── index.html         ← OBLIGATORIO
├── assets/            ← OBLIGATORIO (carpeta con JS, CSS, imágenes)
│   ├── index-*.js
│   ├── index-*.css
│   └── logo-*.png
└── uploads/           ← Crear esta carpeta
    └── certificados/  ← Crear esta carpeta
```

### 2. Verificar que `.htaccess` existe

**En File Manager de Hostinger:**
1. Ve a `public_html/`
2. Activa "Show Hidden Files" (Mostrar archivos ocultos)
3. Deberías ver `.htaccess`
4. Si no existe, súbelo manualmente

### 3. Verificar permisos

- `.htaccess`: `644`
- `index.html`: `644`
- `assets/` (carpeta): `755`
- Archivos en `assets/`: `644`

### 4. Verificar contenido de `.htaccess`

Abre el archivo `.htaccess` en Hostinger y verifica que tenga este contenido:

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteCond %{REQUEST_FILENAME} !-l
  RewriteRule . /index.html [L]
</IfModule>
```

### 5. Probar URLs

Visita estas URLs y verifica que funcionen (no deben dar 404):

- ✅ `https://centroprofesionaldocente.com/` → Debe mostrar la página de verificación
- ✅ `https://centroprofesionaldocente.com/verificar` → Debe mostrar la página de verificación
- ✅ `https://centroprofesionaldocente.com/login` → Debe mostrar el login
- ✅ `https://centroprofesionaldocente.com/panel` → Debe redirigir a login si no estás autenticado

### 6. Verificar en consola del navegador

1. Abre `https://centroprofesionaldocente.com/login`
2. Presiona F12 para abrir DevTools
3. Ve a la pestaña "Console"
4. Verifica que NO haya errores 404 para archivos JS/CSS
5. Ve a la pestaña "Network"
6. Recarga la página
7. Verifica que los archivos en `assets/` se carguen correctamente (status 200)

## 🐛 Problemas Comunes

### Error 404 en todas las rutas

**Causa**: El archivo `.htaccess` no existe o no está funcionando

**Solución**:
1. Verifica que `.htaccess` esté en `public_html/`
2. Verifica que tenga el contenido correcto
3. Verifica permisos (644)
4. Contacta a Hostinger para verificar que `mod_rewrite` esté habilitado

### Error 404 solo en assets (JS, CSS)

**Causa**: Los archivos no se subieron correctamente o la ruta está mal

**Solución**:
1. Verifica que la carpeta `assets/` esté en `public_html/assets/`
2. Verifica que los archivos tengan los nombres correctos (con hash)
3. Verifica permisos de la carpeta (755)

### La página carga pero no se conecta al backend

**Causa**: La URL del backend no está configurada correctamente

**Solución**:
1. Abre la consola del navegador (F12)
2. Ve a "Network"
3. Intenta hacer login
4. Verifica que las peticiones vayan a `https://cenprod-backend.onrender.com/api/...`
5. Si no, reconstruye el frontend con `npm run build` después de verificar `.env.production`

## 📞 Contactar Soporte de Hostinger

Si después de verificar todo sigue sin funcionar, contacta a Hostinger y pregunta:

1. ¿Está `mod_rewrite` habilitado en mi hosting?
2. ¿Pueden verificar que mi `.htaccess` esté funcionando?
3. ¿Hay alguna restricción en mi plan de hosting que impida usar `.htaccess`?
