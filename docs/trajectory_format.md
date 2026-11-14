# Formato de trayectorias articulares

La plataforma admite archivos TXT y CSV con secuencias de configuraciones articulares.

## Estructura de datos

Cada fila válida debe contener exactamente cinco valores numéricos:

`q1, q2, q3, q4, q5`

Los valores se interpretan en radianes y el orden de las filas se conserva para formar la secuencia discreta de puntos.

## Ejemplo ilustrativo

```csv
q1,q2,q3,q4,q5
0.0000,1.5708,0.0000,0.0000,0.0000
0.1000,1.5000,0.1000,0.0500,0.0000
0.2000,1.4000,0.2000,0.1000,0.1000
```

Este fragmento es únicamente ilustrativo y no debe enviarse al robot sin verificar límites articulares, convenciones, formato esperado por el software y condiciones de seguridad.

La tesis indica que las filas vacías o con dimensiones incorrectas se descartan durante el procesamiento. El cálculo y la planificación de la trayectoria se realizan externamente.
