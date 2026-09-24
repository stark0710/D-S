"""
VTOL Payload Selection databases
"""

from dataclasses import dataclass
from typing import List

@dataclass(slots=True)
class Payload:
    name: str
    category: str
    weight_kg: float
    width_m: float
    height_m: float
    length_m: float
    power_draw_watts: float
    voltage_volts: float
    data_bandwidth_mbps: float
    heat_dissipation_watts: float
    data_interfaces: List[str]
    cost_usd: float

class PayloadSelector:
    """
    Database and selector for sizing mission payloads.
    """
    _database: List[Payload] = [
        Payload("Sony RX1R II", "RGB Camera", 0.65, 0.11, 0.07, 0.08, 10.0, 8.4, 20.0, 8.0, ["USB3", "HDMI"], 3300.0),
        Payload("Sony Alpha Mapping", "Mapping Camera", 0.75, 0.12, 0.08, 0.09, 12.0, 8.4, 25.0, 9.0, ["USB3", "HDMI"], 4200.0),
        Payload("MicaSense RedEdge", "Multispectral Camera", 0.35, 0.09, 0.06, 0.06, 8.0, 5.0, 10.0, 5.0, ["Ethernet", "UART"], 4900.0),
        Payload("Flir Duo Pro R", "Thermal Camera", 0.32, 0.08, 0.06, 0.08, 12.0, 12.0, 15.0, 8.0, ["USB3", "HDMI", "UART"], 5500.0),
        Payload("Velodyne VLP-16", "LiDAR", 0.83, 0.10, 0.10, 0.07, 8.0, 12.0, 50.0, 8.0, ["Ethernet"], 4000.0),
        Payload("EchoDyne EchoFlight", "Radar", 0.80, 0.16, 0.08, 0.04, 20.0, 24.0, 100.0, 18.0, ["Ethernet"], 12000.0),
        Payload("Standard Delivery Box", "Delivery Box", 0.50, 0.25, 0.20, 0.20, 0.0, 0.0, 0.0, 0.0, [], 50.0),
        Payload("Heavy Cargo Pod", "Cargo Pod", 2.50, 0.40, 0.30, 0.30, 2.0, 12.0, 1.0, 0.0, ["CAN"], 350.0),
        Payload("Medical Cooler Pod", "Medical Payload", 3.00, 0.30, 0.25, 0.25, 15.0, 12.0, 2.0, 10.0, ["UART", "CAN"], 900.0),
        Payload("TeeJet Spray System", "Agricultural Sprayer", 4.50, 0.80, 0.15, 0.15, 35.0, 24.0, 2.0, 5.0, ["GPIO", "CAN"], 1200.0),
        Payload("Geotech Sensors Suite", "Scientific Instruments", 1.80, 0.20, 0.15, 0.15, 15.0, 12.0, 10.0, 12.0, ["Ethernet", "UART"], 4500.0),
        Payload("Silvus StreamCaster Relay", "Communication Relay", 1.10, 0.15, 0.10, 0.05, 30.0, 24.0, 150.0, 28.0, ["Ethernet"], 8500.0),
        Payload("Custom Payload", "Custom Payload", 1.00, 0.15, 0.15, 0.15, 15.0, 12.0, 10.0, 10.0, ["UART"], 1000.0)
    ]

    def select(self, category: str, preferred: str | None = None) -> Payload:
        if preferred:
            for p in self._database:
                if p.name.lower() == preferred.lower() or p.category.lower() == preferred.lower():
                    return p
                    
        candidates = [p for p in self._database if p.category.lower() == category.lower()]
        if not candidates:
            # Fallback search by category keyword
            candidates = [p for p in self._database if category.lower() in p.category.lower()]
            if not candidates:
                return self._database[-1]
            
        candidates.sort(key=lambda x: x.weight_kg)
        return candidates[0]
