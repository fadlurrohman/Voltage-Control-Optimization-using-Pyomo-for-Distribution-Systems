"""Plot voltage-control optimization results."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_worst_scenario(bus_profiles_csv: str, output_path: str) -> None:
    df = pd.read_csv(bus_profiles_csv)
    scenario_scores = df.groupby("scenario_id")["violation_before_pu"].sum()
    worst_sid = int(scenario_scores.idxmax())
    w = df[df["scenario_id"] == worst_sid].sort_values("bus")

    plt.figure(figsize=(9, 5))
    plt.plot(w["bus"], w["vm_before_pu"], marker="o", label="Before control")
    plt.plot(w["bus"], w["vm_after_pu"], marker="o", label="After optimization")
    plt.axhline(0.95, linestyle="--", label="Lower voltage limit")
    plt.axhline(1.05, linestyle="--", label="Upper voltage limit")
    plt.title(f"Voltage profile before and after control, scenario {worst_sid}")
    plt.xlabel("Bus")
    plt.ylabel("Voltage magnitude (p.u.)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Saved plot to {output_path}")


def plot_violation_comparison(summary_csv: str, output_path: str) -> None:
    df = pd.read_csv(summary_csv)
    means = {
        "Before control": df["violating_buses_before"].mean(),
        "After optimization": df["violating_buses_after"].mean(),
    }
    plt.figure(figsize=(6, 4))
    plt.bar(list(means.keys()), list(means.values()))
    plt.title("Average number of violating buses")
    plt.ylabel("Buses per scenario")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Saved plot to {output_path}")


def plot_case_comparison(comparison_csv: str, output_path: str) -> None:
    df = pd.read_csv(comparison_csv)
    x = range(len(df))
    width = 0.35
    plt.figure(figsize=(8, 5))
    plt.bar([i - width / 2 for i in x], df["mean_total_violation_before_pu"], width=width, label="Before")
    plt.bar([i + width / 2 for i in x], df["mean_total_violation_after_pu"], width=width, label="After")
    plt.xticks(list(x), df["feeder"].tolist())
    plt.title("Mean total voltage violation by feeder")
    plt.ylabel("Violation magnitude (p.u.)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Saved plot to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bus-profiles")
    parser.add_argument("--scenario-summary")
    parser.add_argument("--comparison-csv")
    parser.add_argument("--output", required=True)
    parser.add_argument("--plot-type", choices=["profile", "violations", "case_comparison"], required=True)
    args = parser.parse_args()
    if args.plot_type == "profile":
        if not args.bus_profiles:
            raise ValueError("--bus-profiles is required for profile plot")
        plot_worst_scenario(args.bus_profiles, args.output)
    elif args.plot_type == "violations":
        if not args.scenario_summary:
            raise ValueError("--scenario-summary is required for violations plot")
        plot_violation_comparison(args.scenario_summary, args.output)
    else:
        if not args.comparison_csv:
            raise ValueError("--comparison-csv is required for case_comparison plot")
        plot_case_comparison(args.comparison_csv, args.output)


if __name__ == "__main__":
    main()
