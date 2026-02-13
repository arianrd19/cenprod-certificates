# Conexión Remota a MySQL de Hostinger

## ⚠️ Importante: Hostinger y Conexiones Remotas

Hostinger **NO permite conexiones remotas a MySQL** por defecto por seguridad. Solo puedes conectarte desde:
- El mismo servidor (localhost)
- phpMyAdmin (interfaz web)

## Opciones para Desarrollo Local

### Opción 1: Usar Base de Datos Local (Recomendado para desarrollo)

Para desarrollo local, usa SQLite o MySQL local:

```env
# SQLite (más fácil para desarrollo)
DATABASE_URL=sqlite:///./cenprod_local.db

# O MySQL local si lo tienes instalado
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/cenprod_local
```

**Ventajas:**
- ✅ Funciona inmediatamente
- ✅ No depende de conexión a internet
- ✅ Más rápido para desarrollo
- ✅ Puedes migrar datos después

### Opción 2: Túnel SSH (Avanzado)

Si tienes acceso SSH a Hostinger, puedes crear un túnel:

```bash
ssh -L 3307:localhost:3306 usuario@honeydew-nightingale-926447.hostingersite.com
```

Luego en `.env`:
```env
DATABASE_URL=mysql+pymysql://u508077754_cenprod_user:ASD123$@127.0.0.1:3307/u508077754_cenprod_db
```

### Opción 3: Habilitar Acceso Remoto (No recomendado)

Hostinger generalmente no permite esto por seguridad. Si lo intentas:
1. Ve a cPanel → Remote MySQL
2. Agrega tu IP
3. Cambia el host en DATABASE_URL al dominio de Hostinger

**⚠️ No recomendado:** Menos seguro y puede no funcionar.

## Recomendación

**Para desarrollo local:** Usa SQLite o MySQL local
**Para producción:** Cuando subas a Hostinger, cambia a la conexión localhost

## Configuración Híbrida

El sistema está diseñado para funcionar así:
- **Sin DATABASE_URL configurado:** Usa Google Sheets
- **Con DATABASE_URL local:** Usa base de datos local
- **Con DATABASE_URL en servidor:** Usa MySQL de Hostinger
