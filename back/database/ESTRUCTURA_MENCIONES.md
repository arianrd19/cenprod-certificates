# Estructura de Google Sheets - Menciones

## Hoja: "menciones"

Esta hoja debe tener las siguientes columnas (primera fila como headers):

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| `NRO` | Número de identificación de la mención | 1050 |
| `ESPECIALIDAD` | Tipo de especialidad | GENERALES |
| `P. CERTIFICADO` | Programa o tipo de certificado | CARGOS DIRECTIVOS 2025 I |
| `MENCIÓN` | Texto completo de la mención | ACTUALIZACIÓN DOCENTE EN FORTALECIMIENTO... |
| `HORAS` | Horas del programa | 350 |
| `F. INICIO` | Fecha de inicio | 24 de marzo |
| `F. TÉRMINO` | Fecha de término | 08 de julio del 2025 |
| `F. EMISIÓN` | Fecha de emisión | 11 de julio del 2025 |

## Ejemplo de Datos

```
NRO  | ESPECIALIDAD | P. CERTIFICADO          | MENCIÓN                                                      | HORAS | F. INICIO      | F. TÉRMINO            | F. EMISIÓN
-----|--------------|-------------------------|-------------------------------------------------------------|-------|----------------|----------------------|------------------
1050 | GENERALES    | CARGOS DIRECTIVOS 2025 I| ACTUALIZACIÓN DOCENTE EN FORTALECIMIENTO DE CONOCIMIENTOS... | 350   | 24 de marzo    | 08 de julio del 2025 | 11 de julio del 2025
```

## Uso en el Sistema

### Obtener Menciones

**Desde Google Sheets:**
```
GET /api/admin/menciones?source=sheets
```

**Desde Base de Datos:**
```
GET /api/admin/menciones?source=db
```

### Procesar Compra con Mención

```
POST /api/admin/compras/{row_index}/procesar?mencion_nro=1050
```

O usando ID de BD:
```
POST /api/admin/compras/{row_index}/procesar?mencion_id=1
```

## Flujo

1. **Operador ve compras pendientes** → `GET /api/admin/compras/pendientes`
2. **Operador ve menciones disponibles** → `GET /api/admin/menciones?source=sheets`
3. **Operador selecciona mención por NRO** → `POST /api/admin/compras/{row_index}/procesar?mencion_nro=1050`
4. **Sistema:**
   - Lee mención desde Google Sheets usando NRO
   - Genera código único
   - Actualiza Google Sheets (compra) con el código
   - Guarda en base de datos
   - Genera PDF con mención completa
   - Guarda PDF en almacenamiento
   - Si hay BD, crea registro de mención vinculado al certificado

## Notas

- El sistema prioriza Google Sheets para menciones
- Si se usa `mencion_nro`, busca en Google Sheets
- Si se usa `mencion_id`, busca en BD
- Las horas se toman de la mención si están disponibles, sino de la compra
- La mención completa se incluye en el PDF generado
