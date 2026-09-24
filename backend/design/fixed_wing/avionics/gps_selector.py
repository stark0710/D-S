"""
Fixed-Wing GPS Selector Subsystem

Purpose:
    Defines the `GPSSelector` class and GNSS receiver models.

Role in Architecture:
    `GPSSelector` matches accuracy and navigation constraints to GNSS receivers.
"""

from typing import List


class GPSRecord:
    """GNSS receiver description."""

    def __init__(self, name: str, weight_g: float, supports_rtk: bool, supports_dual: bool, price: float) -> None:
        self.name = name
        self.weight_g = weight_g
        self.supports_rtk = supports_rtk
        self.supports_dual = supports_dual
        self.price = price


class GPSSelector:
    """
    Selector class matching navigation styles to GNSS hardware units.
    """

    _gps_units: List[GPSRecord] = [
        GPSRecord("Holybro Micro M8N", 15, False, False, 35.0),
        GPSRecord("Holybro M9N GNSS", 22, False, True, 65.0),
        GPSRecord("CubePilot Here3 RTK", 48, True, True, 250.0),
        GPSRecord("CubePilot Here4 RTK", 52, True, True, 320.0),
    ]

    def select_gps(self, needs_rtk: bool, needs_dual: bool) -> GPSRecord:
        candidates = self._gps_units
        if needs_rtk:
            candidates = [g for g in candidates if g.supports_rtk]
        if needs_dual:
            # Dual frequency or dual constellation support
            candidates = [g for g in candidates if g.supports_dual]

        if not candidates:
            return self._gps_units[-1]

        return min(candidates, key=lambda g: g.price)
