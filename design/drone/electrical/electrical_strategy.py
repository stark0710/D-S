"""
ElectricalStrategy Subsystem

Purpose:
    Defines the abstract `ElectricalStrategy` interface and concrete multirotor electrical design strategies.

Role in Architecture:
    `ElectricalStrategy` implements the Strategy Pattern to select battery, ESC, PDB, BEC, connector, and wiring
    specifications matching mission priorities (Balanced, Long Endurance, Heavy Lift, High Performance, Low Cost, Industrial).
"""

from abc import ABC, abstractmethod
from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_result import ConfigurationResult
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.electrical.power_budget import PowerBudget
from backend.design.drone.electrical.current_analysis import CurrentAnalysis
from backend.design.drone.electrical.voltage_analysis import VoltageAnalysis
from backend.design.drone.electrical.efficiency_analysis import EfficiencyAnalysis
from backend.design.drone.electrical.battery_selector import BatterySelector
from backend.design.drone.electrical.esc_selector import EscSelector
from backend.design.drone.electrical.pdb_selector import PdbSelector
from backend.design.drone.electrical.bec_selector import BecSelector
from backend.design.drone.electrical.connector_selector import ConnectorSelector
from backend.design.drone.electrical.wire_selector import WireSelector


class ElectricalStrategy(ABC):
    """
    Abstract interface for multirotor electrical power design strategies.
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Unique identifier name of the strategy."""
        pass

    @abstractmethod
    def calculate_electrical(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult
    ) -> ElectricalResult:
        """
        Calculates complete ElectricalResult for a multirotor UAV.

        Args:
            mission (DroneMissionProfile): Mission profile.
            configuration_result (ConfigurationResult): Evaluated configuration result.
            structure_result (FrameResult): Evaluated structural frame result.
            propulsion_result (PropulsionResult): Evaluated propulsion system result.

        Returns:
            ElectricalResult: Completed electrical engineering output summary.
        """
        pass


class BalancedStrategy(ElectricalStrategy):
    """Standard balanced multirotor electrical power design strategy."""

    @property
    def strategy_name(self) -> str:
        return "BalancedStrategy"

    def calculate_electrical(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult
    ) -> ElectricalResult:
        rec_cfg = configuration_result.recommended_configuration.profile
        rotor_count = rec_cfg.rotor_count

        power = propulsion_result.power_analysis
        operating_v = power.operating_voltage_v

        # 1. Power Budget
        budget = PowerBudget(
            propulsion_hover_power_w=power.hover_power_w,
            propulsion_peak_power_w=power.max_power_w,
            avionics_power_w=15.0,
            payload_power_w=10.0
        )

        # 2. Battery Selection (LiPo 6S/4S)
        target_endurance = mission.target_hover_time_min + mission.target_cruise_time_min
        bat_engine = BatterySelector()
        bat_spec = bat_engine.select_battery(
            voltage_v=operating_v,
            target_endurance_min=target_endurance,
            hover_power_w=budget.total_hover_power_w,
            chemistry="LiPo"
        )

        # 3. Current & Voltage Analysis
        curr_engine = CurrentAnalysis()
        curr_res = curr_engine.analyze_current(
            total_hover_power_w=budget.total_hover_power_w,
            total_peak_power_w=budget.total_peak_power_w,
            voltage_v=operating_v,
            rotor_count=rotor_count,
            battery_capacity_mah=bat_spec["capacity_mah"]
        )

        # 4. Wiring & Connectors
        wire_engine = WireSelector()
        wire_spec = wire_engine.select_wiring(curr_res.peak_current_total_a, curr_res.current_per_esc_peak_a)

        volt_engine = VoltageAnalysis()
        volt_res = volt_engine.analyze_voltage(
            cell_count_s=bat_spec["cell_count_s"],
            peak_current_a=curr_res.peak_current_total_a,
            wire_gauge_awg=wire_spec["main_battery_wire_awg"],
            chemistry="LiPo"
        )

        # 5. ESCs, PDB, BEC, Connector Selection
        esc_engine = EscSelector()
        esc_spec = esc_engine.select_escs(curr_res.current_per_esc_peak_a, bat_spec["cell_count_s"], rotor_count)

        pdb_engine = PdbSelector()
        pdb_spec = pdb_engine.select_pdb(curr_res.peak_current_total_a, bat_spec["cell_count_s"], esc_spec["topology"])

        bec_engine = BecSelector()
        bec_spec = bec_engine.select_bec(15.0, 10.0)

        conn_engine = ConnectorSelector()
        conn_spec = conn_engine.select_connectors(curr_res.peak_current_total_a)

        # 6. Endurance & Efficiency Losses
        eff_engine = EfficiencyAnalysis()
        endurance_min = eff_engine.estimate_endurance_min(
            battery_capacity_mah=bat_spec["capacity_mah"],
            nominal_voltage_v=volt_res.nominal_voltage_v,
            total_hover_power_w=budget.total_hover_power_w
        )
        losses = eff_engine.calculate_electrical_losses(curr_res.hover_current_total_a, wire_spec["main_battery_wire_awg"])

        return ElectricalResult(
            selected_battery=bat_spec,
            selected_escs=esc_spec,
            selected_pdb=pdb_spec,
            selected_bec=bec_spec,
            selected_connectors=conn_spec,
            selected_wiring=wire_spec,
            power_budget=budget,
            current_analysis=curr_res,
            voltage_analysis=volt_res,
            efficiency_analysis=losses,
            estimated_endurance_min=endurance_min,
            engineering_notes=f"Balanced electrical power subsystem design ({bat_spec['battery_model']} with {esc_spec['esc_model']})."
        )


