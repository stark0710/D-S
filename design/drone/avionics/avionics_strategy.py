"""
AvionicsStrategy Subsystem

Purpose:
    Defines the abstract `AvionicsStrategy` interface and concrete multirotor avionics design strategies.

Role in Architecture:
    `AvionicsStrategy` implements the Strategy Pattern to compute flight controller, GNSS, receiver, telemetry,
    camera payload, companion computer, and auxiliary sensors according to mission priorities (Balanced, Survey, Mapping, Delivery, Inspection, Autonomous, Research, FPV).
"""

from abc import ABC, abstractmethod
from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_result import ConfigurationResult
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.avionics.avionics_result import AvionicsResult
from backend.design.drone.avionics.communication_analysis import CommunicationAnalysis
from backend.design.drone.avionics.power_analysis import AvionicsPowerAnalysis
from backend.design.drone.avionics.flight_controller_selector import FlightControllerSelector
from backend.design.drone.avionics.gps_selector import GpsSelector
from backend.design.drone.avionics.receiver_selector import ReceiverSelector
from backend.design.drone.avionics.telemetry_selector import TelemetrySelector
from backend.design.drone.avionics.camera_selector import CameraSelector
from backend.design.drone.avionics.companion_computer_selector import CompanionComputerSelector
from backend.design.drone.avionics.sensor_selector import SensorSelector


class AvionicsStrategy(ABC):
    """
    Abstract interface for multirotor avionics design strategies.
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Unique identifier name of the strategy."""
        pass

    @abstractmethod
    def calculate_avionics(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult
    ) -> AvionicsResult:
        """
        Calculates complete AvionicsResult for a multirotor UAV.

        Args:
            mission (DroneMissionProfile): Mission profile.
            configuration_result (ConfigurationResult): Evaluated configuration result.
            structure_result (FrameResult): Evaluated structural frame result.
            propulsion_result (PropulsionResult): Evaluated propulsion result.
            electrical_result (ElectricalResult): Evaluated electrical power result.

        Returns:
            AvionicsResult: Completed avionics engineering output summary.
        """
        pass


class BalancedStrategy(AvionicsStrategy):
    """Standard balanced multirotor avionics design strategy."""

    @property
    def strategy_name(self) -> str:
        return "BalancedStrategy"

    def calculate_avionics(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult
    ) -> AvionicsResult:
        m_type = mission.mission_type.name if hasattr(mission.mission_type, "name") else str(mission.mission_type)

        fc_sel = FlightControllerSelector()
        fc_spec = fc_sel.select_flight_controller(m_type, mission.required_redundancy)

        gps_sel = GpsSelector()
        gps_spec = gps_sel.select_gps(rtk_required=False)

        rx_sel = ReceiverSelector()
        rx_spec = rx_sel.select_receiver(mission.target_range_km)

        telem_sel = TelemetrySelector()
        telem_spec = telem_sel.select_telemetry(mission.target_range_km)

        cam_sel = CameraSelector()
        cam_spec = cam_sel.select_camera(m_type)

        comp_sel = CompanionComputerSelector()
        comp_spec = comp_sel.select_companion_computer(autonomous_required=False)

        sens_sel = SensorSelector()
        sensors = sens_sel.select_sensors(obstacle_avoidance=False)

        comm_engine = CommunicationAnalysis()
        comm_res = comm_engine.analyze_communication(
            rc_protocol=rx_spec["protocol"],
            telemetry_power_mw=telem_spec["tx_power_mw"],
            target_range_km=mission.target_range_km
        )

        pwr_engine = AvionicsPowerAnalysis()
        pwr_res = pwr_engine.analyze_power(fc_spec, gps_spec, telem_spec, comp_spec, cam_spec, sensors)

        nav_analysis = {
            "navigation_source": "GNSS + Dual IMU EKF3 Fusion",
            "positioning_accuracy_m": gps_spec["horizontal_precision_m"],
            "failsafe_return_to_home": True,
        }

        return AvionicsResult(
            selected_flight_controller=fc_spec,
            selected_gps=gps_spec,
            selected_receiver=rx_spec,
            selected_telemetry=telem_spec,
            selected_camera=cam_spec,
            selected_companion_computer=comp_spec,
            selected_sensors=sensors,
            communication_analysis=comm_res,
            navigation_analysis=nav_analysis,
            power_analysis=pwr_res,
            engineering_notes=f"Balanced avionics architecture using {fc_spec['flight_controller_model']} and {gps_spec['gps_model']}."
        )


