"""
Fixed-Wing Airfoil Selector Subsystem

Purpose:
    Defines the `AirfoilSelector` class to locate and match database records.

Role in Architecture:
    `AirfoilSelector` maps strategy-recommended airfoil names to physical database records,
    applying fallback safety and identifying ranked alternatives.
"""

from typing import Tuple, List, Dict
from backend.design.fixed_wing.airfoil.airfoil_requirements import AirfoilRequirements, AirfoilType
from backend.design.fixed_wing.airfoil.airfoil_database import AirfoilDatabase, AirfoilRecord
from backend.design.fixed_wing.airfoil.airfoil_strategy import AirfoilStrategy


class AirfoilSelector:
    """
    Selector class verifying and matching target airfoils against the database.
    """

    def select_airfoils(
        self, requirements: AirfoilRequirements, strategy: AirfoilStrategy
    ) -> Tuple[AirfoilRecord, AirfoilRecord, str]:
        """
        Selects root and tip airfoil records based on requirements and strategy recommendations.
        """
        rec_root_name, rec_tip_name, distribution = strategy.select_best_airfoils(requirements)

        # 1. Resolve Root record
        root_record = AirfoilDatabase.get_airfoil(rec_root_name)
        if root_record is None:
            # Fallback
            root_record = AirfoilDatabase.get_airfoil("Clark Y")

        # 2. Resolve Tip record
        tip_record = AirfoilDatabase.get_airfoil(rec_tip_name)
        if tip_record is None:
            # Fallback
            tip_record = AirfoilDatabase.get_airfoil("Clark Y")

        return root_record, tip_record, distribution

    def find_alternatives(self, selected_root: AirfoilRecord, allowed_types: List[AirfoilType]) -> List[AirfoilRecord]:
        """
        Finds candidate alternative airfoils compatible with the allowed types.
        """
        alternatives: List[AirfoilRecord] = []
        for name in AirfoilDatabase.list_airfoils():
            record = AirfoilDatabase.get_airfoil(name)
            if record is None:
                continue
            if record.name == selected_root.name:
                continue
            if record.airfoil_type in allowed_types:
                alternatives.append(record)

        return alternatives
