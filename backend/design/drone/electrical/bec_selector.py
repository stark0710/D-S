"""
BecSelector Subsystem

Purpose:
    Defines the `BecSelector` class responsible for sizing Battery Eliminator Circuit (BEC) voltage regulators.

Role in Architecture:
    `BecSelector` determines 5V / 9V / 12V voltage regulation channels and current output capacity in Amperes.
"""

from typing import Any


class BecSelector:
    """
    Selection service for BEC voltage regulation channels.

    Design Principles:
        - Single Responsibility Principle: Auxiliary voltage regulation sizing only.
    """

    def select_bec(
        self,
        avionics_power_w: float = 15.0,
        payload_power_w: float = 10.0
    ) -> dict[str, Any]:
        """
        Determines optimal BEC voltage regulator channels.

        Args:
            avionics_power_w (float): Avionics power draw in Watts.
            payload_power_w (float): Payload power draw in Watts.

        Returns:
            dict[str, Any]: Selected BEC specifications dictionary.
        """
        total_aux_w = avionics_power_w + payload_power_w

        # 5V rail current requirement
        current_5v_a = max(3.0, round((avionics_power_w / 5.0) * 1.5, 1))
        # 12V rail current requirement for payload/camera
        current_12v_a = max(2.0, round((payload_power_w / 12.0) * 1.5, 1))

        return {
            "bec_model": f"Dual-Output BEC (5V {current_5v_a:.1f}A / 12V {current_12v_a:.1f}A)",
            "output_5v_max_current_a": current_5v_a,
            "output_12v_max_current_a": current_12v_a,
            "efficiency_percent": 92.0,
            "weight_g": 12.0,
        }
