# Sistema de Certificados con QR + Google Sheets

Sistema completo para gestión de certificados con integración a Google Sheets, generación de códigos QR y visualización/descarga de certificados.

## Estructura del Proyecto

```
Cert-qr/
├── back/          # Backend Python (FastAPI)
└── front/         # Frontend React (Vite)
```

## Características

### Roles y Permisos

- **Admin**: Gestiona usuarios, configura parámetros, ve todos los certificados
- **Operador**: Registra certificados, genera QR, previsualiza certificados
- **Cliente (Público)**: Verifica y visualiza certificados sin login

### Funcionalidades

1. **Búsqueda de Certificados**
   - Landing pública para buscar por código
   - Verificación de validez
   - Visualización de certificados anulados

2. **Gestión de Certificados**
   - Crear, editar y anular certificados
   - Generación de códigos QR
   - Descarga de PDF (dinámico o desde URL)

3. **Integración con Google Sheets**
   - Almacenamiento de datos en Google Sheets
   - Sin necesidad de base de datos tradicional
   - Sincronización en tiempo real

4. **Seguridad**
   - Autenticación JWT
   - Rate limiting
   - Roles y permisos

## Configuración Inicial

### Backend

1. Navegar a la carpeta `back/`
2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
   - Copiar `.env.example` a `.env`
   - Configurar `GOOGLE_SHEET_ID`
   - Configurar `GOOGLE_SERVICE_ACCOUNT_FILE` (ruta al JSON de service account)
   - Configurar `SECRET_KEY` (generar una clave segura)
   - Configurar `BASE_URL`

5. Preparar Google Sheets:
   - Crear un Google Sheet con las columnas requeridas (ver `back/README.md`)
   - Compartir el Sheet con el email del service account
   - Obtener el ID del Sheet de la URL

6. Ejecutar el servidor:
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend

1. Navegar a la carpeta `front/`
2. Instalar dependencias:
```bash
npm install
```

3. Ejecutar en desarrollo:
```bash
npm run dev
```

El frontend se ejecutará en `http://localhost:3000` y el backend en `http://localhost:8000`.

## URLs Públicas

- `/verificar` - Landing de búsqueda
- `/certificado/{codigo}` - Vista del certificado
- `/certificado/{codigo}` - Acceso directo por QR

## Panel de Administración

- `/login` - Iniciar sesión
- `/panel` - Panel principal
  - Lista de certificados
  - Crear certificado
  - Gestión de usuarios (solo admin)

## Credenciales por Defecto

Las credenciales por defecto del admin se configuran en el archivo `.env`:
- `ADMIN_EMAIL` (por defecto: admin@example.com)
- `ADMIN_PASSWORD` (por defecto: admin123)

**IMPORTANTE**: Cambiar estas credenciales en producción.

## Requisitos

- Python 3.8+
- Node.js 16+
- Google Cloud Service Account (para Google Sheets)
- Google Sheet configurado con las columnas requeridas

## Documentación Adicional

- Ver `back/README.md` para detalles del backend
- Ver `front/README.md` para detalles del frontend
