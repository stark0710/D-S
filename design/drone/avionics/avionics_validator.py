"""
AvionicsValidator Subsystem

Purpose:
    Defines the `AvionicsValidator` class responsible for validating multirotor avionics subsystem designs against constraints.

Role in Architecture:
    `AvionicsValidator` checks total power draw, mass budgets, available hardware UART ports, IMU redundancy, and RF link margins.
"""

from backend.design.drone.avionics.avionics_result import AvionicsResult
from backend.design.drone.avionics.avionics_constraints import AvionicsConstraints


class AvionicsValidator:
    """
    Validator for multirotor avionics subsystem designs.

    Design Principles:
        - Single Responsibility Principle: Avionics architecture constraint and safety validation only.
    """

    def validate_avionics(
        self,
        result: AvionicsResult,
        constraints: AvionicsConstraints
    ) -> list[str]:
        """
        Validates an AvionicsResult against AvionicsConstraints.

        Args:
            result (AvionicsResult): Target avionics result.
            constraints (AvionicsConstraints): Avionics constraints.

        Returns:
            list[str]: List of warning messages.
        """
        warnings: list[str] = []

        total_w = result.power_analysis.total_avionics_power_w
        if total_w > constraints.max_avionics_power_w:
            warnings.append(
                f"Total avionics power draw ({total_w:.1f}W) exceeds maximum allowed budget ({constraints.max_avionics_power_w:.1f}W)."
            )

        total_g = result.power_analysis.total_avionics_weight_g
        if total_g > constraints.max_avionics_weight_g:
            warnings.append(
                f"Total avionics mass ({total_g:.0f}g) exceeds maximum allowed budget ({constraints.max_avionics_weight_g:.0f}g)."
            )

        uarts = result.selected_flight_controller.get("available_uart_ports", 4)
        if uarts < constraints.min_uart_ports:
            warnings.append(
                f"Available hardware UART ports ({uarts}) is below minimum requirement ({constraints.min_uart_ports}). Risk of peripheral port exhaustion."
            )

        if constraints.require_dual_imu and result.selected_flight_controller.get("imu_count", 1) < 2:
            warnings.append("Dual IMU sensor redundancy is required but selected flight controller has only 1 IMU.")

        if result.communication_analysis.link_margin_db < 10.0:
            warnings.append(
                f"RF communication link margin ({result.communication_analysis.link_margin_db:.1f} dB) is low (< 10 dB). High risk of signal loss at maximum range."
            )

        return warnings
