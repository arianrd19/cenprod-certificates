# Backend - Sistema de Certificados con QR

Backend desarrollado con FastAPI para gestionar certificados con integración a Google Sheets.

## Configuración

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno:
- Copiar `.env.example` a `.env`
- Configurar `GOOGLE_SHEET_ID` con el ID de tu Google Sheet
- Configurar `GOOGLE_SERVICE_ACCOUNT_FILE` con la ruta al archivo JSON de service account
- Configurar `SECRET_KEY` (generar una clave secreta segura)
- Configurar `BASE_URL` con tu dominio

3. Preparar Google Sheets:
- Crear un Google Sheet con las siguientes columnas (primera fila como headers):
  - codigo
  - nombres
  - apellidos
  - dni
  - curso
  - fecha_emision
  - horas
  - estado
  - pdf_url
  - firma_url
  - logo_url
  - created_at
  - updated_at
  - motivo_anulacion

4. Ejecutar el servidor:
```bash
uvicorn app.main:app --reload --port 8000
```

## Endpoints

### Públicos
- `GET /api/public/certificados/{codigo}` - Obtener certificado por código
- `POST /api/public/buscar` - Buscar certificado
- `GET /api/public/certificados/{codigo}/pdf` - Descargar PDF

### Autenticación
- `POST /api/auth/login` - Login (form-data: username, password)

### Panel (requiere autenticación)
- `POST /api/admin/certificados` - Crear certificado
- `PUT /api/admin/certificados/{codigo}` - Actualizar certificado
- `POST /api/admin/certificados/{codigo}/anular` - Anular certificado
- `GET /api/admin/certificados` - Listar certificados
- `GET /api/admin/certificados/{codigo}/qr` - Descargar QR
- `GET /api/admin/users` - Listar usuarios (solo admin)
- `POST /api/auth/users` - Crear usuario (solo admin)
- `PUT /api/admin/users/{email}/activate` - Activar usuario (solo admin)
- `PUT /api/admin/users/{email}/deactivate` - Desactivar usuario (solo admin)
