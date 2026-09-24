"""
TelemetrySelector Subsystem

Purpose:
    Defines the `TelemetrySelector` class responsible for selecting telemetry data link radios.

Role in Architecture:
    `TelemetrySelector` selects telemetry radio modules (SiK 915MHz 500mW, Holybro Micro Radio, Herelink HD, 4G/5G Cellular).
"""

from typing import Any


class TelemetrySelector:
    """
    Selection service for telemetry data link radios.

    Design Principles:
        - Single Responsibility Principle: Telemetry radio link, power output, and frequency band selection only.
    """

    def select_telemetry(
        self,
        target_range_km: float = 10.0,
        cellular_backup: bool = False
    ) -> dict[str, Any]:
        """
        Determines optimal telemetry radio link specifications.

        Args:
            target_range_km (float): Mission target range in km.
            cellular_backup (bool): True if 4G/5G LTE cellular telemetry is required.

        Returns:
            dict[str, Any]: Selected telemetry radio specifications dictionary.
        """
        if cellular_backup or target_range_km > 20.0:
            telem_model = "4G LTE Cellular Telemetry Dongle & SiK 915MHz 1W"
            freq = "4G LTE & 915MHz"
            power_mw = 1000.0
            weight_g = 65.0
            power_w = 4.5
        elif target_range_km > 8.0:
            telem_model = "Holybro SiK Telemetry Radio 915MHz 500mW"
            freq = "915MHz"
            power_mw = 500.0
            weight_g = 28.0
            power_w = 2.5
        else:
            telem_model = "Holybro Micro Telemetry Radio 915MHz 250mW"
            freq = "915MHz"
            power_mw = 250.0
            weight_g = 14.0
            power_w = 1.5

        return {
            "telemetry_model": telem_model,
            "frequency_band": freq,
            "tx_power_mw": power_mw,
            "mavlink_supported": True,
            "weight_g": weight_g,
            "power_w": power_w,
        }
