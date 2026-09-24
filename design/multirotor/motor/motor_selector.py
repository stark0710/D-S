from dataclasses import dataclass
from typing import List

@dataclass(slots=True)
class CatalogMotorRecord:
    """
    Metadata representation of a motor component in the component catalog.
    """
    manufacturer: str
    model: str
    kv_rating: float
    empty_mass_kg: float
    max_continuous_current_a: float
    min_voltage_v: float
    max_voltage_v: float
    peak_current_a: float
    max_thrust_n: float  # In Newtons
    price_usd: float
    mount_pattern_mm: str


class MotorSelector:
    """
    Manages catalog search queries and filters for compatible motors.
    """
    def __init__(self) -> None:
        self._catalog: List[CatalogMotorRecord] = [
            CatalogMotorRecord("T-Motor", "MN1806-2300", 2300.0, 0.018, 12.0, 7.4, 11.1, 15.0, 4.41, 18.0, "12x12"),
            CatalogMotorRecord("T-Motor", "F40 PRO IV-1950", 1950.0, 0.032, 45.0, 14.8, 22.2, 52.0, 17.65, 29.0, "16x16"),
            CatalogMotorRecord("T-Motor", "MN4014-370", 370.0, 0.150, 28.0, 14.8, 29.6, 35.0, 31.40, 85.0, "25x25"),
            CatalogMotorRecord("T-Motor", "MN5008-400", 400.0, 0.135, 30.0, 22.2, 22.2, 38.0, 35.30, 98.0, "25x25"),
            CatalogMotorRecord("T-Motor", "U8 II-190", 190.0, 0.240, 40.0, 22.2, 44.4, 50.0, 71.60, 280.0, "30x30"),
            CatalogMotorRecord("T-Motor", "U11 II-120", 120.0, 0.730, 55.0, 44.4, 51.8, 70.0, 142.20, 490.0, "35x35"),
        ]

    def get_matching_motors(self, min_kv: float, max_kv: float) -> List[CatalogMotorRecord]:
        """
        Retrieves motors within preferred KV limits.
        """
        results: List[CatalogMotorRecord] = []
        for motor in self._catalog:
            if min_kv <= motor.kv_rating <= max_kv:
                results.append(motor)
        
        # Fallback if no exact KV matches: return all
        if not results:
            return list(self._catalog)
        return results

    def get_all_motors(self) -> List[CatalogMotorRecord]:
        """Returns the full catalog list."""
        return list(self._catalog)
