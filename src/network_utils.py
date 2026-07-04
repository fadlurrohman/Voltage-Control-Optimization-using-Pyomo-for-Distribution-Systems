"""Utility functions for radial feeders."""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Dict, Iterable, List, Set, Tuple

from .feeder import Feeder, Line


def children_map(feeder: Feeder) -> Dict[int, List[int]]:
    children = defaultdict(list)
    for parent, child, _, _ in feeder.lines:
        children[parent].append(child)
    return dict(children)


def parent_map(feeder: Feeder) -> Dict[int, int]:
    return {child: parent for parent, child, _, _ in feeder.lines}


def line_lookup(feeder: Feeder) -> Dict[Tuple[int, int], Tuple[float, float]]:
    return {(i, j): (r, x) for i, j, r, x in feeder.lines}


def topological_order(feeder: Feeder) -> List[int]:
    children = children_map(feeder)
    order: List[int] = []
    queue = deque([feeder.slack_bus])
    while queue:
        node = queue.popleft()
        order.append(node)
        for child in children.get(node, []):
            queue.append(child)
    return order


def descendants_by_line(feeder: Feeder) -> Dict[Tuple[int, int], Set[int]]:
    children = children_map(feeder)

    def descendants(root: int) -> Set[int]:
        out = {root}
        for c in children.get(root, []):
            out |= descendants(c)
        return out

    return {(i, j): descendants(j) for i, j, _, _ in feeder.lines}


def path_to_bus(feeder: Feeder, bus: int) -> List[Tuple[int, int]]:
    parents = parent_map(feeder)
    path: List[Tuple[int, int]] = []
    node = bus
    while node != feeder.slack_bus:
        p = parents[node]
        path.append((p, node))
        node = p
    return list(reversed(path))
