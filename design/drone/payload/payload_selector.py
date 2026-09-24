"""
PayloadSelector Subsystem

Purpose:
    Defines the `PayloadSelector` class responsible for selecting mission payloads across supported types.

Role in Architecture:
    `PayloadSelector` selects payload specifications for RGB Camera, Thermal Camera, LiDAR, Multispectral Camera,
    Sprayer, Delivery Box, Manipulator, Scientific Sensor, or Custom Payload.
"""

from typing import Any


class PayloadSelector:
    """
    Selection service for multirotor mission payloads.

    Design Principles:
        - Single Responsibility Principle: Payload specification and physical parameter selection only.
    """

    def select_payload(
        self,
        mission_type: str,
        custom_payload_spec: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Determines optimal mission payload specification.

        Args:
            mission_type (str): Mission category type string.
            custom_payload_spec (dict[str, Any] | None): Optional custom payload specification override.

        Returns:
            dict[str, Any]: Selected payload specifications dictionary.
        """
        if custom_payload_spec is not None:
            return {
                "payload_name": custom_payload_spec.get("name", "Custom Payload Module"),
                "payload_type": "CUSTOM",
                "mass_kg": custom_payload_spec.get("mass_kg", 1.5),
                "dimensions_mm": custom_payload_spec.get("dimensions_mm", (150.0, 150.0, 150.0)),
                "power_draw_w": custom_payload_spec.get("power_draw_w", 12.0),
                "data_interface": custom_payload_spec.get("data_interface", "USB-C / UART"),
                "mounting_type": custom_payload_spec.get("mounting_type", "QUICK_RELEASE_RAIL"),
            }

        if mission_type in ("MAPPING", "SURVEY"):
            return {
                "payload_name": "Full-Frame 42MP Photogrammetry Mapping Payload",
                "payload_type": "RGB_CAMERA",
                "mass_kg": 1.2,
                "dimensions_mm": (180.0, 140.0, 160.0),
                "power_draw_w": 8.0,
                "data_interface": "USB-C / Ethernet IP",
                "mounting_type": "GIMBAL_DAMPED",
            }
        elif mission_type == "LIDAR":
            return {
                "payload_name": "High-Precision Aerial Survey LiDAR Scanner",
                "payload_type": "LIDAR",
                "mass_kg": 2.5,
                "dimensions_mm": (220.0, 180.0, 190.0),
                "power_draw_w": 25.0,
                "data_interface": "Ethernet IP / MAVLink",
                "mounting_type": "QUICK_RELEASE_RAIL",
            }
        elif mission_type == "AGRICULTURE":
            return {
                "payload_name": "10-Liter Precision Spray Tank & Pump Payload",
                "payload_type": "SPRAYER",
                "mass_kg": 10.5,
                "dimensions_mm": (400.0, 350.0, 300.0),
                "power_draw_w": 35.0,
                "data_interface": "CAN Bus / PWM",
                "mounting_type": "BOTTOM_PLATE_BOLTS",
            }
        elif mission_type in ("DELIVERY", "CARGO"):
            return {
                "payload_name": "Cargo Delivery Box & Winch Release Payload",
                "payload_type": "DELIVERY_BOX",
                "mass_kg": 5.0,
                "dimensions_mm": (300.0, 250.0, 250.0),
                "power_draw_w": 15.0,
                "data_interface": "MAVLink / PWM",
                "mounting_type": "QUICK_RELEASE_RAIL",
            }
        elif mission_type in ("INSPECTION", "SECURITY", "MILITARY"):
            return {
                "payload_name": "Dual EO/IR Thermal & Optical Gimbal Camera",
                "payload_type": "THERMAL_CAMERA",
                "mass_kg": 0.8,
                "dimensions_mm": (140.0, 120.0, 150.0),
                "power_draw_w": 10.0,
                "data_interface": "HDMI / Ethernet IP",
                "mounting_type": "GIMBAL_DAMPED",
            }
        else:
            return {
                "payload_name": "Standard RGB Mission Camera Payload",
                "payload_type": "RGB_CAMERA",
                "mass_kg": 0.4,
                "dimensions_mm": (100.0, 80.0, 90.0),
                "power_draw_w": 4.0,
                "data_interface": "UART / IP Video",
                "mounting_type": "GIMBAL_DAMPED",
            }
