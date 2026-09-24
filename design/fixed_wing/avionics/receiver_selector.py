"""
Fixed-Wing RC Receiver Selector Subsystem

Purpose:
    Defines the `ReceiverSelector` class and RC receiver models.

Role in Architecture:
    `ReceiverSelector` matches RC ranges to receivers.
"""

from typing import List


class ReceiverRecord:
    """RC receiver description."""

    def __init__(self, name: str, weight_g: float, protocol: str, typical_range_km: float, frequency_mhz: float) -> None:
        self.name = name
        self.weight_g = weight_g
        self.protocol = protocol
        self.typical_range_km = typical_range_km
        self.frequency_mhz = frequency_mhz


class ReceiverSelector:
    """
    Selector class matching control ranges to RC hardware units.
    """

    _receivers: List[ReceiverRecord] = [
        ReceiverRecord("FrSky Archer RS", 3, "SBUS", 2.0, 2400.0),
        ReceiverRecord("ExpressLRS 2.4G RX", 5, "CRSF", 8.0, 2400.0),
        ReceiverRecord("ExpressLRS 915M RX", 7, "CRSF", 25.0, 915.0),
        ReceiverRecord("TBS Crossfire Nano RX", 8, "CRSF", 40.0, 915.0),
    ]

    def select_receiver(self, target_range_km: float) -> ReceiverRecord:
        candidates = [r for r in self._receivers if r.typical_range_km >= target_range_km]
        if not candidates:
            return self._receivers[-1]  # TBS Crossfire
        return min(candidates, key=lambda r: r.weight_g)
