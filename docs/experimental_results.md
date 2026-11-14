# Experimental evaluation and results

The thesis reports three study cases:

1. Native manipulator operation using the Teach Pendant and ROBCOMM3.
2. Ten return tests to the MUESCAS (HOME) position from different joint configurations.
3. Execution of a trajectory consisting of twenty consecutive joint configurations.

## Reported results

- In the ten returns to HOME, the same integer pulse readings were obtained for the five joints, and the physical reference marks were visually observed to be aligned.
- The twenty-point trajectory was executed through sequential transmission of the configurations and reception of controller acknowledgement responses.
- The digital design report lists 83 adaptive logic modules (ALMs) and one M10K memory block.

## Interpretation and limitations

These results support the functional feasibility of integrating the host application, FPGA communication interface, and original robot controller. However, the thesis indicates that positioning accuracy and mechanical repeatability require additional independent measurements.

Therefore, the ten return tests must not be presented as an independent metrological measurement of mechanical repeatability. Likewise, the reported tests do not constitute a complete characterization of positioning accuracy.

## Evidence available in this repository

- [Robot and system photographs](../media/images/)
- [Trajectory visualization and experimental captures](../media/images/)
- [Execution video: nine-point sequence](../media/robot_execution/nine_point_trajectory.mp4)
- [FPGA resource and implementation evidence](../hardware/evidence/)

The repository contains the available evidence files supplied with the project archive. The MUESCAS video was present in the supplied ZIP archive but is not currently present as a standalone file in the connected GitHub repository; it must be uploaded separately before it can be linked here.
