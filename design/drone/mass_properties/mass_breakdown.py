"""
MassBreakdown Subsystem

Purpose:
    Defines the `MassBreakdown` domain model and aggregation service.

Role in Architecture:
    `MassBreakdown` aggregates mass across major subsystem categories (Structure, Propulsion, Electrical, Avionics, Payload, Landing Gear, Fasteners, Margins)
    and computes total All-Up Weight (AUW) and empty mass in grams.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.mass_properties.component_mass import ComponentMass


@dataclass(slots=True)
class MassBreakdown:
    """
    Multirotor mass breakdown summary model.

    Attributes:
        structure_mass_g (float): Airframe structure mass in grams.
        propulsion_mass_g (float): Motors and propellers mass in grams.
        electrical_mass_g (float): Battery, ESCs, PDB, BEC, connectors, wiring mass in grams.
        avionics_mass_g (float): Flight controller, GNSS, receiver, telemetry, companion computer mass in grams.
        payload_mass_g (float): Mission payload mass in grams.
        landing_gear_mass_g (float): Landing gear mass in grams.
        fasteners_mass_g (float): Bolts, nuts, standoffs, adhesive mass in grams (~5%).
        margins_mass_g (float): Engineering growth margin mass in grams (~5%).
        total_mass_g (float): Total All-Up Weight (AUW) in grams.
        empty_mass_g (float): Empty aircraft weight (without battery and payload) in grams.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    structure_mass_g: float
    propulsion_mass_g: float
    electrical_mass_g: float
    avionics_mass_g: float
    payload_mass_g: float
    landing_gear_mass_g: float
    fasteners_mass_g: float
    margins_mass_g: float
    total_mass_g: float
    empty_mass_g: float
    metadata: dict[str, Any] = field(default_factory=dict)


class MassBreakdownCalculator:
    """
    Aggregator service for multirotor mass breakdown.

    Design Principles:
        - Single Responsibility Principle: Mass breakdown category summation only.
    """

    def calculate_breakdown(self, components: list[ComponentMass]) -> MassBreakdown:
        """
        Sums component masses by category.

        Args:
            components (list[ComponentMass]): List of component masses.

        Returns:
            MassBreakdown: Computed mass breakdown summary.
        """
        cat_sums: dict[str, float] = {
            "STRUCTURE": 0.0,
            "PROPULSION": 0.0,
            "ELECTRICAL": 0.0,
            "AVIONICS": 0.0,
            "PAYLOAD": 0.0,
            "LANDING_GEAR": 0.0,
            "FASTENERS": 0.0,
            "MARGIN": 0.0,
        }

        for c in components:
            cat = c.category.upper()
            if cat in cat_sums:
                cat_sums[cat] += c.mass_g
            else:
                cat_sums["STRUCTURE"] += c.mass_g

        total_g = sum(cat_sums.values())
        empty_g = total_g - cat_sums["PAYLOAD"] - cat_sums["ELECTRICAL"]

        return MassBreakdown(
            structure_mass_g=round(cat_sums["STRUCTURE"], 1),
            propulsion_mass_g=round(cat_sums["PROPULSION"], 1),
            electrical_mass_g=round(cat_sums["ELECTRICAL"], 1),
            avionics_mass_g=round(cat_sums["AVIONICS"], 1),
            payload_mass_g=round(cat_sums["PAYLOAD"], 1),
            landing_gear_mass_g=round(cat_sums["LANDING_GEAR"], 1),
            fasteners_mass_g=round(cat_sums["FASTENERS"], 1),
            margins_mass_g=round(cat_sums["MARGIN"], 1),
            total_mass_g=round(total_g, 1),
            empty_mass_g=round(empty_g, 1)
        )
