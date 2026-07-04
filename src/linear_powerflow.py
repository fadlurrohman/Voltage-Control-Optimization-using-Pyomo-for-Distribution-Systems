"""Linearized radial power-flow approximation.

For a line i -> j, voltage is approximated by:
    V_j = V_i - 2 * (r_ij * P_ij + x_ij * Q_ij)
where P_ij and Q_ij are downstream active and reactive flows.
This is a simplified DistFlow-style model suitable for optimization demos.
"""
from __future__ import annotations

from typing import Dict, Tuple

import pandas as pd

from .feeder import Feeder
from .network_utils import descendants_by_line, line_lookup, topological_order


def downstream_flows(
    feeder: Feeder,
    p_load: Dict[int, float],
    q_load: Dict[int, float],
    q_control: Dict[int, float] | None = None,
) -> Dict[Tuple[int, int], Tuple[float, float]]:
    q_control = q_control or {b: 0.0 for b in feeder.buses}
    descendants = descendants_by_line(feeder)
    flows: Dict[Tuple[int, int], Tuple[float, float]] = {}
    for line, buses in descendants.items():
        p_flow = sum(p_load[b] for b in buses)
        q_flow = sum(q_load[b] - q_control.get(b, 0.0) for b in buses)
        flows[line] = (p_flow, q_flow)
    return flows


def compute_voltage_profile(
    feeder: Feeder,
    p_load: Dict[int, float],
    q_load: Dict[int, float],
    q_control: Dict[int, float] | None = None,
    slack_vm_pu: float = 1.0,
) -> Dict[int, float]:
    flows = downstream_flows(feeder, p_load, q_load, q_control)
    line_params = line_lookup(feeder)
    order = topological_order(feeder)
    voltage = {feeder.slack_bus: slack_vm_pu}
    for bus in order:
        for i, j, _, _ in feeder.lines:
            if i == bus:
                r, x = line_params[(i, j)]
                p_flow, q_flow = flows[(i, j)]
                voltage[j] = voltage[i] - 2.0 * (r * p_flow + x * q_flow)
    return voltage


def voltage_violation_amount(v: float, v_min: float, v_max: float) -> float:
    if v < v_min:
        return v_min - v
    if v > v_max:
        return v - v_max
    return 0.0


def profile_to_dataframe(
    feeder: Feeder,
    scenario_id: int,
    voltage_before: Dict[int, float],
    voltage_after: Dict[int, float],
    q_control: Dict[int, float],
    v_min: float,
    v_max: float,
) -> pd.DataFrame:
    rows = []
    for bus in feeder.buses:
        before = voltage_before[bus]
        after = voltage_after[bus]
        rows.append({
            "scenario_id": scenario_id,
            "bus": bus,
            "vm_before_pu": before,
            "vm_after_pu": after,
            "q_control_pu": q_control.get(bus, 0.0),
            "violation_before_pu": voltage_violation_amount(before, v_min, v_max),
            "violation_after_pu": voltage_violation_amount(after, v_min, v_max),
            "is_violation_before": int(before < v_min or before > v_max),
            "is_violation_after": int(after < v_min or after > v_max),
        })
    return pd.DataFrame(rows)
