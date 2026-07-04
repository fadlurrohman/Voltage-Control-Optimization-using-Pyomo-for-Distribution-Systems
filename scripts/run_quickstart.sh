#!/usr/bin/env bash
set -e

PYTHON_BIN="${PYTHON_BIN:-python}"

$PYTHON_BIN -m src.run_experiment --config configs/default.yaml --feeder radial_15 --output-prefix radial_15
$PYTHON_BIN -m src.run_experiment --config configs/default.yaml --feeder radial_9_unseen --output-prefix radial_9_unseen
$PYTHON_BIN -m src.compare_cases --metrics results/radial_15_metrics.json results/radial_9_unseen_metrics.json --output-csv results/voltage_control_comparison.csv --output-md results/voltage_control_comparison.md
$PYTHON_BIN -m src.plot_results --plot-type profile --bus-profiles results/radial_15_bus_profiles.csv --output results/radial_15_voltage_profile.png
$PYTHON_BIN -m src.plot_results --plot-type violations --scenario-summary results/radial_15_scenario_summary.csv --output results/radial_15_violation_buses.png
$PYTHON_BIN -m src.plot_results --plot-type case_comparison --comparison-csv results/voltage_control_comparison.csv --output results/voltage_control_case_comparison.png
