# Plantilla de Certificado

Coloca aquí el archivo `plantilla.png` que se usará como fondo para generar los certificados PDF.

## Ubicación del archivo

El archivo debe llamarse exactamente: **`plantilla.png`**

Y debe estar en esta carpeta: `back/plantillas/plantilla.png`

## Formato

- Formato: PNG
- Tamaño recomendado: A4 horizontal (landscape)
- Resolución: 300 DPI o superior para mejor calidad

## Uso

El sistema usará automáticamente esta plantilla al generar certificados PDF desde:
- `/api/public/certificados/{codigo}/pdf`
- Cualquier otro endpoint que genere PDFs de certificados
