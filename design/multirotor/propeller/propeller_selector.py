from dataclasses import dataclass
from typing import List

@dataclass(slots=True)
class CatalogPropellerRecord:
    """
    Metadata representation of a propeller component in the component catalog.
    """
    manufacturer: str
    model: str
    diameter_m: float
    pitch_m: float
    blade_count: int
    material: str
    empty_mass_kg: float
    max_rpm: float
    hub_size_mm: float
    price_usd: float


class PropellerSelector:
    """
    Manages search queries and filters for compatible propellers.
    """
    def __init__(self) -> None:
        self._catalog: List[CatalogPropellerRecord] = [
            # 5 inch, 3 blade prop for micro drones
            CatalogPropellerRecord("HQProp", "5x4.3x3 V2S", 0.127, 0.109, 3, "Nylon", 0.004, 32000.0, 5.0, 1.50),
            # 10 inch prop for small drones
            CatalogPropellerRecord("APC", "10x4.7 MR", 0.254, 0.119, 2, "Nylon-Glass", 0.015, 14000.0, 6.0, 3.50),
            # 13 inch carbon prop for medium drones
            CatalogPropellerRecord("Tarot", "13x5.5 Carbon", 0.330, 0.140, 2, "Carbon Fiber", 0.024, 11000.0, 6.0, 12.00),
            # 15 inch carbon prop for large drones
            CatalogPropellerRecord("Tarot", "15x5.5 Carbon", 0.381, 0.140, 2, "Carbon Fiber", 0.032, 10000.0, 6.0, 18.00),
            # 18 inch carbon prop for heavy lift
            CatalogPropellerRecord("T-Motor", "18x6.1 Carbon", 0.457, 0.155, 2, "Carbon Fiber", 0.045, 8500.0, 8.0, 45.00),
            # 22 inch carbon prop for extreme heavy lift
            CatalogPropellerRecord("T-Motor", "22x7.2 Carbon", 0.559, 0.183, 2, "Carbon Fiber", 0.075, 7000.0, 8.0, 85.00),
        ]

    def get_all_propellers(self) -> List[CatalogPropellerRecord]:
        """Returns the full catalog list."""
        return list(self._catalog)
