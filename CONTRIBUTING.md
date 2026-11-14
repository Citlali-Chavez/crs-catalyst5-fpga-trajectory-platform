# Contributing and project artifacts

This repository contains the research software, recovered HDL source, FPGA project files, trajectory examples, and experimental media associated with the CRS CataLyst-5 trajectory execution platform.

## Before modifying or adding files

- Confirm that you have the right to publish the material.
- Remove credentials, passwords, serial numbers, private network details, and unrelated personal data.
- Do not commit proprietary vendor software, manuals, or third-party material unless redistribution is permitted.
- Keep original experimental data intact; document any processing or conversion.
- Clearly label simulated, calculated, and physically measured results.
- Preserve the original robot/controller command strings and HDL interfaces unless a change is intentional and documented.

## Repository organization

- `software/`: Python desktop application and dependency instructions.
- `hardware/verilog/`: recovered Verilog modules.
- `hardware/quartus/`: Quartus project files.
- `hardware/source_documents/`: original PDF code listings used for HDL recovery.
- `trajectory_examples/`: CSV trajectory examples.
- `media/`: photographs, diagrams, screenshots, plots, and execution videos.
- `results/`: experimental evidence index and result summaries.

## Validation expectations

For HDL changes, identify the Quartus version, top-level entity, target device, and whether compilation and simulation were completed. For software changes, list the Python version and dependencies. Do not claim physical robot validation if only static review or simulation was performed.

## Safety

Changes involving physical robot commands must be reviewed under the laboratory's safety procedures. A software abort command is not a substitute for the robot's physical emergency stop.
