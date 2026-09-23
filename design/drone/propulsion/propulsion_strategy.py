"""
PropulsionStrategy Subsystem

Purpose:
    Defines the abstract `PropulsionStrategy` interface and concrete multirotor propulsion design strategies.

Role in Architecture:
    `PropulsionStrategy` implements the Strategy Pattern to compute motor, propeller, thrust, power,
    and efficiency specifications according to mission priorities (Balanced, Long Endurance, Heavy Lift, High Performance, Low Cost, Industrial).
"""

from abc import ABC, abstractmethod
from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_result import ConfigurationResult
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.propulsion.thrust_analysis import ThrustAnalysis
from backend.design.drone.propulsion.power_analysis import PowerAnalysis
from backend.design.drone.propulsion.hover_analysis import HoverAnalysis
from backend.design.drone.propulsion.efficiency_analysis import EfficiencyAnalysis
from backend.design.drone.propulsion.motor_selector import MotorSelector
from backend.design.drone.propulsion.propeller_selector import PropellerSelector


class PropulsionStrategy(ABC):
    """
    Abstract interface for multirotor propulsion design strategies.
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Unique identifier name of the strategy."""
        pass

    @abstractmethod
    def calculate_propulsion(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult
    ) -> PropulsionResult:
        """
        Calculates complete PropulsionResult for a multirotor UAV.

        Args:
            mission (DroneMissionProfile): Mission profile.
            configuration_result (ConfigurationResult): Evaluated configuration result.
            structure_result (FrameResult): Evaluated structural frame result.

        Returns:
            PropulsionResult: Completed propulsion engineering result.
        """
        pass


class BalancedStrategy(PropulsionStrategy):
    """Standard balanced multirotor propulsion design strategy."""

    @property
    def strategy_name(self) -> str:
        return "BalancedStrategy"

    def calculate_propulsion(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult
    ) -> PropulsionResult:
        rec_cfg = configuration_result.recommended_configuration.profile
        rotor_count = rec_cfg.rotor_count
        coaxial = rec_cfg.coaxial
        max_prop_clearance = structure_result.selected_frame.max_propeller_diameter_inch

        # Estimated AUW = payload + structural weight + battery estimate (~AUW = payload * 3.3)
        auw_kg = max(0.1, mission.payload_weight_kg) * 3.3

        thrust_engine = ThrustAnalysis()
        thrust_res = thrust_engine.analyze_thrust(auw_kg, rotor_count, target_tw_ratio=2.0, coaxial=coaxial)

        motor_engine = MotorSelector()
        motor_spec = motor_engine.select_motor(thrust_res.hover_thrust_per_motor_g, thrust_res.max_thrust_per_motor_g, voltage_v=22.2)

        prop_engine = PropellerSelector()
        prop_spec = prop_engine.select_propeller(motor_spec, max_allowed_diameter_inch=max_prop_clearance)

        hover_engine = HoverAnalysis()
        hover_res = hover_engine.analyze_hover(
            auw_kg=auw_kg,
            hover_thrust_per_motor_g=thrust_res.hover_thrust_per_motor_g,
            max_thrust_per_motor_g=thrust_res.max_thrust_per_motor_g,
            propeller_diameter_inch=prop_spec["diameter_inch"],
            rotor_count=rotor_count
        )

        power_engine = PowerAnalysis()
        power_res = power_engine.analyze_power(
            hover_thrust_per_motor_g=thrust_res.hover_thrust_per_motor_g,
            max_thrust_per_motor_g=thrust_res.max_thrust_per_motor_g,
            rotor_count=rotor_count,
            operating_voltage_v=22.2,
            hover_efficiency_g_w=hover_res.hover_efficiency_g_per_w
        )

        eff_engine = EfficiencyAnalysis()
        eff_res = eff_engine.analyze_efficiency(
            propeller_diameter_inch=prop_spec["diameter_inch"],
            operating_voltage_v=22.2,
            motor_kv=motor_spec["kv_rating"],
            hover_throttle_percent=hover_res.hover_throttle_percent
        )

        return PropulsionResult(
            selected_motors=motor_spec,
            selected_propellers=prop_spec,
            thrust_analysis=thrust_res,
            power_analysis=power_res,
            efficiency_analysis=eff_res,
            hover_analysis=hover_res,
            engineering_notes=f"Balanced propulsion subsystem design ({rotor_count}x {motor_spec['motor_class']} with {prop_spec['propeller_size']}\" propellers)."
        )


