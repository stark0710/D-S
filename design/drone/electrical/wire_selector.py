"""
WireSelector Subsystem

Purpose:
    Defines the `WireSelector` class responsible for sizing main power lead and motor wiring AWG gauges.

Role in Architecture:
    `WireSelector` calculates required American Wire Gauge (AWG) size for main battery leads and ESC motor phase wires.
"""

from typing import Any


class WireSelector:
    """
    Selection service for electrical power wiring AWG gauges.

    Design Principles:
        - Single Responsibility Principle: Wire gauge AWG sizing based on ampacity and thermal limits only.
    """

    def select_wiring(
        self,
        peak_current_total_a: float,
        peak_current_per_motor_a: float
    ) -> dict[str, Any]:
        """
        Determines main battery lead AWG and motor wire AWG.

        Args:
            peak_current_total_a (float): Peak total current draw in Amperes.
            peak_current_per_motor_a (float): Peak motor current in Amperes.

        Returns:
            dict[str, Any]: Selected wiring specifications dictionary.
        """
        # Main lead AWG
        if peak_current_total_a > 180.0:
            main_awg = 8
        elif peak_current_total_a > 110.0:
            main_awg = 10
        elif peak_current_total_a > 60.0:
            main_awg = 12
        elif peak_current_total_a > 35.0:
            main_awg = 14
        else:
            main_awg = 16

        # Motor lead AWG
        if peak_current_per_motor_a > 50.0:
            motor_awg = 14
        elif peak_current_per_motor_a > 30.0:
            motor_awg = 16
        elif peak_current_per_motor_a > 18.0:
            motor_awg = 18
        else:
            motor_awg = 20

        return {
            "main_battery_wire_awg": main_awg,
            "motor_phase_wire_awg": motor_awg,
            "wire_material": "High-Flex Silicone Stranded Copper",
            "max_temp_rating_c": 200.0,
        }
