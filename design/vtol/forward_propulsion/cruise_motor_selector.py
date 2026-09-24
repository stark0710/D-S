"""
VTOL Cruise Motor Selector Subsystem

Purpose:
    Defines the `CruiseMotorSelector` database class managing candidate brushless motor profiles.
"""

from typing import Dict, List, Any


class CruiseMotorSelector:
    """
    Ranks and selects the optimal brushless motor matching the required cruise power.
    """

    _db: Dict[str, Dict[str, Any]] = {
        "T-Motor MN4014": {
            "name": "T-Motor MN4014",
            "kv": 370.0,
            "max_power_w": 900.0,
            "mass_kg": 0.15,
            "max_current_a": 25.0,
            "price_usd": 110.0,
            "description": "Lightweight motor optimized for high efficiency forward flight.",
        },
        "T-Motor MN5008": {
            "name": "T-Motor MN5008",
            "kv": 400.0,
            "max_power_w": 1200.0,
            "mass_kg": 0.14,
            "max_current_a": 20.0,
            "price_usd": 130.0,
            "description": "Excellent power density motor.",
        },
        "T-Motor U8 Lite": {
            "name": "T-Motor U8 Lite",
            "kv": 150.0,
            "max_power_w": 1600.0,
            "mass_kg": 0.24,
            "max_current_a": 32.0,
            "price_usd": 280.0,
            "description": "Heavy industrial motor.",
        },
        "Hobbywing XRotor 8120": {
            "name": "Hobbywing XRotor 8120",
            "kv": 100.0,
            "max_power_w": 3200.0,
            "mass_kg": 0.64,
            "max_current_a": 85.0,
            "price_usd": 390.0,
            "description": "Extra heavy lift forward motor.",
        },
    }

    @classmethod
    def get_motor(cls, name: str) -> Dict[str, Any] | None:
        """Retrieves motor details by name."""
        return cls._db.get(name)

    @classmethod
    def get_all_motors(cls) -> List[str]:
        """Returns names of all registered motors."""
        return list(cls._db.keys())

    def select_optimal_motor(
        self, required_power_per_motor_w: float, preferred_model: str | None = None
    ) -> Dict[str, Any]:
        """
        Selects the best brushless motor.

        Ensures candidate's max_power_w exceeds the required power.
        """
        if preferred_model is not None and preferred_model in self._db:
            candidate = self._db[preferred_model]
            if candidate["max_power_w"] >= required_power_per_motor_w:
                return candidate

        # Filter candidates that can handle the required power
        qualified = [m for m in self._db.values() if m["max_power_w"] >= required_power_per_motor_w]

        if not qualified:
            # Fallback to largest motor
            return self._db["Hobbywing XRotor 8120"]

        # Pick the lightest motor to maximize empty weight efficiency
        selected = min(qualified, key=lambda x: x["mass_kg"])
        return selected
