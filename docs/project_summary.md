# One-page project summary

## Title
Voltage Control Optimization using Pyomo for Distribution Systems

## Objective
The objective of this project is to build a simple decision-making model for distribution-system operation. The model determines reactive power control actions that reduce voltage violations in a radial distribution network.

## Method
The project uses a linearized radial power-flow model and formulates the control problem as a linear optimization problem in Pyomo. For each load scenario, the model chooses reactive power injections at selected controllable buses. The objective minimizes voltage-violation slacks, voltage deviation from the target value, control effort, and a simple loss proxy.

## Evaluation
The model compares voltage profiles before and after optimization. Evaluation metrics include the number of violating buses, total voltage violation magnitude, minimum voltage before and after control, and total reactive control effort.

