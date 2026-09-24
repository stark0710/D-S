"""
EfficiencyAnalysis Subsystem

Purpose:
    Defines the `EfficiencyAnalysis` class for electrical subsystem energy efficiency and flight endurance calculations.

Role in Architecture:
    `EfficiencyAnalysis` evaluates battery usable energy in Watt-hours, electrical transmission losses,
    and estimated hover/cruise flight endurance in minutes.
"""


class EfficiencyAnalysis:
    """
    Analysis service for electrical energy efficiency and flight endurance estimation.

    Design Principles:
        - Single Responsibility Principle: Electrical energy, usable capacity, and endurance estimation only.
    """

    def estimate_endurance_min(
        self,
        battery_capacity_mah: float,
        nominal_voltage_v: float,
        total_hover_power_w: float,
        usable_capacity_percent: float = 80.0
    ) -> float:
        """
        Estimates hover flight endurance in minutes.

        Args:
            battery_capacity_mah (float): Battery capacity in mAh.
            nominal_voltage_v (float): Nominal pack voltage in Volts.
            total_hover_power_w (float): Total hover power draw in Watts.
            usable_capacity_percent (float): Usable capacity percentage (80% default for LiPo life).

        Returns:
            float: Estimated flight time in minutes.
        """
        if total_hover_power_w <= 0:
            return 0.0

        # Total energy E = (Capacity Ah) * Voltage V
        total_energy_wh = (battery_capacity_mah / 1000.0) * nominal_voltage_v
        usable_energy_wh = total_energy_wh * (usable_capacity_percent / 100.0)

        flight_hours = usable_energy_wh / total_hover_power_w
        flight_minutes = flight_hours * 60.0

        return round(flight_minutes, 1)

    def calculate_electrical_losses(
        self,
        hover_current_a: float,
        wire_gauge_awg: int = 12,
        wire_length_cm: float = 30.0
    ) -> dict[str, float]:
        """
        Calculates I^2*R electrical wiring heat dissipation losses in Watts.

        Args:
            hover_current_a (float): Hover current in Amperes.
            wire_gauge_awg (int): Wiring AWG.
            wire_length_cm (float): Round-trip wire length in cm.

        Returns:
            dict[str, float]: Wiring loss dictionary.
        """
        awg_res_per_m = {8: 0.0021, 10: 0.0033, 12: 0.0052, 14: 0.0083, 16: 0.0132}
        r_per_m = awg_res_per_m.get(wire_gauge_awg, 0.0052)
        r_total = r_per_m * (wire_length_cm / 100.0)

        wire_loss_w = (hover_current_a ** 2) * r_total

        return {
            "wiring_resistance_ohms": round(r_total, 4),
            "wiring_power_loss_w": round(wire_loss_w, 2),
        }
