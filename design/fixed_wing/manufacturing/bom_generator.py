"""
Fixed-Wing Bill of Materials (BOM) Generator Subsystem

Purpose:
    Defines the `BOMGenerator` class.

Role in Architecture:
    `BOMGenerator` compiles the list of parts, fasteners, and purchase components.
"""

from typing import List, Dict, Any
from backend.design.fixed_wing.manufacturing.manufacturing_requirements import ManufacturingRequirements


class BOMGenerator:
    """
    Service compiling the bill of materials with quantities, materials, and weights.
    """

    def generate_bom(self, requirements: ManufacturingRequirements) -> List[Dict[str, Any]]:
        """
        Generates the Bill of Materials checklist.

        Returns:
            List[Dict[str, Any]]: Sized BOM items map.
        """
        bom: List[Dict[str, Any]] = []

        # Core custom fabrication components
        bom.extend([
            {
                "part_number": "TW-FW-001",
                "name": "Main Wing Panel",
                "quantity": 1,
                "type": "Fabricated",
                "material": "Balsa Wood / Carbon spars" if requirements.wing_result.planform != "Delta" else "EPO Foam",
                "weight_kg": round(requirements.mass_result.weight_breakdown.structural_weight_kg * 0.40, 3),
            },
            {
                "part_number": "TW-FW-002",
                "name": "Fuselage Shell",
                "quantity": 1,
                "type": "Fabricated",
                "material": "Carbon Fiber / Composite shell",
                "weight_kg": round(requirements.mass_result.weight_breakdown.structural_weight_kg * 0.45, 3),
            },
            {
                "part_number": "TW-FW-003",
                "name": "Tail Fin Assembly",
                "quantity": 1,
                "type": "Fabricated",
                "material": "Balsa Wood",
                "weight_kg": round(requirements.mass_result.weight_breakdown.structural_weight_kg * 0.15, 3),
            },
        ])

        # Purchase standard components
        prop = requirements.propulsion_result
        bom.extend([
            {
                "part_number": "TW-FW-COM-101",
                "name": f"Motor: {prop.selected_motor_or_engine}",
                "quantity": 1,
                "type": "Purchased",
                "supplier": "SunnySky Global",
                "weight_kg": round(prop.power_analysis.metadata.get("motor_weight_g", 310) / 1000.0, 3),
            },
            {
                "part_number": "TW-FW-COM-102",
                "name": f"Propeller: {prop.selected_propeller}",
                "quantity": 1,
                "type": "Purchased",
                "supplier": "APC Propellers",
                "weight_kg": 0.065,
            },
            {
                "part_number": "TW-FW-COM-103",
                "name": f"Autopilot FC: {requirements.avionics_result.selected_flight_controller}",
                "quantity": 1,
                "type": "Purchased",
                "supplier": "Holybro",
                "weight_kg": 0.080,
            },
            {
                "part_number": "TW-FW-COM-104",
                "name": "LiPo Battery Pack 6S",
                "quantity": 1,
                "type": "Purchased",
                "supplier": "Tattu GensAce",
                "weight_kg": round(requirements.mass_result.weight_breakdown.battery_fuel_weight_kg, 3),
            },
        ])

        # Fasteners
        bom.append({
            "part_number": "TW-FW-FAST-201",
            "name": "Wing Mount Bolt M5",
            "quantity": 4,
            "type": "Fastener",
            "material": "Nylon",
            "weight_kg": 0.005,
        })

        return bom