class LongEnduranceStrategy(ElectricalStrategy):
    """Prioritizes High Energy Density Li-Ion batteries for extended endurance."""

    @property
    def strategy_name(self) -> str:
        return "LongEnduranceStrategy"

    def calculate_electrical(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult
    ) -> ElectricalResult:
        rec_cfg = configuration_result.recommended_configuration.profile
        rotor_count = rec_cfg.rotor_count

        power = propulsion_result.power_analysis
        operating_v = power.operating_voltage_v

        budget = PowerBudget(
            propulsion_hover_power_w=power.hover_power_w,
            propulsion_peak_power_w=power.max_power_w,
            avionics_power_w=12.0,
            payload_power_w=8.0
        )

        target_endurance = mission.target_hover_time_min + mission.target_cruise_time_min
        bat_engine = BatterySelector()
        bat_spec = bat_engine.select_battery(
            voltage_v=operating_v,
            target_endurance_min=target_endurance,
            hover_power_w=budget.total_hover_power_w,
            chemistry="Li-Ion"
        )

        curr_engine = CurrentAnalysis()
        curr_res = curr_engine.analyze_current(
            total_hover_power_w=budget.total_hover_power_w,
            total_peak_power_w=budget.total_peak_power_w,
            voltage_v=operating_v,
            rotor_count=rotor_count,
            battery_capacity_mah=bat_spec["capacity_mah"]
        )

        wire_engine = WireSelector()
        wire_spec = wire_engine.select_wiring(curr_res.peak_current_total_a, curr_res.current_per_esc_peak_a)

        volt_engine = VoltageAnalysis()
        volt_res = volt_engine.analyze_voltage(
            cell_count_s=bat_spec["cell_count_s"],
            peak_current_a=curr_res.peak_current_total_a,
            wire_gauge_awg=wire_spec["main_battery_wire_awg"],
            chemistry="Li-Ion"
        )

        esc_engine = EscSelector()
        esc_spec = esc_engine.select_escs(curr_res.current_per_esc_peak_a, bat_spec["cell_count_s"], rotor_count)

        pdb_engine = PdbSelector()
        pdb_spec = pdb_engine.select_pdb(curr_res.peak_current_total_a, bat_spec["cell_count_s"], esc_spec["topology"])

        bec_engine = BecSelector()
        bec_spec = bec_engine.select_bec(12.0, 8.0)

        conn_engine = ConnectorSelector()
        conn_spec = conn_engine.select_connectors(curr_res.peak_current_total_a)

        eff_engine = EfficiencyAnalysis()
        endurance_min = eff_engine.estimate_endurance_min(
            battery_capacity_mah=bat_spec["capacity_mah"],
            nominal_voltage_v=volt_res.nominal_voltage_v,
            total_hover_power_w=budget.total_hover_power_w
        )
        losses = eff_engine.calculate_electrical_losses(curr_res.hover_current_total_a, wire_spec["main_battery_wire_awg"])

        return ElectricalResult(
            selected_battery=bat_spec,
            selected_escs=esc_spec,
            selected_pdb=pdb_spec,
            selected_bec=bec_spec,
            selected_connectors=conn_spec,
            selected_wiring=wire_spec,
            power_budget=budget,
            current_analysis=curr_res,
            voltage_analysis=volt_res,
            efficiency_analysis=losses,
            estimated_endurance_min=endurance_min,
            engineering_notes="Long endurance strategy utilizing Li-Ion cell chemistry (240 Wh/kg)."
        )
