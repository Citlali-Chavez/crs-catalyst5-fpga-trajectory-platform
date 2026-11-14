# Diseño de hardware digital

## Plataforma FPGA

- Familia: Intel Cyclone V GX.
- Número de parte indicado en la tesis: 5CGXFC5C6F27C7N.
- Lenguaje de descripción: Verilog.

## Arquitectura lógica

El diseño integra módulos UART de recepción y transmisión, una memoria FIFO y una máquina de estados. En conjunto, estos bloques permiten recibir datos, almacenarlos temporalmente y retransmitirlos hacia el controlador C500C.

## Interfaz eléctrica

La tesis reporta adaptación de niveles eléctricos mediante un circuito MAX3232 para la comunicación serial con el controlador. La velocidad nominal indicada es 57,600 baudios.

## Recursos reportados

La implementación identificada como BLOQUE_COMPLETO reporta 83 módulos lógicos adaptativos (ALM) y un bloque de memoria M10K.

## Archivos pendientes

Añadir aquí, cuando estén preparados para publicación:

- Código Verilog y módulos de nivel superior.
- Testbenches y resultados de simulación.
- Proyecto y restricciones de pines del FPGA.
- Reportes de síntesis y compilación.
- Esquemáticos de interfaz y documentación de conexiones.

No se incluyen archivos HDL ficticios en el scaffold.
