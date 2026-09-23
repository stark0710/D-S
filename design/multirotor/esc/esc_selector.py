from dataclasses import dataclass
from typing import List

@dataclass(slots=True)
class CatalogEscRecord:
    """
    Metadata representation of an ESC component in the component catalog.
    """
    manufacturer: str
    model: str
    continuous_current_a: float
    burst_current_a: float
    min_voltage_v: float
    max_voltage_v: float
    supported_protocols: List[str]  # e.g., ["PWM", "DShot600"]
    empty_mass_kg: float
    has_bec: bool
    bec_voltage_v: float
    bec_current_a: float
    price_usd: float


class EscSelector:
    """
    Manages catalog search queries and filters for compatible ESCs.
    """
    def __init__(self) -> None:
        self._catalog: List[CatalogEscRecord] = [
            CatalogEscRecord("MicroESC", "Nano 20A BEC", 20.0, 30.0, 7.4, 14.8, ["PWM", "OneShot125", "DShot300", "DShot600"], 0.004, True, 5.0, 2.0, 10.00),
            CatalogEscRecord("Spedix", "GS30 DShot", 30.0, 40.0, 7.4, 14.8, ["PWM", "OneShot125", "OneShot42", "DShot300", "DShot600"], 0.006, False, 0.0, 0.0, 15.00),
            CatalogEscRecord("Holybro", "Tekko32 F4 Metal", 65.0, 80.0, 11.1, 22.2, ["PWM", "OneShot125", "OneShot42", "Multishot", "DShot150", "DShot300", "DShot600", "DShot1200"], 0.008, False, 0.0, 0.0, 25.00),
            CatalogEscRecord("T-Motor", "Flame 60A Pro", 60.0, 80.0, 11.1, 22.2, ["PWM"], 0.073, False, 0.0, 0.0, 65.00),
            CatalogEscRecord("T-Motor", "Flame 80A Heavy", 80.0, 120.0, 22.2, 44.4, ["PWM"], 0.106, False, 0.0, 0.0, 110.00),
            CatalogEscRecord("T-Motor", "Flame 180A Extreme", 180.0, 220.0, 22.2, 51.8, ["PWM"], 0.285, False, 0.0, 0.0, 260.00),
        ]

    def get_all_escs(self) -> List[CatalogEscRecord]:
        """Returns the full catalog list."""
        return list(self._catalog)
