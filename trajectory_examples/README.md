# Trajectory examples

This directory contains the five CSV trajectory files supplied with the original project archive. They are retained as input examples for the host application.

The files are named `trajectory_01.csv` through `trajectory_05.csv`. Some examples include a header row and some do not; inspect the selected file and the parser behavior before execution.

All rows are intended to represent five joint values in radians. The presence of an example file does not mean that its configurations have been validated as safe for physical execution. Check joint limits, controller conventions, and laboratory safety procedures before sending any trajectory to the robot.