class LongEnduranceStrategy(PropulsionStrategy):
    """Prioritizes low KV motors and large propellers for maximum hover efficiency."""

    @property
    def strategy_name(self) -> str:
        return "LongEnduranceStrategy"

    def calculate_propulsion(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult
    ) -> PropulsionResult:
        rec_cfg = configuration_result.recommended_configuration.profile
        rotor_count = rec_cfg.rotor_count
        coaxial = rec_cfg.coaxial
        max_prop_clearance = structure_result.selected_frame.max_propeller_diameter_inch

        auw_kg = max(0.1, mission.payload_weight_kg) * 3.3

        thrust_engine = ThrustAnalysis()
        thrust_res = thrust_engine.analyze_thrust(auw_kg, rotor_count, target_tw_ratio=1.8, coaxial=coaxial)

        motor_engine = MotorSelector()
        motor_spec = motor_engine.select_motor(thrust_res.hover_thrust_per_motor_g, thrust_res.max_thrust_per_motor_g, voltage_v=22.2)

        prop_engine = PropellerSelector()
        prop_spec = prop_engine.select_propeller(motor_spec, max_allowed_diameter_inch=max_prop_clearance)

        hover_engine = HoverAnalysis()
        hover_res = hover_engine.analyze_hover(
            auw_kg=auw_kg,
            hover_thrust_per_motor_g=thrust_res.hover_thrust_per_motor_g,
            max_thrust_per_motor_g=thrust_res.max_thrust_per_motor_g,
            propeller_diameter_inch=prop_spec["diameter_inch"],
            rotor_count=rotor_count
        )

        power_engine = PowerAnalysis()
        power_res = power_engine.analyze_power(
            hover_thrust_per_motor_g=thrust_res.hover_thrust_per_motor_g,
            max_thrust_per_motor_g=thrust_res.max_thrust_per_motor_g,
            rotor_count=rotor_count,
            operating_voltage_v=22.2,
            hover_efficiency_g_w=hover_res.hover_efficiency_g_per_w
        )

        eff_engine = EfficiencyAnalysis()
        eff_res = eff_engine.analyze_efficiency(
            propeller_diameter_inch=prop_spec["diameter_inch"],
            operating_voltage_v=22.2,
            motor_kv=motor_spec["kv_rating"],
            hover_throttle_percent=hover_res.hover_throttle_percent
        )

        return PropulsionResult(
            selected_motors=motor_spec,
            selected_propellers=prop_spec,
            thrust_analysis=thrust_res,
            power_analysis=power_res,
            efficiency_analysis=eff_res,
            hover_analysis=hover_res,
            engineering_notes="Long endurance propulsion strategy optimized for high power loading (g/W) efficiency."
        )


class HeavyLiftStrategy(PropulsionStrategy):
    """Prioritizes high thrust margin (T/W = 2.5) for heavy payloads."""

    @property
    def strategy_name(self) -> str:
        return "HeavyLiftStrategy"

    def calculate_propulsion(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult
    ) -> PropulsionResult:
        rec_cfg = configuration_result.recommended_configuration.profile
        rotor_count = rec_cfg.rotor_count
        coaxial = rec_cfg.coaxial
        max_prop_clearance = structure_result.selected_frame.max_propeller_diameter_inch

        auw_kg = max(0.1, mission.payload_weight_kg) * 3.3

        thrust_engine = ThrustAnalysis()
        thrust_res = thrust_engine.analyze_thrust(auw_kg, rotor_count, target_tw_ratio=2.5, coaxial=coaxial)

        motor_engine = MotorSelector()
        motor_spec = motor_engine.select_motor(thrust_res.hover_thrust_per_motor_g, thrust_res.max_thrust_per_motor_g, voltage_v=44.4)

        prop_engine = PropellerSelector()
        prop_spec = prop_engine.select_propeller(motor_spec, max_allowed_diameter_inch=max_prop_clearance)

        hover_engine = HoverAnalysis()
        hover_res = hover_engine.analyze_hover(
            auw_kg=auw_kg,
            hover_thrust_per_motor_g=thrust_res.hover_thrust_per_motor_g,
            max_thrust_per_motor_g=thrust_res.max_thrust_per_motor_g,
            propeller_diameter_inch=prop_spec["diameter_inch"],
            rotor_count=rotor_count
        )

        power_engine = PowerAnalysis()
        power_res = power_engine.analyze_power(
            hover_thrust_per_motor_g=thrust_res.hover_thrust_per_motor_g,
            max_thrust_per_motor_g=thrust_res.max_thrust_per_motor_g,
            rotor_count=rotor_count,
            operating_voltage_v=44.4,
            hover_efficiency_g_w=hover_res.hover_efficiency_g_per_w
        )

        eff_engine = EfficiencyAnalysis()
        eff_res = eff_engine.analyze_efficiency(
            propeller_diameter_inch=prop_spec["diameter_inch"],
            operating_voltage_v=44.4,
            motor_kv=motor_spec["kv_rating"],
            hover_throttle_percent=hover_res.hover_throttle_percent
        )

        return PropulsionResult(
            selected_motors=motor_spec,
            selected_propellers=prop_spec,
            thrust_analysis=thrust_res,
            power_analysis=power_res,
            efficiency_analysis=eff_res,
            hover_analysis=hover_res,
            engineering_notes="Heavy lift propulsion strategy with elevated thrust-to-weight ratio (2.5) and 12S high-voltage operating envelope."
        )
