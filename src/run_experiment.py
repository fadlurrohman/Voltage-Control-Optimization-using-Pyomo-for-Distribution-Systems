"""Run voltage-control optimization experiments."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import yaml

from .feeder import get_feeder
from .linear_powerflow import compute_voltage_profile, profile_to_dataframe
from .optimize_voltage import solve_voltage_control
from .scenario import generate_scenarios, scenarios_to_dataframe


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_experiment(config_path: str, feeder_name: str | None, output_prefix: str) -> None:
    cfg = load_config(config_path)
    feeder = get_feeder(feeder_name or cfg["feeder_name"])
    out_dir = Path(cfg["output"]["results_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    Path("data").mkdir(parents=True, exist_ok=True)

    load_cfg = cfg["load"]
    scenarios = generate_scenarios(
        feeder=feeder,
        num_scenarios=int(cfg["num_scenarios"]),
        seed=int(cfg["seed"]),
        p_scale_min=float(load_cfg["active_scale_min"]),
        p_scale_max=float(load_cfg["active_scale_max"]),
        q_scale_min=float(load_cfg["reactive_scale_min"]),
        q_scale_max=float(load_cfg["reactive_scale_max"]),
    )
    scenarios_to_dataframe(scenarios).to_csv(f"data/{output_prefix}_scenarios.csv", index=False)

    v_cfg = cfg["voltage"]
    c_cfg = cfg["control"]
    o_cfg = cfg["objective"]
    solver_cfg = cfg.get("solver", {})

    profile_frames = []
    summary_rows = []

    for sc in scenarios:
        v_before = compute_voltage_profile(
            feeder,
            sc.p_load,
            sc.q_load,
            q_control={b: 0.0 for b in feeder.buses},
            slack_vm_pu=float(v_cfg["slack_vm_pu"]),
        )
        opt = solve_voltage_control(
            feeder=feeder,
            p_load=sc.p_load,
            q_load=sc.q_load,
            controllable_buses=list(c_cfg["controllable_buses"]),
            q_capability_pu=float(c_cfg["q_capability_pu"]),
            v_min_pu=float(v_cfg["v_min_pu"]),
            v_max_pu=float(v_cfg["v_max_pu"]),
            v_target_pu=float(v_cfg["v_target_pu"]),
            slack_vm_pu=float(v_cfg["slack_vm_pu"]),
            violation_weight=float(o_cfg["violation_weight"]),
            voltage_deviation_weight=float(o_cfg["voltage_deviation_weight"]),
            control_effort_weight=float(o_cfg["control_effort_weight"]),
            loss_proxy_weight=float(o_cfg["loss_proxy_weight"]),
            solver_preferred=str(solver_cfg.get("preferred", "appsi_highs")),
        )
        q_control = opt["q_control"]
        v_after = opt["voltage"]

        profile = profile_to_dataframe(
            feeder=feeder,
            scenario_id=sc.scenario_id,
            voltage_before=v_before,
            voltage_after=v_after,
            q_control=q_control,
            v_min=float(v_cfg["v_min_pu"]),
            v_max=float(v_cfg["v_max_pu"]),
        )
        profile["feeder"] = feeder.name
        profile_frames.append(profile)

        summary_rows.append({
            "scenario_id": sc.scenario_id,
            "feeder": feeder.name,
            "solver": opt["solver"],
            "termination_condition": opt["termination_condition"],
            "objective_value": opt["objective_value"],
            "violating_buses_before": int(profile["is_violation_before"].sum()),
            "violating_buses_after": int(profile["is_violation_after"].sum()),
            "total_violation_before_pu": float(profile["violation_before_pu"].sum()),
            "total_violation_after_pu": float(profile["violation_after_pu"].sum()),
            "min_voltage_before_pu": float(profile["vm_before_pu"].min()),
            "min_voltage_after_pu": float(profile["vm_after_pu"].min()),
            "max_abs_q_control_pu": float(profile["q_control_pu"].abs().max()),
            "total_abs_q_control_pu": float(profile["q_control_pu"].abs().sum()),
        })

    profiles = pd.concat(profile_frames, ignore_index=True)
    summary = pd.DataFrame(summary_rows)

    profiles_path = out_dir / f"{output_prefix}_bus_profiles.csv"
    summary_path = out_dir / f"{output_prefix}_scenario_summary.csv"
    metrics_path = out_dir / f"{output_prefix}_metrics.json"
    md_path = out_dir / f"{output_prefix}_metrics.md"

    profiles.to_csv(profiles_path, index=False)
    summary.to_csv(summary_path, index=False)

    metrics = {
        "feeder": feeder.name,
        "num_scenarios": len(scenarios),
        "num_buses": len(feeder.buses),
        "mean_violating_buses_before": float(summary["violating_buses_before"].mean()),
        "mean_violating_buses_after": float(summary["violating_buses_after"].mean()),
        "mean_total_violation_before_pu": float(summary["total_violation_before_pu"].mean()),
        "mean_total_violation_after_pu": float(summary["total_violation_after_pu"].mean()),
        "violation_reduction_percent": float(
            100.0
            * (summary["total_violation_before_pu"].sum() - summary["total_violation_after_pu"].sum())
            / max(summary["total_violation_before_pu"].sum(), 1e-12)
        ),
        "mean_min_voltage_before_pu": float(summary["min_voltage_before_pu"].mean()),
        "mean_min_voltage_after_pu": float(summary["min_voltage_after_pu"].mean()),
        "mean_total_abs_q_control_pu": float(summary["total_abs_q_control_pu"].mean()),
    }
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Voltage control metrics: {feeder.name}\n\n")
        for key, value in metrics.items():
            f.write(f"- {key}: {value}\n")

    print(json.dumps(metrics, indent=2))
    print(f"Saved bus profiles to {profiles_path}")
    print(f"Saved scenario summary to {summary_path}")
    print(f"Saved metrics to {metrics_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--feeder", default=None)
    parser.add_argument("--output-prefix", default="radial_15")
    args = parser.parse_args()
    run_experiment(args.config, args.feeder, args.output_prefix)


if __name__ == "__main__":
    main()
