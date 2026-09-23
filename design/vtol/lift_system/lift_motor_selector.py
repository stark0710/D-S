"""
VTOL Lift Motor Selector Subsystem

Purpose:
    Defines the `LiftMotorSelector` database class managing candidate brushless motor profiles.
"""

from typing import Dict, List, Any


class LiftMotorSelector:
    """
    Ranks and selects the optimal brushless motor matching the required rotor thrust.
    """

    _db: Dict[str, Dict[str, Any]] = {
        "T-Motor MN5008": {
            "name": "T-Motor MN5008",
            "kv": 400.0,
            "max_thrust_n": 28.0,
            "mass_kg": 0.14,
            "max_current_a": 20.0,
            "price_usd": 130.0,
            "description": "Lightweight motor optimized for high efficiency multirotors.",
        },
        "T-Motor MN6007": {
            "name": "T-Motor MN6007",
            "kv": 320.0,
            "max_thrust_n": 42.0,
            "mass_kg": 0.18,
            "max_current_a": 25.0,
            "price_usd": 190.0,
            "description": "Medium lift high efficiency motor for mapping drones.",
        },
        "T-Motor U8 Lite": {
            "name": "T-Motor U8 Lite",
            "kv": 150.0,
            "max_thrust_n": 65.0,
            "mass_kg": 0.24,
            "max_current_a": 32.0,
            "price_usd": 280.0,
            "description": "Heavy industrial motor with excellent thermal heat sinks.",
        },
        "Hobbywing XRotor 8120": {
            "name": "Hobbywing XRotor 8120",
            "kv": 100.0,
            "max_thrust_n": 165.0,
            "mass_kg": 0.64,
            "max_current_a": 85.0,
            "price_usd": 390.0,
            "description": "Large agricultural heavy lifting motor and ESC combo.",
        },
        "Hobbywing XRotor 10120": {
            "name": "Hobbywing XRotor 10120",
            "kv": 80.0,
            "max_thrust_n": 250.0,
            "mass_kg": 0.88,
            "max_current_a": 115.0,
            "price_usd": 520.0,
            "description": "Extra heavy lift industrial motor.",
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
        self, required_max_thrust_per_rotor_n: float, preferred_model: str | None = None
    ) -> Dict[str, Any]:
        """
        Selects the best brushless motor.

        Ensures candidate's max_thrust_n exceeds the required maximum thrust per rotor.
        If preferred model is set and matches thrust limits, it will be selected.
        """
        if preferred_model is not None and preferred_model in self._db:
            candidate = self._db[preferred_model]
            if candidate["max_thrust_n"] >= required_max_thrust_per_rotor_n:
                return candidate

        # Filter candidates that can physically generate the required thrust
        qualified = [m for m in self._db.values() if m["max_thrust_n"] >= required_max_thrust_per_rotor_n]

        if not qualified:
            # Fallback to the largest motor in database
            return self._db["Hobbywing XRotor 8120"]

        # Pick the lightest motor to maximize empty weight efficiency
        selected = min(qualified, key=lambda x: x["mass_kg"])
        return selected
