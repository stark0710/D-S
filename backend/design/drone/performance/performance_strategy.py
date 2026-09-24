"""
PerformanceStrategy Subsystem

Purpose:
    Defines the abstract `PerformanceStrategy` interface and concrete multirotor flight performance strategies.

Role in Architecture:
    `PerformanceStrategy` implements the Strategy Pattern to compute hover, climb, descent, cruise, stability,
    wind, energy, endurance, and range metrics according to mission priorities (Balanced, Long Endurance, Heavy Lift,
    High Performance, Survey, Inspection, Delivery).
"""

from abc import ABC, abstractmethod
from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_result import ConfigurationResult
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.avionics.avionics_result import AvionicsResult
from backend.design.drone.payload.payload_result import PayloadResult
from backend.design.drone.mass_properties.mass_result import MassResult
from backend.design.drone.performance.hover_performance import HoverPerformance
from backend.design.drone.performance.climb_performance import ClimbPerformance
from backend.design.drone.performance.descent_performance import DescentPerformance
from backend.design.drone.performance.cruise_performance import CruisePerformance
from backend.design.drone.performance.stability_analysis import StabilityAnalysis
from backend.design.drone.performance.wind_analysis import WindAnalysis
from backend.design.drone.performance.energy_analysis import EnergyAnalysis
from backend.design.drone.performance.endurance_analysis import EnduranceAnalysis
from backend.design.drone.performance.range_analysis import RangeAnalysis
from backend.design.drone.performance.performance_result import PerformanceResult


class PerformanceStrategy(ABC):
    """
    Abstract interface for multirotor flight performance strategies.
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Unique identifier name of the strategy."""
        pass

    @abstractmethod
    def calculate_performance(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult,
        payload_result: PayloadResult,
        mass_result: MassResult
    ) -> PerformanceResult:
        """
        Calculates complete PerformanceResult for a multirotor UAV.

        Args:
            mission (DroneMissionProfile): Mission profile.
            configuration_result (ConfigurationResult): Evaluated configuration result.
            structure_result (FrameResult): Evaluated structural frame result.
            propulsion_result (PropulsionResult): Evaluated propulsion result.
            electrical_result (ElectricalResult): Evaluated electrical result.
            avionics_result (AvionicsResult): Evaluated avionics result.
            payload_result (PayloadResult): Evaluated payload result.
            mass_result (MassResult): Evaluated mass properties result.

        Returns:
            PerformanceResult: Completed performance engineering output summary.
        """
        pass


class BalancedStrategy(PerformanceStrategy):
    """Standard balanced multirotor flight performance strategy."""

    @property
    def strategy_name(self) -> str:
        return "BalancedStrategy"

    def calculate_performance(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult,
        payload_result: PayloadResult,
        mass_result: MassResult
    ) -> PerformanceResult:
        rec_cfg = configuration_result.recommended_configuration.profile
        rotor_count = rec_cfg.rotor_count

        total_mass = mass_result.total_mass_kg
        actual_tw = propulsion_result.thrust_analysis.actual_thrust_to_weight_ratio
        prop_diam = propulsion_result.selected_propellers.get("diameter_inch", 13.0)

        # 1. Hover Performance
        hover_engine = HoverPerformance()
        hover_res = hover_engine.analyze_hover(
            total_mass_kg=total_mass,
            rotor_count=rotor_count,
            propeller_diameter_inch=prop_diam,
            hover_power_w=electrical_result.power_budget.total_hover_power_w,
            actual_tw_ratio=actual_tw,
            hover_throttle_percent=propulsion_result.hover_analysis.hover_throttle_percent
        )

        # 2. Cruise Performance
        cruise_engine = CruisePerformance()
        cruise_res = cruise_engine.analyze_cruise(
            total_mass_kg=total_mass,
            hover_power_w=electrical_result.power_budget.total_hover_power_w,
            max_power_w=electrical_result.power_budget.total_peak_power_w,
            target_cruise_speed_kmh=mission.cruise_speed_kmh
        )

        # 3. Climb & Descent Performance
        climb_engine = ClimbPerformance()
        climb_res = climb_engine.analyze_climb(
            total_mass_kg=total_mass,
            hover_power_w=electrical_result.power_budget.total_hover_power_w,
            max_power_w=electrical_result.power_budget.total_peak_power_w,
            actual_tw_ratio=actual_tw
        )

        descent_engine = DescentPerformance()
        descent_res = descent_engine.analyze_descent(hover_res.disk_loading_kg_m2)

        # 4. Energy Analysis
        energy_engine = EnergyAnalysis()
        energy_res = energy_engine.analyze_energy(
            capacity_mah=electrical_result.selected_battery.get("capacity_mah", 5000.0),
            nominal_voltage_v=electrical_result.voltage_analysis.nominal_voltage_v,
            hover_power_w=hover_res.hover_power_w,
            cruise_power_w=cruise_res.cruise_power_w
        )

        # 5. Endurance & Range Analysis
        endurance_engine = EnduranceAnalysis()
        endurance = endurance_engine.calculate_endurance(
            usable_energy_wh=energy_res.usable_energy_wh,
            hover_power_w=hover_res.hover_power_w,
            cruise_power_w=cruise_res.cruise_power_w,
            hover_fraction=0.30
        )

        range_engine = RangeAnalysis()
        range_km = range_engine.calculate_range(
            mission_endurance_min=endurance["mission_endurance_min"],
            cruise_speed_kmh=cruise_res.optimal_cruise_speed_kmh,
            reserve_margin_percent=20.0
        )

        # 6. Stability & Wind Analysis
        stab_engine = StabilityAnalysis()
        stab_res = stab_engine.analyze_stability(
            actual_tw_ratio=actual_tw,
            cg_offset_x_mm=mass_result.center_of_gravity.cg_x_mm,
            cg_offset_y_mm=mass_result.center_of_gravity.cg_y_mm
        )

        wind_engine = WindAnalysis()
        wind_res = wind_engine.analyze_wind(
            actual_tw_ratio=actual_tw,
            cruise_speed_kmh=cruise_res.optimal_cruise_speed_kmh,
            max_wind_speed_m_s=mission.max_wind_speed_m_s
        )

        return PerformanceResult(
            flight_time_min=endurance["mission_endurance_min"],
            max_hover_time_min=endurance["max_hover_time_min"],
            range_km=range_km,
            cruise_speed_kmh=cruise_res.optimal_cruise_speed_kmh,
            maximum_speed_kmh=cruise_res.max_horizontal_speed_kmh,
            hover_performance=hover_res,
            climb_performance=climb_res,
            descent_performance=descent_res,
            cruise_performance=cruise_res,
            stability_analysis=stab_res,
            wind_analysis=wind_res,
            energy_analysis=energy_res,
            engineering_notes=f"Balanced flight performance analysis: {endurance['mission_endurance_min']:.1f} min endurance, {range_km:.1f} km range."
        )


