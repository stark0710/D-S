"""
VoltageAnalysis Subsystem

Purpose:
    Defines the `VoltageAnalysis` class and `VoltageAnalysisResult` dataclass for electrical voltage level calculations.

Role in Architecture:
    `VoltageAnalysis` calculates nominal battery voltage, fully charged voltage, low voltage cutoff cutoff,
    and estimated main power cable voltage drop.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class VoltageAnalysisResult:
    """
    Multirotor electrical voltage analysis output model.

    Attributes:
        nominal_voltage_v (float): Nominal battery pack voltage in Volts (e.g. 22.2V for 6S).
        max_charged_voltage_v (float): Fully charged battery voltage in Volts (e.g. 25.2V for 6S LiPo).
        cutoff_voltage_v (float): Recommended low voltage cutoff point in Volts (e.g. 21.0V for 6S).
        estimated_voltage_drop_v (float): Estimated I*R voltage drop in main wiring under peak current.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    nominal_voltage_v: float
    max_charged_voltage_v: float
    cutoff_voltage_v: float
    estimated_voltage_drop_v: float
    metadata: dict[str, Any] = field(default_factory=dict)


class VoltageAnalysis:
    """
    Analysis service for multirotor electrical voltage levels.

    Design Principles:
        - Single Responsibility Principle: Voltage thresholds and wiring voltage drop calculations only.
    """

    def analyze_voltage(
        self,
        cell_count_s: int,
        peak_current_a: float,
        wire_gauge_awg: int = 12,
        wire_length_cm: float = 30.0,
        chemistry: str = "LiPo"
    ) -> VoltageAnalysisResult:
        """
        Calculates cell voltage thresholds and line voltage drop.

        Args:
            cell_count_s (int): Series cell count (e.g. 4S, 6S, 12S).
            peak_current_a (float): Peak current draw in Amperes.
            wire_gauge_awg (int): Wiring AWG (e.g. 12 AWG).
            wire_length_cm (float): Round-trip wiring length in cm.
            chemistry (str): Battery chemistry ('LiPo', 'LiHV', 'Li-Ion').

        Returns:
            VoltageAnalysisResult: Computed voltage analysis output.
        """
        if chemistry == "LiHV":
            cell_nom = 3.8
            cell_max = 4.35
            cell_cutoff = 3.5
        elif chemistry == "Li-Ion":
            cell_nom = 3.6
            cell_max = 4.2
            cell_cutoff = 3.0
        else:  # LiPo
            cell_nom = 3.7
            cell_max = 4.2
            cell_cutoff = 3.5

        nom_v = round(cell_count_s * cell_nom, 2)
        max_v = round(cell_count_s * cell_max, 2)
        cut_v = round(cell_count_s * cell_cutoff, 2)

        # Wire resistance estimate per meter in Ohms
        awg_res_per_m = {
            8: 0.0021,
            10: 0.0033,
            12: 0.0052,
            14: 0.0083,
            16: 0.0132
        }
        r_per_m = awg_res_per_m.get(wire_gauge_awg, 0.0052)
        r_total = r_per_m * (wire_length_cm / 100.0)
        v_drop = round(peak_current_a * r_total, 3)

        return VoltageAnalysisResult(
            nominal_voltage_v=nom_v,
            max_charged_voltage_v=max_v,
            cutoff_voltage_v=cut_v,
            estimated_voltage_drop_v=v_drop
        )
