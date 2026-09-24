"""
Fixed-Wing Propeller Selector Subsystem

Purpose:
    Defines the `PropellerSelector` class and propeller geometry calculations.

Role in Architecture:
    `PropellerSelector` matches engine/motor shaft power and clearance bounds to standard propeller records.
"""

from typing import List, Tuple
import math


class PropellerRecord:
    """Propeller dimensional description."""

    def __init__(self, diameter_in: float, pitch_in: float) -> None:
        self.diameter_in = diameter_in
        self.pitch_in = pitch_in
        self.name = f"{int(diameter_in)}x{int(pitch_in)} APC"

    @property
    def diameter_m(self) -> float:
        return self.diameter_in * 0.0254

    @property
    def pitch_m(self) -> float:
        return self.pitch_in * 0.0254


class PropellerSelector:
    """
    Sizing service matching shaft power and thrust targets to propeller sizes.
    """

    _props: List[PropellerRecord] = [
        PropellerRecord(9.0, 6.0),
        PropellerRecord(10.0, 7.0),
        PropellerRecord(11.0, 7.0),
        PropellerRecord(12.0, 6.0),
        PropellerRecord(12.0, 8.0),
        PropellerRecord(13.0, 8.0),
        PropellerRecord(14.0, 10.0),
        PropellerRecord(15.0, 10.0),
        PropellerRecord(16.0, 8.0),
        PropellerRecord(18.0, 10.0),
        PropellerRecord(20.0, 10.0),
        PropellerRecord(22.0, 12.0),
    ]

    def select_propeller(
        self,
        target_thrust_n: float,
        shaft_power_w: float,
        air_density: float,
        max_diameter_m: float | None = None,
    ) -> PropellerRecord:
        """
        Selects a propeller using Actuator Disk Theory.
        """
        valid_props = [p for p in self._props if (max_diameter_m is None or p.diameter_m <= max_diameter_m)]
        if not valid_props:
            valid_props = [self._props[0]]

        best_prop = valid_props[-1]
        closest_diff = float("inf")

        for prop in valid_props:
            eta_static = 0.65
            area = (math.pi / 4.0) * (prop.diameter_m ** 2)
            est_thrust = (air_density * area * ((shaft_power_w * eta_static) ** 2)) ** (1.0 / 3.0)

            if est_thrust >= target_thrust_n:
                diff = est_thrust - target_thrust_n
                if diff < closest_diff:
                    closest_diff = diff
                    best_prop = prop

        return best_prop
