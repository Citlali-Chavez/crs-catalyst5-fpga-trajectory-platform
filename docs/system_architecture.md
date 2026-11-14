# Arquitectura del sistema

## Bloques principales

### 1. Computadora anfitriona

La aplicación de usuario carga y organiza las configuraciones articulares, representa el manipulador en 3D mediante cinemática directa y administra la ejecución secuencial. Las respuestas del controlador llegan directamente a la computadora y participan en la coordinación del envío.

### 2. FPGA Intel Cyclone V GX

El diseño digital descrito en la tesis está escrito en Verilog e incluye:

- UART de recepción.
- UART de transmisión.
- Memoria FIFO para almacenamiento temporal.
- Máquina de estados finitos para coordinar el flujo de datos.

La FPGA funciona como interfaz de comunicación entre la computadora y el controlador; no reemplaza las funciones internas de control del C500C.

### 3. Adaptación eléctrica y controlador

La comunicación hacia el controlador emplea adaptación de niveles eléctricos mediante un circuito MAX3232. La velocidad serial nominal indicada en la tesis es de 57,600 baudios.

## Flujo de información

1. Se carga una secuencia de configuraciones articulares.
2. La aplicación procesa y conserva el orden de los puntos.
3. La computadora coordina el envío de datos hacia el sistema FPGA.
4. La FPGA recibe, almacena temporalmente y retransmite los datos al controlador C500C.
5. La computadora recibe las respuestas del controlador y coordina el avance de la secuencia.

Los detalles eléctricos, temporales y del protocolo deben verificarse contra los esquemas y el código originales antes de reproducir la implementación.
