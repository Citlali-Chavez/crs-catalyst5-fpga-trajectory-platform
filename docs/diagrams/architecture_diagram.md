# System architecture diagram

The two serial paths are distinct. Solid arrows show command transmission toward the controller; dashed arrows show the controller response returning directly to the computer.

```mermaid
flowchart LR
    CSV["CSV trajectory\n(q1, q2, q3, q4, q5)"] --> PC["Computer\nPython API + 3D visualization"]
    PC -->|"Command data"| USB["USB-to-TTL adapter"]
    USB -->|"TTL serial"| FPGA["Intel Cyclone V GX FPGA\nUART RX · FIFO · FSM · UART TX"]
    FPGA -->|"UART TX"| MAX["MAX3232 level adaptation"]
    MAX -->|"Serial console"| CTRL["Original CRS C500C controller"]
    CTRL -->|"Native motion control"| ROBOT["CRS CataLyst-5 robot\n5 DOF"]
    CTRL -.->|"Controller TX response"| MAX
    MAX -.->|"Level-adapted response"| USB
    USB -.->|"USB serial RX"| PC
```

**Forward path:** computer/Python → USB-to-TTL → FPGA → MAX3232 → C500C.

**Return path:** C500C → MAX3232 → USB-to-TTL → computer/Python. The response path bypasses the FPGA.
