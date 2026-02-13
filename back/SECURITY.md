# Guía de Seguridad

## Configuración Requerida para Producción

### Variables de Entorno Obligatorias

1. **SECRET_KEY**: Debe ser una cadena aleatoria fuerte (mínimo 32 caracteres)
   ```bash
   SECRET_KEY=tu_clave_secreta_muy_larga_y_aleatoria_aqui
   ```

2. **ADMIN_PASSWORD**: Contraseña segura para el usuario administrador por defecto
   ```bash
   ADMIN_PASSWORD=tu_contraseña_segura_aqui
   ```

3. **ENVIRONMENT**: Debe ser 'production' en producción
   ```bash
   ENVIRONMENT=production
   ```

### Variables de Entorno Recomendadas

- `BASE_URL`: URL base de la aplicación
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Tiempo de expiración de tokens (default: 30)
- `RATE_LIMIT_PER_MINUTE`: Límite de requests por minuto (default: 60)

## Medidas de Seguridad Implementadas

### 1. Headers de Seguridad HTTP
- `X-Content-Type-Options: nosniff` - Previene MIME sniffing
- `X-Frame-Options: DENY` - Previene clickjacking
- `X-XSS-Protection: 1; mode=block` - Protección XSS
- `Strict-Transport-Security` - Fuerza HTTPS
- `Referrer-Policy` - Controla información del referrer
- `Content-Security-Policy` - Política de seguridad de contenido

### 2. Validación de Archivos
- Validación de tipo MIME
- Validación de tamaño máximo (10MB para PDFs)
- Validación de contenido (verificación de header PDF)
- Sanitización de nombres de archivo (previene path traversal)

### 3. Manejo de Errores
- Los errores internos no exponen información sensible al usuario
- Los tracebacks solo se registran en logs del servidor
- Mensajes de error genéricos en producción

### 4. CORS
- Orígenes permitidos configurados explícitamente
- Métodos HTTP limitados a los necesarios
- Headers permitidos específicos

### 5. Autenticación y Autorización
- Tokens JWT con expiración
- Contraseñas hasheadas con bcrypt
- Protección de rutas por rol (admin/operador)
- Validación de tokens en cada request

### 6. Rate Limiting
- Límite de requests por minuto configurable
- Basado en dirección IP remota

## Recomendaciones Adicionales

1. **HTTPS**: Siempre usar HTTPS en producción
2. **Firewall**: Configurar firewall para limitar acceso
3. **Logs**: Revisar logs regularmente para detectar actividad sospechosa
4. **Backups**: Realizar backups regulares de Google Sheets
5. **Actualizaciones**: Mantener dependencias actualizadas
6. **Monitoreo**: Implementar monitoreo de seguridad

## Checklist de Despliegue

- [ ] SECRET_KEY configurado y seguro
- [ ] ADMIN_PASSWORD cambiado del valor por defecto
- [ ] ENVIRONMENT=production configurado
- [ ] HTTPS habilitado
- [ ] CORS configurado correctamente
- [ ] Rate limiting activo
- [ ] Logs configurados
- [ ] Backups configurados
- [ ] Firewall configurado
- [ ] Monitoreo activo
