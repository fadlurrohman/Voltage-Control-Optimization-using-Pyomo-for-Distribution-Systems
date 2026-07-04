"""Scenario generation for voltage-control experiments."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd

from .feeder import Feeder


@dataclass
class Scenario:
    scenario_id: int
    p_load: Dict[int, float]
    q_load: Dict[int, float]


def generate_scenarios(
    feeder: Feeder,
    num_scenarios: int,
    seed: int,
    p_scale_min: float,
    p_scale_max: float,
    q_scale_min: float,
    q_scale_max: float,
) -> List[Scenario]:
    rng = np.random.default_rng(seed)
    scenarios: List[Scenario] = []
    non_slack = [b for b in feeder.buses if b != feeder.slack_bus]

    for sid in range(num_scenarios):
        global_p = rng.uniform(p_scale_min, p_scale_max)
        global_q = rng.uniform(q_scale_min, q_scale_max)
        p_load: Dict[int, float] = {}
        q_load: Dict[int, float] = {}
        for bus in feeder.buses:
            local = rng.normal(1.0, 0.08) if bus in non_slack else 1.0
            local = float(np.clip(local, 0.80, 1.25))
            p_load[bus] = feeder.base_p_load[bus] * global_p * local
            q_load[bus] = feeder.base_q_load[bus] * global_q * local
        scenarios.append(Scenario(sid, p_load, q_load))
    return scenarios


def scenarios_to_dataframe(scenarios: List[Scenario]) -> pd.DataFrame:
    rows = []
    for sc in scenarios:
        for bus, p in sc.p_load.items():
            rows.append({
                "scenario_id": sc.scenario_id,
                "bus": bus,
                "p_load_pu": p,
                "q_load_pu": sc.q_load[bus],
            })
    return pd.DataFrame(rows)
