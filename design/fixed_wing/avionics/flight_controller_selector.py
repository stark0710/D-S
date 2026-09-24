"""
Fixed-Wing Autopilot Selector Subsystem

Purpose:
    Defines the `FlightControllerSelector` class and autopilot models database.

Role in Architecture:
    `FlightControllerSelector` maps autopilot capability requirements (IMUs, interfaces)
    to physical hardware records.
"""

from typing import List


class FlightControllerRecord:
    """Autopilot hardware description."""

    def __init__(self, name: str, weight_g: float, triple_redundant: bool, price: float, interfaces: List[str]) -> None:
        self.name = name
        self.weight_g = weight_g
        self.triple_redundant = triple_redundant
        self.price = price
        self.interfaces = interfaces


class FlightControllerSelector:
    """
    Selector class matching mission redundancy levels to autopilot hardware units.
    """

    _controllers: List[FlightControllerRecord] = [
        FlightControllerRecord("Matek H743-WING", 30, False, 120.0, ["PWM", "UART", "CAN"]),
        FlightControllerRecord("Holybro Pixhawk 6C", 45, False, 220.0, ["PWM", "UART", "CAN", "Ethernet"]),
        FlightControllerRecord("Cube Orange+", 75, True, 450.0, ["PWM", "UART", "CAN", "Ethernet", "SPI"]),
        FlightControllerRecord("Holybro Pixhawk 6X", 80, True, 490.0, ["PWM", "UART", "CAN", "Ethernet", "SPI"]),
    ]

    def select_flight_controller(self, needs_redundancy: bool, needs_ethernet: bool) -> FlightControllerRecord:
        """
        Selects the best autopilot model meeting the safety and ethernet requirements.
        """
        candidates = self._controllers
        if needs_redundancy:
            candidates = [c for c in candidates if c.triple_redundant]
        if needs_ethernet:
            candidates = [c for c in candidates if "Ethernet" in c.interfaces]

        if not candidates:
            # Fallback to Pixhawk 6X
            return self._controllers[-1]

        return min(candidates, key=lambda c: c.price)