class LongEnduranceStrategy(PerformanceStrategy):
    """Long endurance flight performance strategy focusing on hover power reduction and range optimization."""

    @property
    def strategy_name(self) -> str:
        return "LongEnduranceStrategy"

    def calculate_performance(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult,
        payload_result: PayloadResult,
        mass_result: MassResult
    ) -> PerformanceResult:
        rec_cfg = configuration_result.recommended_configuration.profile
        rotor_count = rec_cfg.rotor_count

        total_mass = mass_result.total_mass_kg
        actual_tw = propulsion_result.thrust_analysis.actual_thrust_to_weight_ratio
        prop_diam = propulsion_result.selected_propellers.get("diameter_inch", 13.0)

        hover_engine = HoverPerformance()
        hover_res = hover_engine.analyze_hover(
            total_mass_kg=total_mass,
            rotor_count=rotor_count,
            propeller_diameter_inch=prop_diam,
            hover_power_w=electrical_result.power_budget.total_hover_power_w,
            actual_tw_ratio=actual_tw,
            hover_throttle_percent=propulsion_result.hover_analysis.hover_throttle_percent
        )

        cruise_engine = CruisePerformance()
        cruise_res = cruise_engine.analyze_cruise(
            total_mass_kg=total_mass,
            hover_power_w=electrical_result.power_budget.total_hover_power_w,
            max_power_w=electrical_result.power_budget.total_peak_power_w,
            target_cruise_speed_kmh=mission.cruise_speed_kmh
        )

        climb_engine = ClimbPerformance()
        climb_res = climb_engine.analyze_climb(total_mass, hover_res.hover_power_w, electrical_result.power_budget.total_peak_power_w, actual_tw)

        descent_engine = DescentPerformance()
        descent_res = descent_engine.analyze_descent(hover_res.disk_loading_kg_m2)

        energy_engine = EnergyAnalysis()
        energy_res = energy_engine.analyze_energy(
            capacity_mah=electrical_result.selected_battery.get("capacity_mah", 10000.0),
            nominal_voltage_v=electrical_result.voltage_analysis.nominal_voltage_v,
            hover_power_w=hover_res.hover_power_w,
            cruise_power_w=cruise_res.cruise_power_w
        )

        endurance_engine = EnduranceAnalysis()
        endurance = endurance_engine.calculate_endurance(energy_res.usable_energy_wh, hover_res.hover_power_w, cruise_res.cruise_power_w, 0.20)

        range_engine = RangeAnalysis()
        range_km = range_engine.calculate_range(endurance["mission_endurance_min"], cruise_res.optimal_cruise_speed_kmh, 15.0)

        stab_engine = StabilityAnalysis()
        stab_res = stab_engine.analyze_stability(actual_tw, mass_result.center_of_gravity.cg_x_mm, mass_result.center_of_gravity.cg_y_mm)

        wind_engine = WindAnalysis()
        wind_res = wind_engine.analyze_wind(actual_tw, cruise_res.optimal_cruise_speed_kmh, mission.max_wind_speed_m_s)

        return PerformanceResult(
            flight_time_min=endurance["mission_endurance_min"],
            max_hover_time_min=endurance["max_hover_time_min"],
            range_km=range_km,
            cruise_speed_kmh=cruise_res.optimal_cruise_speed_kmh,
            maximum_speed_kmh=cruise_res.max_horizontal_speed_kmh,
            hover_performance=hover_res,
            climb_performance=climb_res,
            descent_performance=descent_res,
            cruise_performance=cruise_res,
            stability_analysis=stab_res,
            wind_analysis=wind_res,
            energy_analysis=energy_res,
            engineering_notes=f"Long endurance performance strategy: {endurance['mission_endurance_min']:.1f} min flight time."
        )
