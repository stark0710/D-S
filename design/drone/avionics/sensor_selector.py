"""
SensorSelector Subsystem

Purpose:
    Defines the `SensorSelector` class responsible for selecting auxiliary navigation sensors.

Role in Architecture:
    `SensorSelector` selects optical flow cameras, lidar rangefinders, millimeter-wave obstacle radars,
    and precision barometers.
"""

from typing import Any


class SensorSelector:
    """
    Selection service for auxiliary navigation sensors.

    Design Principles:
        - Single Responsibility Principle: Auxiliary navigation, altimetry, and obstacle detection sensor selection only.
    """

    def select_sensors(
        self,
        obstacle_avoidance: bool = False,
        indoor_hover: bool = False
    ) -> list[dict[str, Any]]:
        """
        Determines auxiliary sensors list.

        Args:
            obstacle_avoidance (bool): True if 360 obstacle detection is required.
            indoor_hover (bool): True if non-GPS optical flow indoor positioning is required.

        Returns:
            list[dict[str, Any]]: Selected sensors list.
        """
        sensors: list[dict[str, Any]] = []

        # Precision Lidar Rangefinder for terrain following / precision landing
        sensors.append({
            "sensor_type": "RANGEFINDER",
            "sensor_model": "Benewake TFmini Plus Micro Lidar Rangefinder (12m)",
            "update_rate_hz": 100,
            "weight_g": 11.0,
            "power_w": 0.55,
        })

        if indoor_hover:
            sensors.append({
                "sensor_type": "OPTICAL_FLOW",
                "sensor_model": "HereFlow Optical Flow & Lidar Distance Sensor",
                "interface": "CAN Bus",
                "weight_g": 15.0,
                "power_w": 0.8,
            })

        if obstacle_avoidance:
            sensors.append({
                "sensor_type": "OBSTACLE_RADAR",
                "sensor_model": "77GHz Millimeter-Wave 360 Obstacle Avoidance Radar",
                "detection_range_m": 30.0,
                "weight_g": 65.0,
                "power_w": 2.5,
            })

        return sensors
