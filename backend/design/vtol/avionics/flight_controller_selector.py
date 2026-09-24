"""
VTOL Flight Controller Selector logic
"""

from dataclasses import dataclass
from typing import List

@dataclass(slots=True)
class FlightController:
    name: str
    manufacturer: str
    supported_firmware: List[str]
    weight_kg: float
    power_draw_watts: float
    redundancy_level: int  # 1: Single, 2: Dual, 3: Triple
    has_ethernet: bool
    can_ports: int
    uart_ports: int
    i2c_ports: int
    spi_ports: int
    clock_speed_mhz: float
    ram_mb: float
    cost_usd: float

class FlightControllerSelector:
    """
    Matches autopilot hardware units to VTOL configuration requirements.
    """
    _database: List[FlightController] = [
        FlightController("Pixhawk 6X", "Holybro", ["PX4", "ArduPilot"], 0.095, 3.5, 3, True, 3, 6, 4, 2, 480, 2.0, 350.0),
        FlightController("Pixhawk 6C", "Holybro", ["PX4", "ArduPilot"], 0.045, 2.5, 2, False, 2, 4, 2, 1, 480, 2.0, 180.0),
        FlightController("Cube Orange", "CubePilot", ["ArduPilot", "PX4"], 0.073, 3.0, 3, False, 2, 5, 2, 1, 400, 2.0, 270.0),
        FlightController("CUAV V5+", "CUAV", ["PX4", "ArduPilot"], 0.090, 3.2, 2, False, 2, 5, 2, 1, 400, 2.0, 320.0),
        FlightController("Auterion Skynode", "Auterion", ["PX4"], 0.160, 10.0, 3, True, 2, 4, 2, 2, 1500, 4096.0, 1200.0),
        FlightController("Custom Flight Controller", "Custom", ["ArduPilot", "PX4"], 0.120, 5.0, 3, True, 4, 8, 4, 4, 800, 1024.0, 1500.0)
    ]

    def select(self, redundancy_level: int = 1, needs_ethernet: bool = False, preferred: str | None = None) -> FlightController:
        if preferred:
            for fc in self._database:
                if fc.name.lower() == preferred.lower():
                    return fc

        candidates = [
            fc for fc in self._database 
            if fc.redundancy_level >= redundancy_level 
            and (not needs_ethernet or fc.has_ethernet)
        ]

        if not candidates:
            # Fallback to Ethernet-capable if Ethernet requested
            candidates = [fc for fc in self._database if fc.has_ethernet]
            if not candidates:
                return self._database[-1] # Custom FC fallback
        
        candidates.sort(key=lambda x: (x.weight_kg, x.power_draw_watts))
        return candidates[0]
