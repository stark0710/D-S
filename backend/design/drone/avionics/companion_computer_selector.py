"""
CompanionComputerSelector Subsystem

Purpose:
    Defines the `CompanionComputerSelector` class responsible for selecting companion onboard computing platforms.

Role in Architecture:
    `CompanionComputerSelector` selects onboard processors (Raspberry Pi 5 8GB, NVIDIA Jetson Orin Nano 8GB) for AI vision,
    SLAM navigation, obstacle avoidance, and high-level autonomy.
"""

from typing import Any


class CompanionComputerSelector:
    """
    Selection service for companion onboard computing platforms.

    Design Principles:
        - Single Responsibility Principle: Companion computer processor architecture and compute capacity selection only.
    """

    def select_companion_computer(
        self,
        autonomous_required: bool = False,
        ai_vision_required: bool = False
    ) -> dict[str, Any] | None:
        """
        Determines optimal companion computer.

        Args:
            autonomous_required (bool): True if advanced ROS/MAVROS onboard mission planning is required.
            ai_vision_required (bool): True if onboard AI object detection or SLAM is required.

        Returns:
            dict[str, Any] | None: Selected companion computer dictionary or None.
        """
        if ai_vision_required:
            return {
                "computer_model": "NVIDIA Jetson Orin Nano 8GB Developer Kit",
                "processor": "6-core ARM Cortex-A78AE + Ampere GPU (40 TOPS)",
                "ram_gb": 8,
                "os": "Ubuntu 22.04 LTS (ROS2 Humble)",
                "weight_g": 180.0,
                "power_w": 15.0,
            }
        elif autonomous_required:
            return {
                "computer_model": "Raspberry Pi 5 8GB",
                "processor": "Quad-core ARM Cortex-A76 @ 2.4GHz",
                "ram_gb": 8,
                "os": "Ubuntu 22.04 LTS (ROS2 / MAVROS)",
                "weight_g": 55.0,
                "power_w": 8.0,
            }
        return None
