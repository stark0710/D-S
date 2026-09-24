"""
CameraSelector Subsystem

Purpose:
    Defines the `CameraSelector` class responsible for selecting mission camera payloads.

Role in Architecture:
    `CameraSelector` selects imaging payloads (e.g. Sony RX1R II 42MP, 4K Mapping Gimbal, FPV Micro Camera, Dual Thermal Gimbal).
"""

from typing import Any


class CameraSelector:
    """
    Selection service for camera payloads.

    Design Principles:
        - Single Responsibility Principle: Camera sensor resolution, gimbal stabilization, and imaging payload selection only.
    """

    def select_camera(self, mission_type: str) -> dict[str, Any] | None:
        """
        Determines optimal camera payload.

        Args:
            mission_type (str): Mission category string ('MAPPING', 'SURVEY', 'INSPECTION', 'SECURITY', etc.).

        Returns:
            dict[str, Any] | None: Selected camera specifications dictionary or None if not required.
        """
        if mission_type == "MAPPING":
            return {
                "camera_model": "Sony RX1R II 42MP Full-Frame Photogrammetry Camera",
                "resolution_mp": 42.0,
                "sensor_size": "Full Frame (35mm)",
                "gimbal_stabilization": "3-Axis Direct Drive Brushless Gimbal",
                "weight_g": 650.0,
                "power_w": 8.0,
            }
        elif mission_type in ("SURVEY", "INSPECTION"):
            return {
                "camera_model": "4K 20MP Survey RGB Gimbal Camera",
                "resolution_mp": 20.0,
                "sensor_size": "1-inch CMOS",
                "gimbal_stabilization": "3-Axis Gimbal",
                "weight_g": 280.0,
                "power_w": 5.0,
            }
        elif mission_type in ("SECURITY", "MILITARY", "DISASTER_RESPONSE"):
            return {
                "camera_model": "Dual Optical + Thermal EO/IR Gimbal Camera",
                "resolution_mp": 12.0,
                "thermal_resolution": "640x512 Radiometric",
                "gimbal_stabilization": "3-Axis Gimbal",
                "weight_g": 380.0,
                "power_w": 9.0,
            }
        else:
            return {
                "camera_model": "FPV Micro HD Camera",
                "resolution_mp": 2.0,
                "sensor_size": "1/1.8-inch CMOS",
                "gimbal_stabilization": "Fixed Mount",
                "weight_g": 12.0,
                "power_w": 1.5,
            }
