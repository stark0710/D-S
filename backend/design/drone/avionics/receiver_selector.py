"""
ReceiverSelector Subsystem

Purpose:
    Defines the `ReceiverSelector` class responsible for selecting RC control link receivers.

Role in Architecture:
    `ReceiverSelector` selects RC protocol (ExpressLRS, TBS Crossfire, SBUS) and operating frequency (2.4GHz / 900MHz).
"""

from typing import Any


class ReceiverSelector:
    """
    Selection service for RC control receivers.

    Design Principles:
        - Single Responsibility Principle: RC control protocol, frequency, and telemetry feedback link selection only.
    """

    def select_receiver(self, target_range_km: float = 10.0) -> dict[str, Any]:
        """
        Determines optimal RC receiver.

        Args:
            target_range_km (float): Mission target operational range in km.

        Returns:
            dict[str, Any]: Selected receiver specifications dictionary.
        """
        if target_range_km > 15.0:
            rx_model = "TBS Crossfire Nano RX Pro 900MHz"
            freq = "915MHz / 868MHz"
            protocol = "CRSF"
            weight_g = 4.5
        elif target_range_km > 5.0:
            rx_model = "RadioMaster RP3 ExpressLRS 900MHz Diversity RX"
            freq = "900MHz"
            protocol = "CRSF / ExpressLRS"
            weight_g = 4.6
        else:
            rx_model = "RadioMaster RP1 ExpressLRS 2.4GHz RX"
            freq = "2.4GHz"
            protocol = "CRSF / ExpressLRS"
            weight_g = 2.2

        return {
            "receiver_model": rx_model,
            "frequency_band": freq,
            "protocol": protocol,
            "diversity_antennas": True,
            "weight_g": weight_g,
            "power_w": 0.5,
        }
