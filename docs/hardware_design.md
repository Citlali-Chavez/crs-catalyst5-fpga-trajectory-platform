# Digital hardware design

## FPGA platform

- FPGA family: Intel Cyclone V GX.
- Device part number reported in the project: 5CGXFC5C6F27C7N.
- Hardware description language: Verilog.
- Original Quartus project files: [hardware/quartus/](../hardware/quartus/).

## Recovered Verilog source

The PDF code listings supplied with the project archive were used to recover the following source modules:

### UART receiver

Located in [hardware/verilog/uart_rx/](../hardware/verilog/uart_rx/):

- `BT_RX.v`: receiver timing pulse generator.
- `CONT_RX.v`: received-frame bit counter.
- `FSM_RX.v`: receiver state machine.
- `REG_RX.v`: serial shift register and byte output.
- `TOP_RX.v`: receiver subsystem interconnection.

### FIFO

Located in [hardware/verilog/fifo/](../hardware/verilog/fifo/):

- `FIFO_Buffer.v`: 256-entry, 8-bit-wide buffer with write/read pointers and empty/full flags.

### UART transmitter

Located in [hardware/verilog/uart_tx/](../hardware/verilog/uart_tx/):

- `BT_TX.v`: transmitter timing pulse generator.
- `MUX_TX.v`: start/data/stop/idle bit selection.
- `FSM_TX.v`: UART frame sequencing.
- `CONT_DIRECCIONES.v`: address counter for the transmit ROM.
- `ROM_TX.v`: stores the ASCII bytes for the string `boot\r`.
- `FSM_GENERAL_TX.v`: coordinates the multi-character transmission sequence.
- `BLOQUE_TX.v`: UART transmitter subsystem.
- `BLOQUE_TX_TOP.v`: top-level wrapper for the boot-string transmitter.

The recovered files preserve the original module names and signal identifiers. Spanish comments were translated where practical. The original PDF listings are retained under [hardware/source_documents/verilog/](../hardware/source_documents/verilog/).

## Important integration limitation

The supplied Quartus project file references a top-level entity named `BLOQUE_COMPLETO` and source paths outside the archived project. The supplied PDF listings do not include a complete `BLOQUE_COMPLETO.v` module. The recovered modules are therefore organized as source components, but the complete Quartus project is **not claimed to be immediately compilable**. The missing integrated top-level module and original project path assignments must be resolved from the author's working design.

The standalone `BLOQUE_TX_TOP` module transmits the literal ASCII command `boot\r`; it must not be mistaken for the full trajectory communication subsystem or for implementation of the C500C ACI mode.

## Electrical interface and serial settings

The platform documentation reports a MAX3232-based level-adaptation stage between the FPGA transmit channel and the C500C serial console. The nominal serial rate is 57,600 baud. Exact pin mapping, connector wiring, UART frame configuration, and electrical measurements should be confirmed against the original schematics and test records.

## Reported FPGA resources

The implementation report identifies:

- 83 adaptive logic modules (ALMs).
- One M10K memory block.

See [hardware/evidence/](../hardware/evidence/) for the supplied FPGA reports and pin-planner capture.
