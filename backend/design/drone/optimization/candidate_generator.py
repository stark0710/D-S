"""
CandidateGenerator Subsystem

Purpose:
    Defines the `CandidateGenerator` class for generating alternative aircraft candidate designs in optimization space.

Role in Architecture:
    `CandidateGenerator` generates variations of design variables (frame wheelbase, motor KV, propeller diameter, battery capacity).
"""

from backend.design.drone.optimization.design_variables import DesignVariables


class CandidateGenerator:
    """
    Candidate generator service for optimization design variable exploration.

    Design Principles:
        - Single Responsibility Principle: Systematic design variable perturbation and candidate vector generation only.
    """

    def generate_candidates(self, base_variables: DesignVariables, max_candidates: int = 5) -> list[DesignVariables]:
        """
        Generates candidate design variable variations.

        Args:
            base_variables (DesignVariables): Baseline design variables vector.
            max_candidates (int): Maximum number of candidates to generate.

        Returns:
            list[DesignVariables]: Generated candidate vectors.
        """
        candidates: list[DesignVariables] = [base_variables]

        # Candidate 1: Larger battery for endurance (+30% capacity)
        candidates.append(
            DesignVariables(
                wheelbase_mm=base_variables.wheelbase_mm,
                motor_kv=base_variables.motor_kv,
                propeller_diameter_inch=base_variables.propeller_diameter_inch,
                battery_capacity_mah=round(base_variables.battery_capacity_mah * 1.30, 0),
                battery_cell_count_s=base_variables.battery_cell_count_s,
                esc_current_rating_a=base_variables.esc_current_rating_a,
                battery_offset_z_mm=base_variables.battery_offset_z_mm
            )
        )

        # Candidate 2: Larger propeller + lower KV motor for aerodynamic efficiency (+1.5" prop, -15% KV)
        candidates.append(
            DesignVariables(
                wheelbase_mm=round(base_variables.wheelbase_mm * 1.10, 0),
                motor_kv=max(200, int(base_variables.motor_kv * 0.85)),
                propeller_diameter_inch=base_variables.propeller_diameter_inch + 1.5,
                battery_capacity_mah=base_variables.battery_capacity_mah,
                battery_cell_count_s=base_variables.battery_cell_count_s,
                esc_current_rating_a=base_variables.esc_current_rating_a,
                battery_offset_z_mm=base_variables.battery_offset_z_mm
            )
        )

        # Candidate 3: High-voltage lower-capacity pack (8S / 12S step)
        candidates.append(
            DesignVariables(
                wheelbase_mm=base_variables.wheelbase_mm,
                motor_kv=max(180, int(base_variables.motor_kv * 0.70)),
                propeller_diameter_inch=base_variables.propeller_diameter_inch,
                battery_capacity_mah=round(base_variables.battery_capacity_mah * 0.80, 0),
                battery_cell_count_s=min(12, base_variables.battery_cell_count_s + 2),
                esc_current_rating_a=base_variables.esc_current_rating_a,
                battery_offset_z_mm=base_variables.battery_offset_z_mm
            )
        )

        return candidates[:max_candidates]
