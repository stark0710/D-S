"""
EscSelector Subsystem

Purpose:
    Defines the `EscSelector` class responsible for sizing and selecting Electronic Speed Controller (ESC) specifications.

Role in Architecture:
    `EscSelector` determines continuous ESC current rating in Amperes, peak burst current rating,
    S-cell voltage support, protocol support (DShot600/DShot1200), and topology (4-in-1 vs Individual).
"""

from typing import Any


class EscSelector:
    """
    Selection service for multirotor Electronic Speed Controller (ESC) specifications.

    Design Principles:
        - Single Responsibility Principle: ESC current rating, voltage bounds, protocol, and form factor sizing only.
    """

    def select_escs(
        self,
        peak_current_per_motor_a: float,
        cell_count_s: int,
        rotor_count: int
    ) -> dict[str, Any]:
        """
        Determines optimal ESC specifications.

        Args:
            peak_current_per_motor_a (float): Peak motor current in Amperes.
            cell_count_s (int): Battery series cell count.
            rotor_count (int): Total rotor count.

        Returns:
            dict[str, Any]: Selected ESC specifications dictionary.
        """
        req_esc_current = peak_current_per_motor_a * 1.30  # 30% safety margin

        if req_esc_current > 80.0:
            rated_a = 120.0
            topology = "INDIVIDUAL_ESC"
            weight_g = 65.0 * rotor_count
        elif req_esc_current > 50.0:
            rated_a = 80.0
            topology = "4_IN_1_STACK" if rotor_count in (4, 8) else "INDIVIDUAL_ESC"
            weight_g = 45.0 * (2 if rotor_count == 8 else 1)
        elif req_esc_current > 35.0:
            rated_a = 50.0
            topology = "4_IN_1_STACK" if rotor_count in (4, 8) else "INDIVIDUAL_ESC"
            weight_g = 28.0 * (2 if rotor_count == 8 else 1)
        elif req_esc_current > 25.0:
            rated_a = 35.0
            topology = "4_IN_1_STACK" if rotor_count in (4, 8) else "INDIVIDUAL_ESC"
            weight_g = 18.0 * (2 if rotor_count == 8 else 1)
        else:
            rated_a = 30.0
            topology = "4_IN_1_STACK" if rotor_count in (4, 8) else "INDIVIDUAL_ESC"
            weight_g = 14.0

        burst_a = round(rated_a * 1.25, 0)

        return {
            "esc_model": f"{rated_a:.0f}A BLHeli_32 {topology}",
            "continuous_current_a": rated_a,
            "burst_current_a": burst_a,
            "max_supported_cells_s": max(6, cell_count_s),
            "protocol_support": "DShot600 / DShot1200",
            "topology": topology,
            "total_esc_weight_g": weight_g,
        }
