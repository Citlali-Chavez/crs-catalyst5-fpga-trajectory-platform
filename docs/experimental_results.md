# Evaluación experimental y resultados

La tesis reporta tres casos de estudio:

1. Operación nativa del manipulador mediante Teach Pendant y ROBCOMM3.
2. Diez ensayos de retorno a la posición MUESCAS (HOME) desde distintas configuraciones articulares.
3. Ejecución de una trayectoria compuesta por veinte configuraciones articulares consecutivas.

## Resultados reportados

- En los diez retornos a HOME se obtuvieron las mismas lecturas enteras de pulsos para las cinco articulaciones y se observó visualmente la alineación de las marcas físicas de referencia.
- La trayectoria de veinte puntos se ejecutó mediante transmisión secuencial de las configuraciones y recepción de respuestas de confirmación del controlador.
- El diseño digital reportó 83 ALMs y un bloque de memoria M10K.

## Interpretación y limitaciones

Los resultados respaldan la viabilidad funcional de la integración entre la aplicación, la FPGA y el controlador original. Sin embargo, la tesis señala que la precisión de posicionamiento y la repetibilidad mecánica requieren mediciones independientes adicionales.

Por tanto, los diez retornos no deben presentarse como una medición metrológica independiente de repetibilidad, ni las pruebas descritas como una caracterización completa de precisión.

## Evidencia

Los registros, fotografías, videos, reportes y datos originales podrán incorporarse en `results/` y `media/` una vez seleccionados y revisados por la autora.
