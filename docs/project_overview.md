# Descripción general del proyecto

## Propósito

La investigación desarrolla y evalúa funcionalmente una plataforma para gestionar la ejecución de trayectorias articulares en el manipulador CRS CataLyst-5 de cinco grados de libertad. La solución integra una aplicación en Python, un subsistema de comunicación implementado en una FPGA Intel Cyclone V GX y el controlador original C500C del robot.

## Alcance funcional

La aplicación permite cargar secuencias articulares desde archivos TXT y CSV, visualizar posturas mediante un modelo tridimensional basado en cinemática directa y coordinar el envío secuencial de instrucciones al controlador.

El subsistema FPGA recibe datos, los almacena temporalmente mediante una FIFO y los retransmite al C500C. Las respuestas del controlador se reciben en la computadora y se utilizan para coordinar el envío de los puntos.

## Qué no pretende hacer

- No sustituye el controlador original C500C.
- No implementa una nueva ley de control del movimiento.
- No genera ni planifica automáticamente las trayectorias.
- No demuestra por sí sola la precisión absoluta ni la repetibilidad mecánica del robot.

Las trayectorias se consideran previamente generadas. Cada configuración está formada por cinco valores numéricos, correspondientes a q1–q5, expresados en radianes.
