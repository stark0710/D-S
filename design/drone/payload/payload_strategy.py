"""
PayloadStrategy Subsystem

Purpose:
    Defines the abstract `PayloadStrategy` interface and concrete multirotor payload integration strategies.

Role in Architecture:
    `PayloadStrategy` implements the Strategy Pattern to compute payload profiles, mechanical mounting solutions,
    electrical interfaces, power analysis, CG balance, and vibration isolation according to mission priorities
    (Balanced, Mapping, Inspection, Delivery, Agriculture, Research, Surveillance).
"""

from abc import ABC, abstractmethod
from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_result import ConfigurationResult
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.avionics.avionics_result import AvionicsResult
from backend.design.drone.payload.payload_profile import PayloadProfile
from backend.design.drone.payload.payload_mount import PayloadMount
from backend.design.drone.payload.payload_interface import PayloadInterface
from backend.design.drone.payload.payload_result import PayloadResult
from backend.design.drone.payload.payload_power_analysis import PayloadPowerAnalysis
from backend.design.drone.payload.payload_balance_analysis import PayloadBalanceAnalysis
from backend.design.drone.payload.payload_vibration_analysis import PayloadVibrationAnalysis
from backend.design.drone.payload.payload_selector import PayloadSelector


class PayloadStrategy(ABC):
    """
    Abstract interface for multirotor payload integration strategies.
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Unique identifier name of the strategy."""
        pass

    @abstractmethod
    def calculate_payload(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult
    ) -> PayloadResult:
        """
        Calculates complete PayloadResult for a multirotor UAV.

        Args:
            mission (DroneMissionProfile): Mission profile.
            configuration_result (ConfigurationResult): Evaluated configuration result.
            structure_result (FrameResult): Evaluated structural frame result.
            propulsion_result (PropulsionResult): Evaluated propulsion result.
            electrical_result (ElectricalResult): Evaluated electrical result.
            avionics_result (AvionicsResult): Evaluated avionics result.

        Returns:
            PayloadResult: Completed payload engineering output summary.
        """
        pass


class BalancedStrategy(PayloadStrategy):
    """Standard balanced multirotor payload integration strategy."""

    @property
    def strategy_name(self) -> str:
        return "BalancedStrategy"

    def calculate_payload(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult
    ) -> PayloadResult:
        m_type = mission.mission_type.name if hasattr(mission.mission_type, "name") else str(mission.mission_type)

        selector = PayloadSelector()
        p_spec = selector.select_payload(m_type)

        profile = PayloadProfile(
            payload_name=p_spec["payload_name"],
            payload_type=p_spec["payload_type"],
            mass_kg=p_spec["mass_kg"],
            dimensions_mm=p_spec["dimensions_mm"],
            power_draw_w=p_spec["power_draw_w"],
            data_interface=p_spec["data_interface"],
            mounting_type=p_spec["mounting_type"]
        )

        mount = PayloadMount(
            mount_type=profile.mounting_type,
            vibration_dampers=True,
            quick_release=True,
            location="BOTTOM_CENTER",
            max_supported_mass_kg=round(profile.mass_kg * 2.0, 1),
            weight_g=120.0
        )

        iface = PayloadInterface(
            power_voltage_v=12.0,
            power_connector="XT30 / JST-XH",
            data_protocol=profile.data_interface,
            required_bandwidth_mbps=15.0
        )

        pwr_engine = PayloadPowerAnalysis()
        pwr_res = pwr_engine.analyze_power(
            payload_power_w=profile.power_draw_w,
            voltage_v=12.0,
            total_hover_power_w=electrical_result.power_budget.total_hover_power_w
        )

        bal_engine = PayloadBalanceAnalysis()
        bal_res = bal_engine.analyze_balance(
            payload_mass_kg=profile.mass_kg,
            offset_x_mm=5.0,
            offset_y_mm=0.0,
            offset_z_mm=120.0
        )

        vib_engine = PayloadVibrationAnalysis()
        vib_res = vib_engine.analyze_vibration(payload_mass_kg=profile.mass_kg, sensitive_imaging=True)

        return PayloadResult(
            selected_payload=profile,
            mounting_solution=mount,
            interface_definition=iface,
            power_analysis=pwr_res,
            balance_analysis=bal_res,
            vibration_analysis=vib_res,
            engineering_notes=f"Balanced payload integration for '{profile.payload_name}'."
        )


class MappingPayloadStrategy(PayloadStrategy):
    """Photogrammetry mapping payload integration strategy."""

    @property
    def strategy_name(self) -> str:
        return "MappingPayloadStrategy"

    def calculate_payload(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult
    ) -> PayloadResult:
        selector = PayloadSelector()
        p_spec = selector.select_payload("MAPPING")

        profile = PayloadProfile(
            payload_name=p_spec["payload_name"],
            payload_type="RGB_CAMERA",
            mass_kg=p_spec["mass_kg"],
            dimensions_mm=p_spec["dimensions_mm"],
            power_draw_w=p_spec["power_draw_w"],
            data_interface=p_spec["data_interface"],
            mounting_type=p_spec["mounting_type"]
        )

        mount = PayloadMount(
            mount_type="GIMBAL_DAMPED",
            vibration_dampers=True,
            quick_release=True,
            location="BOTTOM_CENTER",
            max_supported_mass_kg=3.0,
            weight_g=180.0
        )

        iface = PayloadInterface(
            power_voltage_v=12.0,
            power_connector="XT30",
            data_protocol="Ethernet IP / USB-C",
            required_bandwidth_mbps=50.0
        )

        pwr_engine = PayloadPowerAnalysis()
        pwr_res = pwr_engine.analyze_power(profile.power_draw_w, 12.0, electrical_result.power_budget.total_hover_power_w)

        bal_engine = PayloadBalanceAnalysis()
        bal_res = bal_engine.analyze_balance(profile.mass_kg, offset_x_mm=0.0, offset_y_mm=0.0, offset_z_mm=130.0)

        vib_engine = PayloadVibrationAnalysis()
        vib_res = vib_engine.analyze_vibration(profile.mass_kg, sensitive_imaging=True)

        return PayloadResult(
            selected_payload=profile,
            mounting_solution=mount,
            interface_definition=iface,
            power_analysis=pwr_res,
            balance_analysis=bal_res,
            vibration_analysis=vib_res,
            engineering_notes="Mapping photogrammetry payload integration with 3-axis damped gimbal."
        )
