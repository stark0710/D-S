"""
FlightControllerSelector Subsystem

Purpose:
    Defines the `FlightControllerSelector` class responsible for selecting flight controller hardware and autopilot firmware.

Role in Architecture:
    `FlightControllerSelector` selects flight controller model (Cube Orange+, Pixhawk 6C, Matek H743),
    MCU architecture (STM32H7 / STM32F7), sensor suite (Dual/Triple IMUs), firmware ('ArduPilot Copter', 'PX4 Autopilot'),
    and UART port availability.
"""

from typing import Any


class FlightControllerSelector:
    """
    Selection service for multirotor flight controller hardware and firmware.

    Design Principles:
        - Single Responsibility Principle: Autopilot hardware, MCU class, and firmware architecture sizing only.
    """

    def select_flight_controller(
        self,
        mission_type: str,
        required_redundancy: str = "NONE"
    ) -> dict[str, Any]:
        """
        Determines optimal flight controller hardware and firmware.

        Args:
            mission_type (str): Mission type category string.
            required_redundancy (str): Required sensor redundancy ('NONE', 'SINGLE', 'DUAL', 'OCTO_DUAL_FAIL').

        Returns:
            dict[str, Any]: Selected flight controller specifications dictionary.
        """
        if required_redundancy in ("DUAL", "OCTO_DUAL_FAIL") or mission_type in ("DEFENSE", "MILITARY", "DELIVERY", "CARGO"):
            fc_model = "Cube Orange+ Dual/Triple Redundant Autopilot"
            mcu = "STM32H753 @ 480MHz"
            firmware = "ArduPilot Copter (Redundant Stack)"
            imus = 3
            uarts = 6
            weight_g = 75.0
            power_w = 3.5
        elif mission_type in ("SURVEY", "MAPPING", "AGRICULTURE", "INSPECTION"):
            fc_model = "Holybro Pixhawk 6C Autopilot"
            mcu = "STM32H743 @ 480MHz"
            firmware = "PX4 Autopilot v1.14"
            imus = 2
            uarts = 5
            weight_g = 48.0
            power_w = 2.5
        else:
            fc_model = "Matek H743-WING / SLIM Autopilot"
            mcu = "STM32H743 @ 480MHz"
            firmware = "ArduPilot Copter"
            imus = 2
            uarts = 7
            weight_g = 25.0
            power_w = 2.0

        return {
            "flight_controller_model": fc_model,
            "mcu": mcu,
            "firmware": firmware,
            "imu_count": imus,
            "available_uart_ports": uarts,
            "weight_g": weight_g,
            "power_w": power_w,
            "can_bus_supported": True,
        }
