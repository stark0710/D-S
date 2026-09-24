"""
VTOL Companion Computer Selector logic
"""

from dataclasses import dataclass
from typing import List

@dataclass(slots=True)
class CompanionComputer:
    name: str
    processor: str
    tops: float
    weight_kg: float
    power_draw_watts: float
    interfaces: List[str]
    ram_mb: float
    cost_usd: float

class CompanionComputerSelector:
    """
    Matches companion computer units to mission autonomy profiles.
    """
    _database: List[CompanionComputer] = [
        CompanionComputer("None", "None", 0.0, 0.0, 0.0, [], 0, 0.0),
        CompanionComputer("Raspberry Pi 4", "BCM2711", 0.1, 0.046, 5.0, ["Ethernet", "UART", "USB3"], 4096, 75.0),
        CompanionComputer("Jetson Nano", "Tegra X1", 0.5, 0.140, 10.0, ["Ethernet", "UART", "USB3"], 4096, 149.0),
        CompanionComputer("Jetson Xavier NX", "Carmel", 21.0, 0.160, 15.0, ["Ethernet", "UART", "USB3", "CAN"], 8192, 399.0),
        CompanionComputer("Jetson Orin NX", "Cortex-A78AE", 100.0, 0.200, 20.0, ["Ethernet", "UART", "USB3", "CAN"], 16384, 599.0),
        CompanionComputer("Intel NUC", "Core i7", 10.0, 0.550, 45.0, ["Ethernet", "UART", "USB3"], 16384, 800.0),
        CompanionComputer("RK3588", "Rockchip RK3588", 6.0, 0.060, 8.0, ["Ethernet", "UART", "USB3", "CAN"], 8192, 120.0),
        CompanionComputer("Custom Companion Computer", "Custom FPGA/ASIC", 150.0, 0.300, 25.0, ["Ethernet", "UART", "USB3", "CAN"], 32768, 2000.0)
    ]

    def select(self, required_tops: float = 0.0, needs_ethernet: bool = False, preferred: str | None = None) -> CompanionComputer:
        if preferred:
            for cc in self._database:
                if cc.name.lower() == preferred.lower():
                    return cc

        candidates = [
            cc for cc in self._database 
            if cc.tops >= required_tops 
            and (not needs_ethernet or "Ethernet" in cc.interfaces)
        ]

        if not candidates:
            return self._database[-1] # Custom CC fallback
            
        candidates.sort(key=lambda x: (x.weight_kg, x.power_draw_watts))
        return candidates[0]
