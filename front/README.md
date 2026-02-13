# Frontend - Sistema de Certificados con QR

Frontend desarrollado con React y Vite para el sistema de certificados.

## Configuración

1. Instalar dependencias:
```bash
npm install
```

2. Ejecutar en desarrollo:
```bash
npm run dev
```

3. Construir para producción:
```bash
npm run build
```

## Estructura

- `/` - Página de inicio (redirige a /verificar)
- `/verificar` - Landing para buscar certificados
- `/certificado/:codigo` - Vista pública del certificado
- `/login` - Login para Admin/Operador
- `/panel` - Panel de administración (requiere autenticación)
  - `/panel` - Lista de certificados
  - `/panel/crear` - Crear nuevo certificado
  - `/panel/usuarios` - Gestión de usuarios (solo admin)

## Características

- Búsqueda de certificados por código
- Visualización de certificados
- Descarga de PDF
- Panel de administración con autenticación
- Gestión de usuarios (solo admin)
- Generación y descarga de códigos QR
- Responsive design
