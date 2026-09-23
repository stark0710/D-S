"""
PropellerSelector Subsystem

Purpose:
    Defines the `PropellerSelector` class responsible for sizing and selecting propeller engineering specifications.

Role in Architecture:
    `PropellerSelector` determines propeller diameter in inches, pitch in inches, blade count,
    material, and weight estimate matching the motor stator class and frame clearance.
"""

from typing import Any


class PropellerSelector:
    """
    Selection service for multirotor propeller engineering specifications.

    Design Principles:
        - Single Responsibility Principle: Propeller diameter, pitch, and blade count sizing only.
    """

    def select_propeller(
        self,
        motor_spec: dict[str, Any],
        max_allowed_diameter_inch: float = 18.0
    ) -> dict[str, Any]:
        """
        Determines optimal propeller engineering parameters.

        Args:
            motor_spec (dict[str, Any]): Selected motor specifications dictionary.
            max_allowed_diameter_inch (float): Max propeller diameter allowed by frame clearance.

        Returns:
            dict[str, Any]: Selected propeller specifications dictionary.
        """
        stator = motor_spec.get("stator_size", "2806")

        if stator == "8318":
            diameter = 28.0
            pitch = 9.2
            weight_g = 110.0
        elif stator == "5010":
            diameter = 18.0
            pitch = 6.0
            weight_g = 45.0
        elif stator == "3510":
            diameter = 13.0
            pitch = 4.5
            weight_g = 22.0
        elif stator == "2806":
            diameter = 7.0
            pitch = 4.0
            weight_g = 8.5
        else:  # 2207
            diameter = 5.1
            pitch = 4.5
            weight_g = 4.2

        # Respect frame max diameter constraint
        if diameter > max_allowed_diameter_inch:
            diameter = max_allowed_diameter_inch
            pitch = round(pitch * 1.15, 1)  # Slightly higher pitch to compensate for smaller diameter

        return {
            "propeller_size": f"{diameter:.1f}x{pitch:.1f}",
            "diameter_inch": diameter,
            "pitch_inch": pitch,
            "blade_count": 2,
            "material": "Carbon Fiber Reinforced Composite",
            "weight_per_prop_g": weight_g,
        }
