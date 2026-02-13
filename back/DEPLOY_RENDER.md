# Guía de Despliegue en Render

Esta guía te ayudará a desplegar el backend de FastAPI en Render.

## 📋 Prerequisitos

1. Cuenta en [Render.com](https://render.com) (gratis o pago)
2. Repositorio en GitHub/GitLab (recomendado) o código listo para subir
3. Archivo `service_account.json` de Google Cloud Platform
4. Variables de entorno preparadas

## 🚀 Paso 1: Preparar el Repositorio

### 1.1 Verificar archivos necesarios

Asegúrate de tener estos archivos en la raíz de `back/`:
- ✅ `Procfile` (ya creado)
- ✅ `runtime.txt` (ya creado)
- ✅ `requirements.txt` (ya existe)
- ✅ `app/main.py` (ya existe)

### 1.2 Subir a GitHub (Recomendado)

```bash
# Si aún no tienes repositorio
git init
git add .
git commit -m "Preparado para Render"
git branch -M main
git remote add origin https://github.com/tu-usuario/tu-repo.git
git push -u origin main
```

## 🔧 Paso 2: Crear Servicio en Render

### 2.1 Crear nuevo Web Service

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Click en **"New +"** → **"Web Service"**
3. Conecta tu repositorio de GitHub/GitLab
   - Si no está conectado, Render te pedirá autorización
   - Selecciona tu repositorio
   - Selecciona la rama `main` o `master`

### 2.2 Configuración del Servicio

**Configuración básica:**
- **Name**: `cenprod-backend` (o el nombre que prefieras)
- **Environment**: `Python 3`
- **Region**: Elige la más cercana a tus usuarios
- **Branch**: `main` (o la rama que uses)

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - ⚠️ Render detectará automáticamente el `Procfile`, pero puedes especificarlo aquí también

**Root Directory**: `back` (si tu repo tiene la carpeta `back/`)

## 🔐 Paso 3: Configurar Variables de Entorno

En Render, ve a la sección **"Environment"** y agrega estas variables:

### Variables Obligatorias

```env
ENVIRONMENT=production
BASE_URL=https://centroprofesionaldocente.com
SECRET_KEY=tu-secret-key-super-segura-aqui-genera-una-aleatoria
ADMIN_EMAIL=admin@centroprofesionaldocente.com
ADMIN_PASSWORD=tu-password-super-segura
```

### Variables de Google Sheets

```env
GOOGLE_SHEET_ID=15sZo9tyeF-hw0Pgd8YrDgJBNkUPXBF0u6BTEj8-p3Fw
GOOGLE_SHEET_MENCIONES_ID=1zaFo7ZJq0yAIjNwcTWJiCr3odCzs6ZYL_ibRE8yrkeM
```

### Service Account (Elige UNA opción)

**Opción A: Usar archivo JSON (Recomendado para Render)**

1. En Render, ve a **"Secrets"** (en el menú lateral)
2. Click en **"Create Secret"**
3. Nombre: `GOOGLE_SERVICE_ACCOUNT`
4. Valor: Pega el contenido COMPLETO del archivo `path/service_account.json`
   - ⚠️ Debe ser una sola línea, sin saltos de línea
   - Puedes usar un editor online para convertir JSON a una línea
5. En variables de entorno, agrega:
   ```env
   GOOGLE_SERVICE_ACCOUNT={"type":"service_account","project_id":"...","private_key_id":"...","private_key":"...","client_email":"...","client_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_x509_cert_url":"..."}
   ```

**Opción B: Usar variable de entorno estándar**

Si prefieres usar el archivo directamente:
1. Sube `service_account.json` a Render usando el sistema de archivos
2. Agrega la variable:
   ```env
   GOOGLE_SA_FILE=/etc/secrets/service_account.json
   ```

### Variables Opcionales (con valores por defecto)

```env
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SESSION_SECONDS=3600
RATE_LIMIT_PER_MINUTE=60
STORAGE_TYPE=local
STORAGE_PATH=uploads/certificados
BASE_STORAGE_URL=https://centroprofesionaldocente.com/uploads/certificados
```

## 📁 Paso 4: Subir service_account.json

### Método 1: Variable de Entorno (Más Fácil)

1. Abre `back/path/service_account.json` en tu editor
2. Copia TODO el contenido
3. Conviértelo a una sola línea (sin saltos de línea)
   - Puedes usar: https://jsonformatter.org/json-minify
4. En Render, agrega la variable de entorno:
   ```env
   GOOGLE_SERVICE_ACCOUNT={"type":"service_account",...}
   ```
   (Pega el JSON completo en una sola línea)

### Método 2: Secrets de Render

1. En Render Dashboard, ve a **"Secrets"**
2. Click en **"Create Secret"**
3. Nombre: `service_account_json`
4. Valor: Contenido completo del JSON (puede tener saltos de línea)
5. Luego, en variables de entorno, referencia el secret

## 🚀 Paso 5: Desplegar

1. Click en **"Create Web Service"**
2. Render comenzará a construir y desplegar tu aplicación
3. Verás los logs en tiempo real
4. Una vez completado, obtendrás una URL como: `https://cenprod-backend.onrender.com`

## ✅ Paso 6: Verificar el Despliegue

### 6.1 Verificar que el servicio está corriendo

Visita: `https://tu-backend.onrender.com/health`

Deberías ver:
```json
{"status": "ok"}
```

### 6.2 Verificar la raíz

Visita: `https://tu-backend.onrender.com/`

Deberías ver:
```json
{"message": "Sistema de Certificados API", "version": "1.0.0"}
```

### 6.3 Verificar que las variables están configuradas

Revisa los logs en Render. No deberías ver errores de:
- ❌ "SECRET_KEY debe estar configurado"
- ❌ "No se encontró configuración de Service Account"
- ❌ Errores de conexión a Google Sheets

## 🔧 Paso 7: Configurar Dominio Personalizado (Opcional)

1. En Render, ve a tu servicio
2. Click en **"Settings"**
3. Scroll hasta **"Custom Domain"**
4. Agrega: `api.centroprofesionaldocente.com` (o el subdominio que prefieras)
5. Render te dará instrucciones para configurar DNS

## 📝 Notas Importantes

### Sobre el Storage

- En Render, el storage local es **temporal** (se borra al reiniciar)
- Para producción, considera usar:
  - **AWS S3** (configura `STORAGE_TYPE=s3` y las variables de AWS)
  - **Google Cloud Storage**
  - **Subir PDFs directamente a Hostinger vía FTP/SFTP**

### Sobre los Logs

- Los logs están deshabilitados en producción
- Puedes ver logs en tiempo real en Render Dashboard
- Los errores se muestran en los logs de Render

### Sobre el Plan Gratuito

- Render Free tiene limitaciones:
  - El servicio se "duerme" después de 15 minutos de inactividad
  - El primer request después de dormir puede tardar ~30 segundos
  - Considera el plan Starter ($7/mes) para producción

## 🐛 Solución de Problemas

### Error: "SECRET_KEY debe estar configurado"
- ✅ Verifica que `ENVIRONMENT=production` esté configurado
- ✅ Verifica que `SECRET_KEY` tenga un valor diferente a `dev_key_change_this`

### Error: "No se encontró configuración de Service Account"
- ✅ Verifica que `GOOGLE_SERVICE_ACCOUNT` esté configurado (JSON completo en una línea)
- ✅ O verifica que `GOOGLE_SA_FILE` apunte a un archivo válido

### Error: "Module not found"
- ✅ Verifica que `requirements.txt` tenga todas las dependencias
- ✅ Revisa los logs de build en Render

### El servicio no inicia
- ✅ Verifica que el `Procfile` esté en la raíz de `back/`
- ✅ Verifica que `app/main.py` exista
- ✅ Revisa los logs de Render para ver el error específico

## 📞 Siguiente Paso

Una vez que el backend esté funcionando en Render:
1. Anota la URL de tu backend: `https://tu-backend.onrender.com`
2. Continúa con el despliegue del frontend en Hostinger
3. Actualiza la configuración del frontend para apuntar a esta URL
