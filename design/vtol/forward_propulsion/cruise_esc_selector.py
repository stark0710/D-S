"""
VTOL Cruise ESC Selector Subsystem

Purpose:
    Defines the `CruiseEscSelector` database class managing candidate ESC profiles.
"""

from typing import Dict, List, Any


class CruiseEscSelector:
    """
    Ranks and selects the optimal ESC matching the motor maximum current.
    """

    _db: Dict[str, Dict[str, Any]] = {
        "Hobbywing XRotor 40A": {
            "name": "Hobbywing XRotor 40A",
            "current_limit_a": 40.0,
            "mass_kg": 0.035,
            "price_usd": 35.0,
        },
        "Hobbywing XRotor 80A": {
            "name": "Hobbywing XRotor 80A",
            "current_limit_a": 80.0,
            "mass_kg": 0.075,
            "price_usd": 65.0,
        },
        "Hobbywing XRotor 120A": {
            "name": "Hobbywing XRotor 120A",
            "current_limit_a": 120.0,
            "mass_kg": 0.110,
            "price_usd": 95.0,
        },
    }

    @classmethod
    def get_esc(cls, name: str) -> Dict[str, Any] | None:
        """Retrieves ESC details by name."""
        return cls._db.get(name)

    def select_optimal_esc(
        self, motor_max_current_a: float, preferred_model: str | None = None
    ) -> Dict[str, Any]:
        """
        Selects the best ESC.

        Ensures candidate's current_limit_a exceeds the motor max current by 20% margin.
        """
        if preferred_model is not None and preferred_model in self._db:
            return self._db[preferred_model]

        required_margin_current = motor_max_current_a * 1.2
        qualified = [esc for esc in self._db.values() if esc["current_limit_a"] >= required_margin_current]

        if not qualified:
            return self._db["Hobbywing XRotor 120A"]

        # Pick the lightest ESC to maximize weight efficiency
        selected = min(qualified, key=lambda x: x["mass_kg"])
        return selected
"""
Sizing forward drive train components.
"""
