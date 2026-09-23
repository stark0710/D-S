"""
GpsSelector Subsystem

Purpose:
    Defines the `GpsSelector` class responsible for selecting GNSS navigation systems.

Role in Architecture:
    `GpsSelector` selects GNSS modules (M9N, M10, Here3+ RTK Dual GNSS) and compass configurations.
"""

from typing import Any


class GpsSelector:
    """
    Selection service for multirotor GNSS navigation modules.

    Design Principles:
        - Single Responsibility Principle: GNSS constellation, RTK precision, and compass selection only.
    """

    def select_gps(
        self,
        rtk_required: bool = False,
        dual_gnss_required: bool = False
    ) -> dict[str, Any]:
        """
        Determines optimal GNSS navigation module specifications.

        Args:
            rtk_required (bool): True if centimeter-level RTK positioning is required.
            dual_gnss_required (bool): True if dual GNSS compass-less heading is required.

        Returns:
            dict[str, Any]: Selected GNSS specifications dictionary.
        """
        if rtk_required or dual_gnss_required:
            gps_model = "Here3+ RTK Precision Dual GNSS & Compass"
            precision_m = 0.02
            rtk = True
            weight_g = 52.0
            power_w = 1.8
        else:
            gps_model = "Matek M10-5883 u-blox M10 GNSS & Compass"
            precision_m = 1.5
            rtk = False
            weight_g = 14.0
            power_w = 0.8

        return {
            "gps_model": gps_model,
            "constellations": ["GPS", "GLONASS", "Galileo", "BeiDou"],
            "horizontal_precision_m": precision_m,
            "rtk_supported": rtk,
            "integrated_compass": True,
            "weight_g": weight_g,
            "power_w": power_w,
        }
