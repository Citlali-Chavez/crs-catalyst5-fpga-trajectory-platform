# Contributing and adding project artifacts

This repository is initially a thesis documentation scaffold. The author will add the original software, HDL, FPGA project and media.

## Before adding files

- Confirm that you have the right to publish the material.
- Remove credentials, passwords, serial numbers, private network details and unrelated personal data.
- Do not commit proprietary vendor software, manuals or third-party material unless redistribution is permitted.
- Keep original experimental data intact; document any processing or conversion.
- Clearly label simulated, calculated and physically measured results.

## Suggested locations

- `software/`: Python application and its dependency instructions.
- `hardware/`: Verilog modules, testbenches and FPGA project files.
- `trajectory_examples/`: example TXT/CSV input files that are cleared for redistribution.
- `media/`: photographs, block diagrams, simulation captures and execution videos.
- `results/`: synthesis reports, test logs and experimental records.

## Pull requests

For contributions, describe the change, the files affected, the validation performed and whether the result was tested in simulation or on the physical robot. Do not claim physical validation if only simulation was performed.
