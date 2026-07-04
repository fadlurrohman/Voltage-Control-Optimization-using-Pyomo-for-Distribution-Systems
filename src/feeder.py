"""Feeder definitions for radial distribution-network experiments.

The project uses simple radial feeders so the optimization remains transparent.
Each line is represented as: from_bus, to_bus, resistance_pu, reactance_pu.
The voltage model used later is a linearized DistFlow approximation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


Line = Tuple[int, int, float, float]


@dataclass(frozen=True)
class Feeder:
    name: str
    buses: List[int]
    slack_bus: int
    lines: List[Line]
    base_p_load: Dict[int, float]
    base_q_load: Dict[int, float]


def radial_15() -> Feeder:
    """A compact 15-bus radial feeder for the main experiment."""
    buses = list(range(15))
    slack = 0
    lines: List[Line] = [
        (0, 1, 0.012, 0.030),
        (1, 2, 0.014, 0.034),
        (2, 3, 0.010, 0.026),
        (3, 4, 0.018, 0.040),
        (2, 5, 0.013, 0.030),
        (5, 6, 0.014, 0.032),
        (6, 7, 0.018, 0.038),
        (7, 8, 0.015, 0.036),
        (1, 9, 0.016, 0.036),
        (9, 10, 0.012, 0.028),
        (10, 11, 0.018, 0.040),
        (11, 12, 0.016, 0.036),
        (3, 13, 0.013, 0.031),
        (13, 14, 0.017, 0.039),
    ]
    base_p = {bus: 0.0 for bus in buses}
    base_q = {bus: 0.0 for bus in buses}
    values = {
        1: (0.10, 0.05), 2: (0.12, 0.06), 3: (0.10, 0.05),
        4: (0.16, 0.08), 5: (0.09, 0.04), 6: (0.11, 0.05),
        7: (0.13, 0.06), 8: (0.15, 0.07), 9: (0.10, 0.05),
        10: (0.12, 0.06), 11: (0.14, 0.07), 12: (0.17, 0.08),
        13: (0.08, 0.04), 14: (0.15, 0.07),
    }
    for bus, (p, q) in values.items():
        base_p[bus] = p
        base_q[bus] = q
    return Feeder("radial_15", buses, slack, lines, base_p, base_q)


def radial_9_unseen() -> Feeder:
    """An unseen 9-bus feeder to test topology transfer of the optimization pipeline."""
    buses = list(range(9))
    slack = 0
    lines: List[Line] = [
        (0, 1, 0.015, 0.035),
        (1, 2, 0.020, 0.045),
        (2, 3, 0.014, 0.034),
        (3, 4, 0.018, 0.041),
        (1, 5, 0.017, 0.038),
        (5, 6, 0.020, 0.046),
        (2, 7, 0.016, 0.037),
        (7, 8, 0.019, 0.042),
    ]
    base_p = {bus: 0.0 for bus in buses}
    base_q = {bus: 0.0 for bus in buses}
    values = {
        1: (0.10, 0.05), 2: (0.15, 0.07), 3: (0.14, 0.07),
        4: (0.18, 0.09), 5: (0.12, 0.06), 6: (0.17, 0.08),
        7: (0.13, 0.06), 8: (0.19, 0.09),
    }
    for bus, (p, q) in values.items():
        base_p[bus] = p
        base_q[bus] = q
    return Feeder("radial_9_unseen", buses, slack, lines, base_p, base_q)


def get_feeder(name: str) -> Feeder:
    name = name.lower().strip()
    if name == "radial_15":
        return radial_15()
    if name in {"radial_9", "radial_9_unseen", "unseen"}:
        return radial_9_unseen()
    raise ValueError(f"Unknown feeder name: {name}")
