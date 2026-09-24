"""
EnergyAnalysis Subsystem

Purpose:
    Defines the `EnergyAnalysis` class and `EnergyAnalysisResult` dataclass for battery energy rates and reserve evaluation.

Role in Architecture:
    `EnergyAnalysis` calculates total energy in Wh, usable energy in Wh, hover/cruise energy rates (Wh/min), and energy reserve %.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class EnergyAnalysisResult:
    """
    Multirotor energy consumption evaluation output model.

    Attributes:
        total_battery_energy_wh (float): Total battery energy capacity in Watt-hours.
        usable_energy_wh (float): Usable battery energy capacity in Watt-hours (80% DOD limit).
        hover_energy_rate_wh_min (float): Hover energy consumption rate in Wh/min.
        cruise_energy_rate_wh_min (float): Cruise energy consumption rate in Wh/min.
        energy_reserve_percent (float): Energy reserve safety margin percentage.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    total_battery_energy_wh: float
    usable_energy_wh: float
    hover_energy_rate_wh_min: float
    cruise_energy_rate_wh_min: float
    energy_reserve_percent: float = 20.0
    metadata: dict[str, Any] = field(default_factory=dict)


class EnergyAnalysis:
    """
    Analysis service for battery energy rates and reserves.

    Design Principles:
        - Single Responsibility Principle: Energy capacity, energy consumption rates, and reserves analysis only.
    """

    def analyze_energy(
        self,
        capacity_mah: float,
        nominal_voltage_v: float,
        hover_power_w: float,
        cruise_power_w: float
    ) -> EnergyAnalysisResult:
        """
        Calculates energy capacity, rates, and reserves.

        Args:
            capacity_mah (float): Capacity in mAh.
            nominal_voltage_v (float): Voltage in V.
            hover_power_w (float): Hover power in W.
            cruise_power_w (float): Cruise power in W.

        Returns:
            EnergyAnalysisResult: Computed energy analysis output.
        """
        total_wh = (capacity_mah / 1000.0) * nominal_voltage_v
        usable_wh = total_wh * 0.80

        hover_rate = hover_power_w / 60.0
        cruise_rate = cruise_power_w / 60.0

        return EnergyAnalysisResult(
            total_battery_energy_wh=round(total_wh, 1),
            usable_energy_wh=round(usable_wh, 1),
            hover_energy_rate_wh_min=round(hover_rate, 2),
            cruise_energy_rate_wh_min=round(cruise_rate, 2),
            energy_reserve_percent=20.0
        )
