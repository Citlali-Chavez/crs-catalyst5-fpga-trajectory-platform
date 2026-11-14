# Host software

## Main application

The desktop application is provided in [`python/crs_catalyst5_gui.py`](python/crs_catalyst5_gui.py). It uses Tkinter for the graphical interface, Matplotlib for the 3D robot visualization, NumPy for numerical operations, and PySerial for serial communication. The optional webcam panel uses OpenCV and Pillow.

## Setup

1. Install Python 3.10 or later.
2. Install the packages listed in [`requirements.txt`](requirements.txt).
3. Connect the USB-to-TTL adapter and identify its serial port.
4. Review the `PUERTO` setting near the beginning of the script. The supplied source currently specifies `COM12`; change it to the port assigned by your operating system.
5. Run the application from a terminal:

   ```bash
   python python/crs_catalyst5_gui.py
   ```

The GUI labels and comments have been translated to English where practical. The underlying command strings and robot/controller protocol tokens are intentionally preserved.

## Important

This is the original research application, not a generic robot driver. It contains hardware-specific command sequences and timing assumptions. Do not connect it to a powered robot until the serial wiring, controller state, emergency-stop arrangements, joint limits, and laboratory procedure have been independently checked.
