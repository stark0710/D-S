from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class EnergyAnalysis:
    """
    Integrated energy and battery current drains during conversion.
    """
    peak_current_draw_amps: float
    total_energy_consumed_kwh: float
    battery_charge_depletion_pct: float
    voltage_sag_minimum_volts: float
    metadata: Dict[str, Any] = field(default_factory=dict)