class MappingStrategy(AvionicsStrategy):
    """Mapping avionics strategy featuring RTK centimeter precision GNSS and full-frame photogrammetry camera."""

    @property
    def strategy_name(self) -> str:
        return "MappingStrategy"

    def calculate_avionics(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult
    ) -> AvionicsResult:
        fc_sel = FlightControllerSelector()
        fc_spec = fc_sel.select_flight_controller("MAPPING", "SINGLE")

        gps_sel = GpsSelector()
        gps_spec = gps_sel.select_gps(rtk_required=True, dual_gnss_required=True)

        rx_sel = ReceiverSelector()
        rx_spec = rx_sel.select_receiver(mission.target_range_km)

        telem_sel = TelemetrySelector()
        telem_spec = telem_sel.select_telemetry(mission.target_range_km)

        cam_sel = CameraSelector()
        cam_spec = cam_sel.select_camera("MAPPING")

        comp_sel = CompanionComputerSelector()
        comp_spec = comp_sel.select_companion_computer(autonomous_required=False)

        sens_sel = SensorSelector()
        sensors = sens_sel.select_sensors(obstacle_avoidance=False)

        comm_engine = CommunicationAnalysis()
        comm_res = comm_engine.analyze_communication(
            rc_protocol=rx_spec["protocol"],
            telemetry_power_mw=telem_spec["tx_power_mw"],
            target_range_km=mission.target_range_km
        )

        pwr_engine = AvionicsPowerAnalysis()
        pwr_res = pwr_engine.analyze_power(fc_spec, gps_spec, telem_spec, comp_spec, cam_spec, sensors)

        nav_analysis = {
            "navigation_source": "RTK Dual GNSS Centimeter Navigation",
            "positioning_accuracy_m": 0.02,
            "failsafe_return_to_home": True,
        }

        return AvionicsResult(
            selected_flight_controller=fc_spec,
            selected_gps=gps_spec,
            selected_receiver=rx_spec,
            selected_telemetry=telem_spec,
            selected_camera=cam_spec,
            selected_companion_computer=comp_spec,
            selected_sensors=sensors,
            communication_analysis=comm_res,
            navigation_analysis=nav_analysis,
            power_analysis=pwr_res,
            engineering_notes="High precision mapping avionics architecture with RTK GNSS and Sony RX1R II camera payload."
        )


class AutonomousStrategy(AvionicsStrategy):
    """High autonomy avionics strategy featuring companion computer, obstacle radar, and optical flow."""

    @property
    def strategy_name(self) -> str:
        return "AutonomousStrategy"

    def calculate_avionics(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult
    ) -> AvionicsResult:
        fc_sel = FlightControllerSelector()
        fc_spec = fc_sel.select_flight_controller("DEFENSE", "DUAL")

        gps_sel = GpsSelector()
        gps_spec = gps_sel.select_gps(rtk_required=False)

        rx_sel = ReceiverSelector()
        rx_spec = rx_sel.select_receiver(mission.target_range_km)

        telem_sel = TelemetrySelector()
        telem_spec = telem_sel.select_telemetry(mission.target_range_km, cellular_backup=True)

        cam_sel = CameraSelector()
        cam_spec = cam_sel.select_camera("SECURITY")

        comp_sel = CompanionComputerSelector()
        comp_spec = comp_sel.select_companion_computer(autonomous_required=True, ai_vision_required=True)

        sens_sel = SensorSelector()
        sensors = sens_sel.select_sensors(obstacle_avoidance=True, indoor_hover=True)

        comm_engine = CommunicationAnalysis()
        comm_res = comm_engine.analyze_communication(
            rc_protocol=rx_spec["protocol"],
            telemetry_power_mw=telem_spec["tx_power_mw"],
            target_range_km=mission.target_range_km
        )

        pwr_engine = AvionicsPowerAnalysis()
        pwr_res = pwr_engine.analyze_power(fc_spec, gps_spec, telem_spec, comp_spec, cam_spec, sensors)

        nav_analysis = {
            "navigation_source": "Multi-Sensor Fusion (GNSS + Vision SLAM + Lidar + Radar)",
            "positioning_accuracy_m": 0.1,
            "failsafe_return_to_home": True,
        }

        return AvionicsResult(
            selected_flight_controller=fc_spec,
            selected_gps=gps_spec,
            selected_receiver=rx_spec,
            selected_telemetry=telem_spec,
            selected_camera=cam_spec,
            selected_companion_computer=comp_spec,
            selected_sensors=sensors,
            communication_analysis=comm_res,
            navigation_analysis=nav_analysis,
            power_analysis=pwr_res,
            engineering_notes="Autonomous avionics architecture featuring NVIDIA Jetson Orin Nano companion computer and 360 radar."
        )
