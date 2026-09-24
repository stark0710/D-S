"""
VTOL Battery Chemistry Selector Subsystem

Purpose:
    Defines the `BatterySelector` database class managing candidate battery chemistry profiles.
"""

from typing import Dict, List, Any


class BatterySelector:
    """
    Ranks and selects the optimal battery chemistry based on discharge rates and energy densities.
    """

    _db: Dict[str, Dict[str, Any]] = {
        "LiPo": {
            "name": "LiPo",
            "nominal_cell_voltage_v": 3.7,
            "wh_per_kg": 180.0,
            "max_c_rate": 45.0,
            "internal_resistance_mohm": 1.5,
            "cycle_life": 300,
            "description": "Lithium Polymer. High discharge currents, low internal resistance, low energy density.",
        },
        "LiHV": {
            "name": "LiHV",
            "nominal_cell_voltage_v": 3.8,
            "wh_per_kg": 200.0,
            "max_c_rate": 40.0,
            "internal_resistance_mohm": 1.8,
            "cycle_life": 250,
            "description": "High Voltage Lithium Polymer. Good compromise between current and density.",
        },
        "Li-Ion": {
            "name": "Li-Ion",
            "nominal_cell_voltage_v": 3.6,
            "wh_per_kg": 245.0,
            "max_c_rate": 15.0,
            "internal_resistance_mohm": 8.0,
            "cycle_life": 500,
            "description": "Lithium Ion. High specific energy density, higher resistance, low peak discharge C-rate.",
        },
        "Solid-State": {
            "name": "Solid-State",
            "nominal_cell_voltage_v": 3.8,
            "wh_per_kg": 350.0,
            "max_c_rate": 10.0,
            "internal_resistance_mohm": 12.0,
            "cycle_life": 800,
            "description": "Solid State battery. Ultra high energy density, low C-rate limits, high cost.",
        },
    }

    @classmethod
    def get_chemistry(cls, name: str) -> Dict[str, Any] | None:
        """Retrieves chemistry details by name."""
        return cls._db.get(name)

    @classmethod
    def get_all_chemistries(cls) -> List[str]:
        """Returns names of all registered chemistries."""
        return list(cls._db.keys())

    def select_optimal_chemistry(
        self, required_c_rate: float, preferred_chemistry: str | None = None
    ) -> Dict[str, Any]:
        """
        Selects the best battery chemistry.

        Ensures candidate's max_c_rate exceeds the required C-rate.
        """
        if preferred_chemistry is not None and preferred_chemistry in self._db:
            candidate = self._db[preferred_chemistry]
            if candidate["max_c_rate"] >= required_c_rate:
                return candidate

        # Filter candidates that can handle the discharge currents
        qualified = [c for c in self._db.values() if c["max_c_rate"] >= required_c_rate]

        if not qualified:
            # Fallback to LiPo
            return self._db["LiPo"]

        # Pick the chemistry with the highest energy density to minimize pack weight
        selected = max(qualified, key=lambda x: x["wh_per_kg"])
        return selected
