# Voltage Control Optimization using Pyomo for Distribution Systems

This project demonstrates a decision-making workflow for distribution-system operation. The goal is to reduce voltage-limit violations by optimizing reactive power injections at selected controllable buses.

The project is designed as a portfolio bridge between AI, optimization, and power systems. It complements a physics-aware GNN project by showing that the candidate can also formulate operational decision problems using mathematical optimization.

## Problem

Distribution networks can experience voltage violations under high load or variable operating conditions. This project formulates a linear voltage-control optimization model that determines reactive power control actions to keep bus voltages within a safe operating range.

## Method

The project uses a simplified radial feeder and a linearized DistFlow-style voltage approximation:

```text
V_j = V_i - 2 * (r_ij * P_ij + x_ij * Q_ij)
```

The optimization is built in Pyomo. For each operating scenario, the model chooses reactive power injections at controllable buses while minimizing:

1. voltage-limit violation slack,
2. voltage deviation from the target voltage,
3. control effort,
4. a simple feeder loss proxy.

## Main features

- Pyomo-based optimization model for voltage control.
- Synthetic operating scenarios generated from radial distribution feeders.
- Before-control and after-control voltage comparison.
- Voltage violation reduction metrics.
- Same-feeder and unseen-feeder evaluation.
- Plots for voltage profiles and violation reduction.

## Project structure

```text
voltage_control_optimization_pyomo_project/
├── configs/
│   └── default.yaml
├── data/
│   └── README.md
├── docs/
│   ├── cv_bullets.md
│   ├── motivation_letter_paragraph.md
│   └── project_summary.md
├── results/
│   └── README.md
├── scripts/
│   └── run_quickstart.sh
├── src/
│   ├── feeder.py
│   ├── linear_powerflow.py
│   ├── network_utils.py
│   ├── optimize_voltage.py
│   ├── scenario.py
│   ├── run_experiment.py
│   ├── compare_cases.py
│   └── plot_results.py
├── requirements.txt
└── README.md
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

If your terminal sometimes uses another Python environment, run commands with:

```bash
./.venv/bin/python
```

## Quickstart

```bash
./.venv/bin/python -m src.run_experiment --config configs/default.yaml --feeder radial_15 --output-prefix radial_15
```

Run an unseen topology case:

```bash
./.venv/bin/python -m src.run_experiment --config configs/default.yaml --feeder radial_9_unseen --output-prefix radial_9_unseen
```

Compare the two cases:

```bash
./.venv/bin/python -m src.compare_cases --metrics results/radial_15_metrics.json results/radial_9_unseen_metrics.json --output-csv results/voltage_control_comparison.csv --output-md results/voltage_control_comparison.md
```

Generate plots:

```bash
./.venv/bin/python -m src.plot_results --plot-type profile --bus-profiles results/radial_15_bus_profiles.csv --output results/radial_15_voltage_profile.png
```

```bash
./.venv/bin/python -m src.plot_results --plot-type violations --scenario-summary results/radial_15_scenario_summary.csv --output results/radial_15_violation_buses.png
```

```bash
./.venv/bin/python -m src.plot_results --plot-type case_comparison --comparison-csv results/voltage_control_comparison.csv --output results/voltage_control_case_comparison.png
```

Or run everything:

```bash
PYTHON_BIN=./.venv/bin/python ./scripts/run_quickstart.sh
```

## Outputs

The experiment generates:

- bus-level voltage profiles before and after control,
- scenario-level violation summaries,
- JSON and Markdown metrics,
- voltage profile plots,
- violation reduction plots,
- same-topology and unseen-topology comparison.

## How this supports PhD application

This project is directly related to distribution-system decision-making because it formulates an operational control action, solves it with mathematical optimization, and evaluates how much the decision reduces voltage violations. It shows practical familiarity with optimization for energy systems, Pyomo, and power-system constraints.
