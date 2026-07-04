"""Compare voltage-control metrics across feeder cases."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def compare(metrics_files: list[str], output_csv: str, output_md: str) -> None:
    rows = []
    for path in metrics_files:
        with open(path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        rows.append(metrics)
    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    cols = [
        "feeder",
        "num_scenarios",
        "mean_violating_buses_before",
        "mean_violating_buses_after",
        "mean_total_violation_before_pu",
        "mean_total_violation_after_pu",
        "violation_reduction_percent",
        "mean_min_voltage_before_pu",
        "mean_min_voltage_after_pu",
        "mean_total_abs_q_control_pu",
    ]
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# Voltage-control comparison\n\n")
        f.write(df[cols].to_markdown(index=False))
        f.write("\n")
    print(df[cols].to_string(index=False))
    print(f"Saved comparison CSV to {output_csv}")
    print(f"Saved comparison Markdown to {output_md}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", nargs="+", required=True)
    parser.add_argument("--output-csv", default="results/voltage_control_comparison.csv")
    parser.add_argument("--output-md", default="results/voltage_control_comparison.md")
    args = parser.parse_args()
    compare(args.metrics, args.output_csv, args.output_md)


if __name__ == "__main__":
    main()
