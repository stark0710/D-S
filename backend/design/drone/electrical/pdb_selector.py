"""
PdbSelector Subsystem

Purpose:
    Defines the `PdbSelector` class responsible for sizing Power Distribution Board (PDB) specifications.

Role in Architecture:
    `PdbSelector` determines continuous and burst current handling capacity of the PDB and telemetry current sensor rating.
"""

from typing import Any


class PdbSelector:
    """
    Selection service for multirotor Power Distribution Board (PDB) specifications.

    Design Principles:
        - Single Responsibility Principle: PDB current capacity and integration sizing only.
    """

    def select_pdb(
        self,
        peak_current_total_a: float,
        cell_count_s: int,
        esc_topology: str = "4_IN_1_STACK"
    ) -> dict[str, Any]:
        """
        Determines optimal PDB specifications.

        Args:
            peak_current_total_a (float): Peak total current draw in Amperes.
            cell_count_s (int): Cell count S.
            esc_topology (str): ESC topology.

        Returns:
            dict[str, Any]: Selected PDB specifications dictionary.
        """
        integrated = (esc_topology == "4_IN_1_STACK")

        req_a = peak_current_total_a * 1.25

        if req_a > 200.0:
            rated_a = 280.0
            weight_g = 85.0
        elif req_a > 120.0:
            rated_a = 180.0
            weight_g = 45.0
        else:
            rated_a = 120.0
            weight_g = 25.0

        return {
            "pdb_model": "Integrated 4-in-1 ESC PDB" if integrated else f"Heavy-Duty {rated_a:.0f}A PDB with Current Sensor",
            "continuous_current_rating_a": rated_a,
            "integrated_in_esc": integrated,
            "current_sensor_rating_a": rated_a * 1.1,
            "weight_g": 0.0 if integrated else weight_g,
        }
