"""
Fixed-Wing Telemetry Selector Subsystem

Purpose:
    Defines the `TelemetrySelector` class and telemetry modems database.

Role in Architecture:
    `TelemetrySelector` matches data link ranges and data rates to modems.
"""

from typing import List


class TelemetryRecord:
    """Telemetry modem description."""

    def __init__(self, name: str, weight_g: float, max_range_km: float, max_bandwidth_kbps: float, power_w: float) -> None:
        self.name = name
        self.weight_g = weight_g
        self.max_range_km = max_range_km
        self.max_bandwidth_kbps = max_bandwidth_kbps
        self.power_w = power_w


class TelemetrySelector:
    """
    Selector class matching communication requirements to telemetry modems.
    """

    _telemetries: List[TelemetryRecord] = [
        TelemetryRecord("Holybro SiK 915MHz Radio", 16, 5.0, 64.0, 0.5),
        TelemetryRecord("RFDesign RFD900ux", 28, 40.0, 224.0, 1.0),
        TelemetryRecord("Microhard PMDDL2450", 45, 50.0, 3100.0, 2.5),  # High bandwidth video + telemetry
        TelemetryRecord("Silvus StreamCaster Lite", 110, 80.0, 15000.0, 6.0), # BVLOS HD Video link
    ]

    def select_telemetry(self, target_range_km: float, needs_video: bool) -> TelemetryRecord:
        candidates = self._telemetries
        if needs_video:
            candidates = [t for t in candidates if t.max_bandwidth_kbps >= 1000.0]
        
        candidates = [t for t in candidates if t.max_range_km >= target_range_km]
        if not candidates:
            max_avail_range = max(t.max_range_km for t in self._telemetries)
            if target_range_km > max_avail_range:
                raise ValueError(
                    f"COMPONENT_DATABASE_LIMITATION: Required communication range ({target_range_km:.2f} km) "
                    f"exceeds the maximum range available in the telemetry catalog ({max_avail_range:.2f} km)."
                )
            else:
                raise ValueError(
                    f"COMMUNICATION_INFEASIBLE: No telemetry modem in catalog satisfies both range ({target_range_km:.2f} km) "
                    f"and video bandwidth requirements."
                )

        return min(candidates, key=lambda t: t.weight_g)
