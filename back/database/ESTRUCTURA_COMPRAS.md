# Estructura de Google Sheets - Compras

## Hoja: "compras"

Esta hoja debe tener las siguientes columnas (primera fila como headers):

| Columnas | Descripción | Requerido |
|----------|-------------|-----------|
| `nombres` | Nombres del cliente | ✅ Sí |
| `apellidos` | Apellidos del cliente | ✅ Sí |
| `dni` | DNI del cliente | ⚠️ Recomendado (para generar código único) |
| `curso` | Nombre del curso | ✅ Sí |
| `fecha_emision` | Fecha de emisión (YYYY-MM-DD) | ✅ Sí |
| `horas` | Horas del curso | ❌ Opcional |
| `codigo` | Código generado (se autocompleta) | ❌ Se genera automáticamente |
| `estado` | Estado (PENDIENTE, PROCESADO) | ❌ Se actualiza automáticamente |
| `fecha_procesado` | Fecha cuando se procesó | ❌ Se actualiza automáticamente |
| `mencion_id` | ID de la mención asignada | ❌ Opcional |

## Ejemplo de Datos

```
nombres | apellidos | dni      | curso                    | fecha_emision | horas | codigo | estado
--------|-----------|----------|--------------------------|---------------|-------|--------|--------
Juan    | Pérez     | 12345678 | Diplomado en Educación   | 2024-01-15    | 120   |        | PENDIENTE
María   | González  | 87654321 | Especialización Docente  | 2024-01-20    | 80    |        | PENDIENTE
```

## Flujo de Procesamiento

1. **Operador ve compras pendientes** → `GET /api/admin/compras/pendientes`
2. **Operador selecciona mención** → `GET /api/admin/menciones`
3. **Operador procesa compra** → `POST /api/admin/compras/{row_index}/procesar?mencion_id=1`
4. **Sistema:**
   - Genera código único (timestamp + DNI)
   - Actualiza Google Sheets con el código
   - Guarda en base de datos
   - Genera PDF con mención
   - Guarda PDF en almacenamiento
   - Retorna código y URL del certificado

## Notas

- El `row_index` es el índice en la lista de compras pendientes (0-based)
- El código se genera automáticamente usando timestamp + DNI
- Si no hay DNI, se usa solo timestamp
- El PDF incluye la mención seleccionada
