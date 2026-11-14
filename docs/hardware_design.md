# Digital hardware design

## FPGA platform

- FPGA family: Intel Cyclone V GX.
- Device part number reported in the thesis: 5CGXFC5C6F27C7N.
- Hardware description language: Verilog.

## Digital architecture

The design integrates UART reception and transmission modules, a FIFO memory and a finite-state machine (FSM).

- **UART RX:** receives command data from the computer through the USB-to-TTL adapter.
- **FIFO:** temporarily stores the received data.
- **FSM:** coordinates the data transfer and transmission sequence.
- **UART TX:** transmits the command data toward the MAX3232-based electrical interface and the C500C controller.

The C500C response path returns to the computer through the MAX3232 and USB-to-TTL adapter. It does not pass through the FPGA.

## Electrical interface and serial settings

The thesis reports a MAX3232-based electrical level adaptation stage between the FPGA transmit channel and the C500C serial console interface. The nominal serial rate is 57,600 baud.

The exact pin mapping, connector wiring, UART frame configuration and electrical measurements should be documented from the original schematic and test records before hardware reproduction.

## Reported FPGA resources

The implementation identified as BLOQUE_COMPLETO reports:

- 83 adaptive logic modules (ALMs).
- One M10K memory block.

These values should be accompanied by the original synthesis report when it is added to the repository.

## Files to add when prepared for publication

- Verilog source files and top-level module.
- Testbenches and simulation results.
- FPGA project files and pin assignments.
- Synthesis and compilation reports.
- Electrical interface schematic and wiring documentation.

No HDL source files are fabricated or included in this documentation scaffold.
