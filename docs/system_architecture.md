# System architecture

## System elements

### 1. Host computer and Python application

The host application loads the externally generated CSV trajectory, organizes its ordered joint configurations, displays the manipulator in 3D using forward kinematics, and coordinates sequential execution. It also receives the controller's responses directly through the USB-to-TTL serial adapter.

The Python application coordinates the trajectory visualization and the physical execution sequence. It does not replace the controller's internal motion-control functions.

### 2. USB-to-TTL serial adapter

The adapter provides the serial connection between the computer and the FPGA for command transmission. It also provides the computer-side receive path for responses coming back from the C500C through the MAX3232. Thus, the adapter participates in both directions, but the two paths terminate at different devices.

### 3. Intel Cyclone V GX FPGA

The digital design is described in Verilog and includes:

- UART receiver (RX), which receives command data from the computer-side USB-to-TTL adapter.
- FIFO memory for temporary data storage.
- Finite-state machine (FSM) to coordinate the data flow.
- UART transmitter (TX), which sends the stored command data toward the C500C.

The FPGA acts as a communication interface. It does not replace the C500C motion controller. The C500C response path does **not** pass through the FPGA.

### 4. MAX3232 electrical interface and C500C

A MAX3232-based level adaptation stage interfaces the FPGA transmit channel with the serial console connection of the original CRS C500C controller. The nominal serial communication rate reported for the platform is 57,600 baud.

The C500C retains the robot's internal motion-control functions and drives the CRS CataLyst-5 manipulator.

## Information paths

### Forward command path

1. The Python application loads and organizes the CSV trajectory.
2. The computer sends command data through its USB-to-TTL serial adapter.
3. The FPGA UART RX receives the data.
4. The FIFO stores data temporarily; the FSM coordinates the transfer.
5. The FPGA UART TX sends the data through the MAX3232 interface to the C500C.
6. The C500C processes the commands using its native controller functions and drives the robot.

### Return response path

1. The C500C transmits its response through its serial TX connection.
2. The MAX3232 adapts the electrical levels.
3. The response reaches the RX channel of the USB-to-TTL adapter.
4. The computer receives the response through the serial interface.
5. The Python application uses the response to coordinate progression through the trajectory.

**Important:** the return response path is C500C → MAX3232 → USB-to-TTL → computer. It bypasses the FPGA.

## Architecture diagram

The rendered diagram is available in [architecture_diagram.md](diagrams/architecture_diagram.md). The editable TikZ source is available in [architecture_diagram.tex](diagrams/architecture_diagram.tex).

## Implementation details to document with primary evidence

Electrical pin assignments, connector wiring, UART timing, command/response framing, FIFO depth, FSM states and controller protocol details should be confirmed against the original schematics, HDL source and experimental records before attempting to reproduce the hardware.
