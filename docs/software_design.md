# Host software design

## Main application

The desktop application is provided in [software/python/crs_catalyst5_gui.py](../software/python/crs_catalyst5_gui.py). It uses:

- **Tkinter** for the graphical user interface.
- **Matplotlib** for three-dimensional robot visualization.
- **NumPy** for numerical operations and forward-kinematics calculations.
- **PySerial** for serial communication with the USB-to-TTL adapter.
- **OpenCV and Pillow** for the optional webcam panel.

## Documented responsibilities

- Select and load an externally generated CSV trajectory.
- Read ordered joint configurations q1, q2, q3, q4, and q5.
- Interpret joint values in radians.
- Preserve the order of trajectory points.
- Display robot configurations using forward kinematics.
- Coordinate sequential command transmission and physical execution.
- Receive controller responses directly through the computer-side serial adapter and use them to coordinate progression through the sequence.

## Relationship with the FPGA

The computer sends command data to the FPGA through the USB-to-TTL adapter. The FPGA receives the stream, stores data temporarily, and retransmits it toward the C500C through the MAX3232 interface.

The C500C responses return to the computer through the MAX3232 and USB-to-TTL adapter, bypassing the FPGA. The Python application coordinates the execution sequence using these responses.

## Configuration and dependencies

Install the dependencies listed in [software/requirements.txt](../software/requirements.txt). The source currently specifies `COM12` as its serial port; change this value to the port assigned by the host operating system before running the application.

## Scope and validation

Trajectory generation and planning are external to the platform. The host application loads, validates, organizes, and visualizes the trajectory and manages its sequential execution.

The source is provided as the supplied research implementation. It has not been generalized or validated for arbitrary robot controllers, serial adapters, or operating systems.
