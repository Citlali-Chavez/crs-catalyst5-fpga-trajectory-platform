# Project overview

## Purpose

This research develops and functionally evaluates a platform for managing joint-space trajectory execution on the five-degree-of-freedom CRS CataLyst-5 manipulator. The system integrates a Python application, a communication subsystem implemented on an Intel Cyclone V GX FPGA, and the robot's original C500C controller.

## Functional scope

The Python application loads a CSV file containing an ordered sequence of joint configurations, visualizes robot postures through a three-dimensional model based on forward kinematics, and coordinates sequential command transmission and execution.

The FPGA receives command data from the computer through a USB-to-TTL adapter, temporarily stores it in a FIFO, and retransmits it to the C500C through a MAX3232-based electrical interface. Responses from the C500C return directly to the computer through the MAX3232 and USB-to-TTL adapter; this response path does not pass through the FPGA.

## Included project artifacts

The repository contains the supplied Python application, example CSV files, recovered Verilog modules from PDF listings, Quartus project files, experimental images, and the available execution video. Some original project elements remain incomplete: the complete integrated FPGA top-level HDL file and the second execution video were not present as standalone files in the connected repository.

## What the platform does not claim

- It does not replace the original C500C controller.
- It does not implement a new robot motion-control law.
- It does not autonomously generate or plan trajectories.
- It does not, by itself, establish absolute positioning accuracy or mechanical repeatability.

The trajectory is generated externally and supplied as a CSV file. Each configuration contains five numerical joint values, q1–q5, expressed in radians.
