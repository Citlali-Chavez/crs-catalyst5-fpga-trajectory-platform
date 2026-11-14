# CRS CataLyst-5 FPGA Trajectory Execution Platform

**A computer-based platform for loading, visualizing and executing joint-space trajectories on a five-degree-of-freedom CRS CataLyst-5 manipulator.**

[![Platform](https://img.shields.io/badge/robot-CRS%20CataLyst--5-informational)]()
[![FPGA](https://img.shields.io/badge/FPGA-Intel%20Cyclone%20V%20GX-blue)]()
[![HDL](https://img.shields.io/badge/HDL-Verilog-purple)]()
[![Software](https://img.shields.io/badge/software-Python-yellow)]()
[![Status](https://img.shields.io/badge/status-research%20prototype-lightgrey)]()

> This repository documents the research platform developed as part of a Master's thesis at the Instituto Nacional de Astrofísica, Óptica y Electrónica (INAOE). Source code, FPGA project files, videos and additional experimental artifacts will be added separately.

## Overview

The platform integrates three main elements:

1. **Python application:** loads TXT/CSV files containing ordered joint configurations, displays the manipulator through a three-dimensional model based on forward kinematics, and coordinates sequential trajectory execution.
2. **FPGA communication subsystem:** designed in Verilog and implemented on an Intel Cyclone V GX. It uses UART reception/transmission, FIFO storage and a finite-state machine to receive, temporarily store and retransmit data.
3. **CRS CataLyst-5 and original C500C controller:** the FPGA acts as a communication interface. The controller retains its internal motion-control functions.

The platform is intended to manage the execution of externally generated joint sequences. **It does not implement a new motion-control law or autonomous trajectory planner.**

## System architecture

```text
        TXT / CSV trajectory
                 |
                 v
       +---------------------+
       |  Python application |
       | load / validate     |
       | 3D forward kinematics|
       | execution sequence |
       +----------+----------+
                  |
             Serial link
                  |
                  v
       +---------------------+
       | Intel Cyclone V GX  |
       | UART RX / UART TX   |
       | FIFO memory         |
       | Finite-state machine|
       +----------+----------+
                  |
          MAX3232 level
             adaptation
                  |
                  v
       +---------------------+
       | CRS C500C controller|
       +----------+----------+
                  |
                  v
       +---------------------+
       | CRS CataLyst-5 robot|
       |       5 DOF         |
       +---------------------+

Controller responses are received by the computer and used to coordinate
the sequential transmission of trajectory points.
```

## Main technical characteristics

| Item | Description |
|---|---|
| Robot | CRS CataLyst-5, 5 degrees of freedom |
| Robot controller | Original CRS C500C |
| Host application | Python |
| GUI / visualization | Tkinter and Matplotlib, as described in the thesis |
| Serial software interface | PySerial |
| FPGA family | Intel Cyclone V GX |
| FPGA part | 5CGXFC5C6F27C7N |
| HDL | Verilog |
| FPGA communication blocks | UART RX, UART TX, FIFO and FSM |
| Nominal serial rate | 57,600 baud |
| Electrical adaptation | MAX3232 |
| Trajectory input | TXT and CSV |
| Joint variables | q1, q2, q3, q4, q5 |
| Input units | Radians |
| FPGA resource result | 83 ALMs and one M10K block |

## Experimental results reported in the thesis

- Ten returns to the MUESCAS (HOME) reference position were carried out from different joint configurations. The same integer pulse readings were obtained for the five joints, and physical alignment of the reference marks was visually observed.
- A trajectory consisting of twenty consecutive joint configurations was executed using sequential transmission and controller acknowledgements.
- The implementation was reported to use 83 adaptive logic modules (ALMs) and one M10K memory block.

These results support **functional integration and execution feasibility**. They should not be interpreted as an independent measurement of positioning accuracy or mechanical repeatability; the thesis identifies those measurements as future work.

## Repository structure

```text
.
├── README.md
├── CITATION.cff
├── CONTRIBUTING.md
├── docs/
│   ├── project_overview.md
│   ├── system_architecture.md
│   ├── software_design.md
│   ├── hardware_design.md
│   ├── trajectory_format.md
│   └── experimental_results.md
├── hardware/
├── software/
├── trajectory_examples/
├── media/
│   ├── architecture/
│   ├── hardware/
│   ├── simulation/
│   └── robot_execution/
└── results/
```

## Current repository contents

This initial repository package contains project documentation and directory placeholders. The original Python source, Verilog source, FPGA project files, trajectory datasets, photographs and videos are intentionally not fabricated or included. They can be added by the author after reviewing and preparing them for publication.

## Safety and scope

This repository is documentation for a research platform connected to an industrial robot. Do not connect, power, or command the manipulator based only on this documentation. Before any physical test, verify the robot/controller manuals, wiring, electrical levels, emergency-stop circuit, workspace clearance, joint limits, communication settings and supervision procedures. Use the robot only under appropriate laboratory safety procedures.

## Thesis information

**Title:** *Desarrollo de una plataforma para la ejecución de trayectorias de un robot articulado de 5 DOF implementado en FPGA*  
**Author:** Gloria Citlali Chávez Flores  
**Degree:** Maestría en Ciencias en la Especialidad de Electrónica  
**Institution:** Instituto Nacional de Astrofísica, Óptica y Electrónica (INAOE)  
**Location and date:** Santa María Tonantzintla, Puebla, November 2026  
**Supervisors:** Dr. Luis Hernández Martínez and Dr. Gerardo Ulises Díaz Arango

The thesis grants INAOE permission to reproduce and distribute copies of the thesis. That statement does **not** establish an open-source license for the software or HDL in this repository. No software license is assigned in this initial scaffold. A license should be added only after the author has confirmed the applicable rights and chosen the intended terms.

## Documentación en español

La documentación técnica complementaria se encuentra en [`docs/`](docs/). Este README está redactado principalmente en inglés para facilitar su consulta internacional; el proyecto y sus resultados se describen también en español en los documentos técnicos.

---
