"""Pyomo model for voltage-control optimization."""
from __future__ import annotations

from typing import Dict, Iterable, List, Tuple


def solve_voltage_control(
    feeder,
    p_load: Dict[int, float],
    q_load: Dict[int, float],
    controllable_buses: List[int],
    q_capability_pu: float,
    v_min_pu: float,
    v_max_pu: float,
    v_target_pu: float,
    slack_vm_pu: float,
    violation_weight: float,
    voltage_deviation_weight: float,
    control_effort_weight: float,
    loss_proxy_weight: float,
    solver_preferred: str = "appsi_highs",
) -> Dict[str, object]:
    """Solve a linear voltage-control problem with Pyomo.

    Decision variables:
    - q_ctrl[bus]: reactive power injection at controllable buses.
    - v[bus]: approximate voltage magnitude.
    - low_slack/high_slack: voltage violation slacks.
    - dev_pos/dev_neg: absolute voltage deviation from target.
    - q_abs: absolute value of reactive control effort.

    Objective:
    minimize voltage violations + voltage deviation + control effort + loss proxy.
    """
    import pyomo.environ as pyo

    from .network_utils import descendants_by_line, line_lookup, topological_order

    buses = feeder.buses
    slack = feeder.slack_bus
    non_slack = [b for b in buses if b != slack]
    controllable = [b for b in controllable_buses if b in buses and b != slack]
    lines = [(i, j) for i, j, _, _ in feeder.lines]
    params = line_lookup(feeder)
    descendants = descendants_by_line(feeder)

    model = pyo.ConcreteModel("voltage_control_optimization")
    model.B = pyo.Set(initialize=buses)
    model.NS = pyo.Set(initialize=non_slack)
    model.C = pyo.Set(initialize=controllable)
    model.L = pyo.Set(dimen=2, initialize=lines)

    model.q_ctrl = pyo.Var(model.C, bounds=(-q_capability_pu, q_capability_pu))
    model.q_abs = pyo.Var(model.C, within=pyo.NonNegativeReals)
    model.v = pyo.Var(model.B)
    model.low_slack = pyo.Var(model.B, within=pyo.NonNegativeReals)
    model.high_slack = pyo.Var(model.B, within=pyo.NonNegativeReals)
    model.dev_pos = pyo.Var(model.B, within=pyo.NonNegativeReals)
    model.dev_neg = pyo.Var(model.B, within=pyo.NonNegativeReals)

    def qctrl_expr(bus):
        if bus in controllable:
            return model.q_ctrl[bus]
        return 0.0

    model.slack_voltage = pyo.Constraint(expr=model.v[slack] == slack_vm_pu)

    def voltage_drop_rule(m, i, j):
        r, x = params[(i, j)]
        down = descendants[(i, j)]
        p_flow = sum(p_load[b] for b in down)
        q_flow = sum(q_load[b] - qctrl_expr(b) for b in down)
        return m.v[j] == m.v[i] - 2.0 * (r * p_flow + x * q_flow)

    model.voltage_drop = pyo.Constraint(model.L, rule=voltage_drop_rule)

    def voltage_lower_rule(m, b):
        return m.v[b] + m.low_slack[b] >= v_min_pu

    def voltage_upper_rule(m, b):
        return m.v[b] - m.high_slack[b] <= v_max_pu

    model.v_lower = pyo.Constraint(model.B, rule=voltage_lower_rule)
    model.v_upper = pyo.Constraint(model.B, rule=voltage_upper_rule)

    def deviation_rule(m, b):
        return m.v[b] - v_target_pu == m.dev_pos[b] - m.dev_neg[b]

    model.voltage_deviation = pyo.Constraint(model.B, rule=deviation_rule)

    def abs_q_pos_rule(m, b):
        return m.q_abs[b] >= m.q_ctrl[b]

    def abs_q_neg_rule(m, b):
        return m.q_abs[b] >= -m.q_ctrl[b]

    model.abs_q_pos = pyo.Constraint(model.C, rule=abs_q_pos_rule)
    model.abs_q_neg = pyo.Constraint(model.C, rule=abs_q_neg_rule)

    # A simple linear loss proxy: penalize active downstream flow weighted by line resistance.
    # The active-flow component is constant for a scenario, but it keeps the objective form
    # interpretable and can be extended to controllable active power later.
    loss_proxy = sum(params[line][0] * sum(p_load[b] for b in descendants[line]) for line in lines)

    model.obj = pyo.Objective(
        expr=(
            violation_weight * sum(model.low_slack[b] + model.high_slack[b] for b in buses)
            + voltage_deviation_weight * sum(model.dev_pos[b] + model.dev_neg[b] for b in buses)
            + control_effort_weight * sum(model.q_abs[b] for b in controllable)
            + loss_proxy_weight * loss_proxy
        ),
        sense=pyo.minimize,
    )

    solver_candidates = [solver_preferred, "appsi_highs", "highs", "glpk"]
    solver = None
    solver_name = None
    for candidate in solver_candidates:
        try:
            opt = pyo.SolverFactory(candidate)
            if opt is not None and opt.available(exception_flag=False):
                solver = opt
                solver_name = candidate
                break
        except Exception:
            continue
    if solver is None:
        raise RuntimeError(
            "No Pyomo solver is available. Install highspy for appsi_highs, "
            "or install GLPK. Try: python -m pip install highspy"
        )

    result = solver.solve(model)
    q_control = {b: 0.0 for b in buses}
    for b in controllable:
        q_control[b] = float(pyo.value(model.q_ctrl[b]))

    voltage = {b: float(pyo.value(model.v[b])) for b in buses}
    slacks = {
        b: float(pyo.value(model.low_slack[b]) + pyo.value(model.high_slack[b]))
        for b in buses
    }
    return {
        "solver": solver_name,
        "termination_condition": str(result.solver.termination_condition),
        "objective_value": float(pyo.value(model.obj)),
        "q_control": q_control,
        "voltage": voltage,
        "violation_slack": slacks,
    }
