# Joint-space trajectory format

The platform uses externally generated CSV files containing ordered sequences of joint configurations. In the thesis workflow, trajectories are generated in Maple and loaded by the Python application.

## Data structure

Each trajectory point contains five numerical values corresponding to the joint variables:

`q1,q2,q3,q4,q5`

The values are expressed in radians. The order of the rows is preserved and defines the sequence of configurations to be executed.

## Included examples

The [trajectory_examples/](../trajectory_examples/) directory contains the CSV files supplied with the project archive. They are retained as original examples and may differ in header presence and whitespace.

## Illustrative format

```csv
q1,q2,q3,q4,q5
0.0000,1.5708,0.0000,0.0000,0.0000
0.1000,1.5000,0.1000,0.0500,0.0000
0.2000,1.4000,0.2000,0.1000,0.1000
```

This example is illustrative only. It is not a validated trajectory for the physical manipulator and must not be sent to the robot without checking the controller's expected command format, joint limits, coordinate conventions, and laboratory safety conditions.

## Validation

The application source contains a parser for rows with five numerical values and handles invalid or empty rows. Consult the implementation before relying on assumptions about delimiters, headers, decimal notation, or error handling.

## Scope

The platform loads and executes an externally generated trajectory; it does not calculate or plan the trajectory itself.
