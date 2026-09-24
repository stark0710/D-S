"""
Fixed-Wing Aircraft Configuration Recommender Subsystem

Purpose:
    Defines the `ConfigurationRecommender` class to generate layout-specific engineering advice.

Role in Architecture:
    `ConfigurationRecommender` translates layout parameters into actionable sizing, aerodynamic,
    and manufacturing suggestions.
"""

from typing import List, Dict


class ConfigurationRecommender:
    """
    Service to compile engineering recommendations based on selected layout components.
    """

    def generate_recommendations(self, layout: Dict[str, str], payload_kg: float) -> List[str]:
        """
        Generates layout-specific recommendations.

        Args:
            layout (Dict[str, str]): Selected layout attributes.
            payload_kg (float): Payload mass in kg.

        Returns:
            List[str]: Actionable design tips.
        """
        recommendations: List[str] = []

        wing = layout.get("wing_position", "")
        prop = layout.get("propulsion_layout", "")
        tail = layout.get("tail_configuration", "")
        gear = layout.get("landing_gear_configuration", "")

        # Wing Recommendations
        if wing == "High Wing":
            recommendations.append(
                "For High Wing layout, configure a dihedral angle of 1 to 3 degrees to improve roll damping "
                "without causing excessive spiral instability."
            )
        elif wing == "Low Wing":
            recommendations.append(
                "For Low Wing layout, configure a dihedral angle of 4 to 6 degrees to compensate for the "
                "loss of pendulum stability relative to high-wing models."
            )
        elif wing == "Parasol Wing":
            recommendations.append(
                "Parasol wing placement requires high-strength cabane struts. Monitor aerodynamic interference "
                "between struts and wing center section."
            )

        # Propulsion Recommendations
        if prop == "Pusher":
            recommendations.append(
                "Rear pusher motor requires a robust firewall and heat shielding. Ensure trailing control surface "
                "linkages clear the propeller sweep."
            )
            recommendations.append(
                "Implement a folding propeller setup if glide phases or low-drag soaring are primary objectives."
            )
        elif prop == "Twin Tractor" or prop == "Twin Pusher":
            recommendations.append(
                "Twin propulsion systems should utilize counter-rotating propellers (CW and CCW) "
                "to cancel gyroscopic precession and torque roll effects."
            )

        # Tail Recommendations
        if tail == "Twin Boom":
            recommendations.append(
                "Utilize carbon-fiber booms to prevent tail assembly twisting under aerodynamic loads. "
                "Verify structural junction strength at wing-boom connections."
            )
        elif tail == "V-Tail":
            recommendations.append(
                "Use a V-Tail angle of 110 degrees for a balanced compromise between horizontal and vertical tail authority."
            )
        elif tail == "Flying Wing" or tail == "Tailless":
            recommendations.append(
                "Flying wings require reflexed airfoils or negative aerodynamic washouts at wingtips "
                "to provide passive longitudinal pitch stability."
            )
            recommendations.append(
                "Ensure Center of Gravity is tightly constrained within 15% to 22% of Mean Aerodynamic Chord."
            )

        # Landing Gear Recommendations
        if gear == "Belly Landing":
            recommendations.append(
                "Add a replaceable skid plate or reinforce the fuselage belly with Kevlar tape "
                "to prevent abrasion during rough field recovery."
            )
        elif gear == "Taildragger":
            recommendations.append(
                "Taildragger gear requires placing the main wheels 15 to 20 degrees forward of the "
                "Center of Gravity in three-point stance to prevent nose-over landing tendencies."
            )

        # Payload Sizing Recommendations
        if payload_kg > 8.0:
            recommendations.append(
                "Heavy payloads require structural landing loads distributed directly into fuselage bulkheads. "
                "Ensure payload bay sits on the neutral axis of the fuselage structure."
            )

        return recommendations
