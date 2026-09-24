"""
AvionicsPowerAnalysis Subsystem

Purpose:
    Defines the `AvionicsPowerAnalysis` class and `AvionicsPowerAnalysisResult` dataclass for avionics electrical power consumption.

Role in Architecture:
    `AvionicsPowerAnalysis` aggregates power draw in Watts and mass in grams for the flight controller, GNSS, telemetry,
    companion computer, camera, and external sensors.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AvionicsPowerAnalysisResult:
    """
    Multirotor avionics subsystem power and mass breakdown model.

    Attributes:
        flight_controller_power_w (float): FC power consumption in Watts.
        gps_power_w (float): GNSS module power consumption in Watts.
        telemetry_power_w (float): Telemetry radio power consumption in Watts.
        companion_computer_power_w (float): Companion computer power consumption in Watts.
        total_avionics_power_w (float): Total avionics subsystem power draw in Watts.
        total_avionics_weight_g (float): Total avionics subsystem mass in grams.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    flight_controller_power_w: float
    gps_power_w: float
    telemetry_power_w: float
    companion_computer_power_w: float
    total_avionics_power_w: float
    total_avionics_weight_g: float
    metadata: dict[str, Any] = field(default_factory=dict)


class AvionicsPowerAnalysis:
    """
    Analysis service for avionics subsystem power and weight.

    Design Principles:
        - Single Responsibility Principle: Avionics power and mass aggregation only.
    """

    def analyze_power(
        self,
        fc_spec: dict[str, Any],
        gps_spec: dict[str, Any],
        telemetry_spec: dict[str, Any],
        companion_spec: dict[str, Any] | None = None,
        camera_spec: dict[str, Any] | None = None,
        sensors_list: list[dict[str, Any]] | None = None
    ) -> AvionicsPowerAnalysisResult:
        """
        Calculates total avionics power draw and mass.

        Args:
            fc_spec (dict[str, Any]): FC specs.
            gps_spec (dict[str, Any]): GNSS specs.
            telemetry_spec (dict[str, Any]): Telemetry specs.
            companion_spec (dict[str, Any] | None): Companion computer specs.
            camera_spec (dict[str, Any] | None): Camera specs.
            sensors_list (list[dict[str, Any]] | None): Sensors list specs.

        Returns:
            AvionicsPowerAnalysisResult: Computed power analysis output.
        """
        fc_w = fc_spec.get("power_w", 2.5)
        fc_g = fc_spec.get("weight_g", 35.0)

        gps_w = gps_spec.get("power_w", 1.2)
        gps_g = gps_spec.get("weight_g", 45.0)

        telem_w = telemetry_spec.get("power_w", 2.5)
        telem_g = telemetry_spec.get("weight_g", 25.0)

        comp_w = companion_spec.get("power_w", 0.0) if companion_spec else 0.0
        comp_g = companion_spec.get("weight_g", 0.0) if companion_spec else 0.0

        cam_w = camera_spec.get("power_w", 0.0) if camera_spec else 0.0
        cam_g = camera_spec.get("weight_g", 0.0) if camera_spec else 0.0

        sens_w = sum(s.get("power_w", 0.5) for s in (sensors_list or []))
        sens_g = sum(s.get("weight_g", 15.0) for s in (sensors_list or []))

        total_w = round(fc_w + gps_w + telem_w + comp_w + cam_w + sens_w, 1)
        total_g = round(fc_g + gps_g + telem_g + comp_g + cam_g + sens_g, 1)

        return AvionicsPowerAnalysisResult(
            flight_controller_power_w=fc_w,
            gps_power_w=gps_w,
            telemetry_power_w=telem_w,
            companion_computer_power_w=comp_w,
            total_avionics_power_w=total_w,
            total_avionics_weight_g=total_g
        )
