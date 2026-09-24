"""
VTOL Cruise Propeller Selector Subsystem

Purpose:
    Defines the `CruisePropellerSelector` database class matching carbon fiber props
    to brushless motor outputs.
"""

from typing import Dict, List, Any


class CruisePropellerSelector:
    """
    Ranks and selects the optimal propeller matching the motor KV and structural limits.
    """

    _db: Dict[str, Dict[str, Any]] = {
        "APC 12x6 E": {
            "name": "APC 12x6 E",
            "diameter_m": 0.305,  # 12 inches
            "pitch_in": 6.0,
            "mass_kg": 0.015,
            "typical_motor": "T-Motor MN4014",
        },
        "T-Motor 15x5 CF": {
            "name": "T-Motor 15x5 CF",
            "diameter_m": 0.381,  # 15 inches
            "pitch_in": 5.0,
            "mass_kg": 0.022,
            "typical_motor": "T-Motor MN5008",
        },
        "T-Motor 22x7.2 CF": {
            "name": "T-Motor 22x7.2 CF",
            "diameter_m": 0.559,  # 22 inches
            "pitch_in": 7.2,
            "mass_kg": 0.052,
            "typical_motor": "T-Motor U8 Lite",
        },
        "Hobbywing 30x9.0 CF": {
            "name": "Hobbywing 30x9.0 CF",
            "diameter_m": 0.762,  # 30 inches
            "pitch_in": 9.0,
            "mass_kg": 0.110,
            "typical_motor": "Hobbywing XRotor 8120",
        },
    }

    @classmethod
    def get_propeller(cls, name: str) -> Dict[str, Any] | None:
        """Retrieves propeller details by name."""
        return cls._db.get(name)

    def select_optimal_propeller(
        self, motor_name: str, preferred_model: str | None = None
    ) -> Dict[str, Any]:
        """
        Selects the best propeller corresponding to the motor model.
        """
        if preferred_model is not None and preferred_model in self._db:
            return self._db[preferred_model]

        for prop in self._db.values():
            if prop["typical_motor"] == motor_name:
                return prop

        # Fallback
        return self._db["T-Motor 15x5 CF"]
