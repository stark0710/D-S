"""
VTOL Airfoil Selector Subsystem

Purpose:
    Defines the `AirfoilSelector` class evaluating database candidates
    and returning the optimal match.
"""

from typing import Dict, Tuple
from backend.design.vtol.airfoil.airfoil_requirements import AirfoilRequirements
from backend.design.vtol.airfoil.airfoil_strategy import AirfoilStrategy
from backend.design.vtol.airfoil.airfoil_database import AirfoilDatabase


class AirfoilSelector:
    """
    Selects the optimal airfoil configuration based on constraints and suitability.
    """

    def select_best_airfoil(
        self, requirements: AirfoilRequirements, strategy: AirfoilStrategy
    ) -> str:
        """
        Retrieves the best airfoil name. Respects preferred override if present.
        """
        pref = requirements.preferred_airfoil_name
        if pref is not None:
            # Check if in DB
            db_entry = AirfoilDatabase.get_airfoil(pref)
            if db_entry is not None:
                return pref

        # Score DB candidates
        candidates = AirfoilDatabase.get_all_airfoils()
        preferred_list = strategy.preferred_candidates

        # Pick the first preferred candidate from the strategy list that exists in database
        for cand in preferred_list:
            if cand in candidates:
                return cand

        # Fallback to Clark Y
        return "Clark Y"
