# Software design

## Host application

The thesis describes a Python application that provides a graphical interface, three-dimensional robot visualization and serial communication. The documented technologies are:

- **Tkinter:** graphical user interface.
- **Matplotlib:** three-dimensional visualization.
- **PySerial:** serial communication with the USB-to-TTL adapter.

## Documented responsibilities

- Select and load the CSV trajectory file generated externally.
- Read ordered joint configurations q1, q2, q3, q4 and q5.
- Validate that each accepted configuration contains five numerical values.
- Interpret joint values in radians.
- Preserve the order of the trajectory points.
- Display robot configurations using forward kinematics.
- Coordinate sequential command transmission and physical execution.
- Receive controller responses directly through the computer-side serial adapter and use them to coordinate progression through the sequence.

## Relationship with the FPGA

The computer sends command data to the FPGA through the USB-to-TTL adapter. The FPGA processes the incoming stream and retransmits it to the C500C through the MAX3232 interface.

The controller's responses return to the computer through the MAX3232 and USB-to-TTL adapter, bypassing the FPGA. The Python application coordinates the execution sequence using these responses.

## Scope

Trajectory generation and planning are external to the platform. The host application loads, validates, organizes and visualizes the trajectory and manages its sequential execution.

## Source code

The original Python source code is not included in this repository yet. Add it after reviewing dependencies, local paths, credentials and publication rights. Include a dependency file (for example, `requirements.txt`) and instructions for configuring the serial port when the source is added.
