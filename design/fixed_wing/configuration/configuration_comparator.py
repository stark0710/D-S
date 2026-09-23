"""
Fixed-Wing Aircraft Configuration Comparator Subsystem

Purpose:
    Defines the `ConfigurationComparator` class to perform side-by-side trade-off analysis.

Role in Architecture:
    `ConfigurationComparator` compares two configuration layouts to produce a detailed
    aerodynamic, structural, and financial comparison matrix.
"""

from typing import Dict, Any, List


class ConfigurationComparator:
    """
    Comparison service to evaluate trade-offs between alternative aircraft architectures.
    """

    def compare(self, config_a: Dict[str, str], config_b: Dict[str, str], scores_a: Dict[str, float], scores_b: Dict[str, float]) -> Dict[str, Any]:
        """
        Runs a side-by-side comparison of two configurations.

        Args:
            config_a (Dict[str, str]): Layout A attributes.
            config_b (Dict[str, str]): Layout B attributes.
            scores_a (Dict[str, float]): Scores for Layout A.
            scores_b (Dict[str, float]): Scores for Layout B.

        Returns:
            Dict[str, Any]: Comparison report.
        """
        trade_offs: List[str] = []

        # Compare Wing Position
        wing_a = config_a.get("wing_position")
        wing_b = config_b.get("wing_position")
        if wing_a != wing_b:
            trade_offs.append(
                f"Wing position: {wing_a} offers different roll stability and ground clearance "
                f"characteristics compared to {wing_b}."
            )

        # Compare Propulsion
        prop_a = config_a.get("propulsion_layout")
        prop_b = config_b.get("propulsion_layout")
        if prop_a != prop_b:
            trade_offs.append(
                f"Propulsion layout: {prop_a} affects camera visibility and thrust alignment "
                f"differently than {prop_b}."
            )

        # Compare Tail
        tail_a = config_a.get("tail_configuration")
        tail_b = config_b.get("tail_configuration")
        if tail_a != tail_b:
            trade_offs.append(
                f"Tail assembly: {tail_a} impacts stability derivatives and structural complexity "
                f"compared to the {tail_b} layout."
            )

        # Compare Landing Gear
        gear_a = config_a.get("landing_gear_configuration")
        gear_b = config_b.get("landing_gear_configuration")
        if gear_a != gear_b:
            trade_offs.append(
                f"Landing gear: {gear_a} affects drag in flight and operational site flexibility "
                f"relative to {gear_b}."
            )

        # Calculate delta scores
        delta_aerodynamics = round(scores_a.get("aerodynamics", 0.0) - scores_b.get("aerodynamics", 0.0), 2)
        delta_simplicity = round(scores_a.get("simplicity", 0.0) - scores_b.get("simplicity", 0.0), 2)
        delta_cost = round(scores_a.get("cost", 0.0) - scores_b.get("cost", 0.0), 2)

        comparison_matrix = {
            "aerodynamics_delta": delta_aerodynamics,
            "simplicity_delta": delta_simplicity,
            "cost_delta": delta_cost,
            "winner": "A" if scores_a.get("overall_score", 0.0) >= scores_b.get("overall_score", 0.0) else "B",
        }

        return {
            "config_a_name": config_a.get("architecture", "Config A"),
            "config_b_name": config_b.get("architecture", "Config B"),
            "comparison_matrix": comparison_matrix,
            "trade_offs": trade_offs,
            "rationales": {
                "aerodynamics": f"Config A is {abs(delta_aerodynamics)} points {'better' if delta_aerodynamics >= 0 else 'worse'} aerodynamically.",
                "structural_simplicity": f"Config A is {abs(delta_simplicity)} points {'simpler' if delta_simplicity >= 0 else 'more complex'}.",
                "cost_impact": f"Config A is {abs(delta_cost)} points {'more cost-effective' if delta_cost >= 0 else 'more expensive'}.",
            }
        }
