"""
Fixed-Wing Internal Combustion Engine Selector Subsystem

Purpose:
    Defines the `EngineSelector` class and engine records for gas propulsion sizing.

Role in Architecture:
    `EngineSelector` matches target horsepower or power requirements (Watts) to gasoline engines.
"""

from typing import List


class EngineRecord:
    """Internal Combustion Engine definition."""

    def __init__(self, name: str, displacement_cc: float, horsepower: float, weight_g: float) -> None:
        self.name = name
        self.displacement_cc = displacement_cc
        self.horsepower = horsepower
        self.weight_g = weight_g
        self.max_power_w = horsepower * 745.7  # convert HP to Watts


class EngineSelector:
    """
    Selector class matching target power requirements to gasoline engines.
    """

    _engines: List[EngineRecord] = [
        EngineRecord("O.S. GT15", 15.0, 2.4, 630),
        EngineRecord("DLE 20cc", 20.0, 2.5, 820),
        EngineRecord("Saito FG-21", 20.9, 2.1, 740),
        EngineRecord("DLE 35cc", 35.0, 4.1, 1150),
        EngineRecord("Saito FG-40", 40.2, 3.5, 1260),
        EngineRecord("DLE 55cc", 55.0, 5.5, 1560),
    ]

    def select_best_engine(self, target_power_w: float) -> EngineRecord:
        """
        Finds the smallest engine that can safely sustain the target power.
        """
        candidates = [e for e in self._engines if e.max_power_w >= target_power_w]
        if not candidates:
            return self._engines[-1]  # DLE 55cc fallback
        return min(candidates, key=lambda e: e.weight_g)
