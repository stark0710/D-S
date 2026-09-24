from dataclasses import dataclass
from typing import List

@dataclass(slots=True)
class CatalogConnectorRecord:
    """
    Metadata representation of an electrical connector in the component catalog.
    """
    name: str
    max_continuous_current_a: float
    max_burst_current_current_a: float
    weight_kg: float
    pin_count: int
    price_usd: float


class ConnectorSelector:
    """
    Manages catalog search queries and filters for compatible connectors.
    """
    def __init__(self) -> None:
        self._catalog: List[CatalogConnectorRecord] = [
            CatalogConnectorRecord("Servo Connector", 3.0, 5.0, 0.001, 3, 0.50),
            CatalogConnectorRecord("MR30", 30.0, 45.0, 0.003, 3, 1.20),
            CatalogConnectorRecord("MR60", 60.0, 80.0, 0.008, 3, 2.00),
            CatalogConnectorRecord("XT30", 30.0, 45.0, 0.002, 2, 1.00),
            CatalogConnectorRecord("XT60", 60.0, 90.0, 0.007, 2, 1.50),
            CatalogConnectorRecord("XT90", 90.0, 120.0, 0.012, 2, 2.50),
            CatalogConnectorRecord("AS150", 150.0, 200.0, 0.024, 2, 5.00),
        ]

    def get_all_connectors(self) -> List[CatalogConnectorRecord]:
        """Returns the full catalog list."""
        return list(self._catalog)

    def select_connector_for_current(self, current_a: float, is_motor_phase: bool = False) -> CatalogConnectorRecord:
        """
        Selects the lightest connector that handles the specified continuous/peak current.
        """
        candidates = [
            c for c in self._catalog
            if (is_motor_phase and c.pin_count == 3 and c.name != "Servo Connector") or
               (not is_motor_phase and c.pin_count == 2)
        ]
        
        # Sort by weight ascending
        candidates.sort(key=lambda x: x.weight_kg)
        for c in candidates:
            # Check continuous current rating with 15% safety headroom
            if c.max_continuous_current_a >= current_a * 1.15:
                return c
                
        # Return heaviest candidate if none is large enough
        return candidates[-1] if candidates else self._catalog[-1]
