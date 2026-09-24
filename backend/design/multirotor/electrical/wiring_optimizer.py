from dataclasses import dataclass
from typing import List

@dataclass(slots=True)
class CatalogWireRecord:
    """
    Metadata representation of an electrical conductor wire in the component catalog.
    """
    awg: int
    max_continuous_current_a: float
    resistance_ohms_per_m: float
    weight_kg_per_m: float


class WiringOptimizer:
    """
    Optimizes wiring gauges and routes to minimize voltage drop and weight.
    """
    def __init__(self) -> None:
        self._catalog: List[CatalogWireRecord] = [
            CatalogWireRecord(8, 150.0, 0.0021, 0.075),
            CatalogWireRecord(10, 110.0, 0.0033, 0.052),
            CatalogWireRecord(12, 75.0, 0.0052, 0.038),
            CatalogWireRecord(14, 50.0, 0.0083, 0.024),
            CatalogWireRecord(16, 35.0, 0.0132, 0.015),
            CatalogWireRecord(18, 22.0, 0.0210, 0.009),
            CatalogWireRecord(20, 11.0, 0.0333, 0.005),
            CatalogWireRecord(22, 7.0, 0.0530, 0.003),
        ]

    def get_all_wires(self) -> List[CatalogWireRecord]:
        """Returns the full catalog list."""
        return list(self._catalog)

    def select_wire_gauge_for_current(self, current_a: float) -> CatalogWireRecord:
        """
        Selects the lightest wire that handles the specified current.
        """
        # Sort by weight ascending
        sorted_wires = sorted(self._catalog, key=lambda x: x.weight_kg_per_m)
        for w in sorted_wires:
            # Check continuous current rating
            if w.max_continuous_current_a >= current_a:
                return w
        # Return heaviest candidate if none is large enough
        return sorted_wires[-1]

    @staticmethod
    def calculate_voltage_drop(current_a: float, resistance_ohms_per_m: float, length_m: float) -> float:
        """
        Calculates voltage drop: V_drop = I * R * L * 2 (for positive and negative returns).
        """
        return current_a * resistance_ohms_per_m * length_m * 2.0
