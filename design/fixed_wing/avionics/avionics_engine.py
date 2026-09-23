"""
Fixed-Wing Avionics Engine Subsystem

Purpose:
    Defines the `AvionicsEngine` class, which serves as the orchestrator for the Avionics Engineering Framework.

Role in Architecture:
    `AvionicsEngine` coordinates the flight controller selection, GNSS receivers, telemetry modems,
    companion computers, sensor packages, and validation rules.
"""

from typing import List, Dict, Any
from datetime import datetime

from backend.design.fixed_wing.avionics.avionics_requirements import AvionicsRequirements, AutopilotFirmware, GNSSConfiguration
from backend.design.fixed_wing.avionics.avionics_profile import AvionicsProfile
from backend.design.fixed_wing.avionics.avionics_constraints import AvionicsConstraints
from backend.design.fixed_wing.avionics.avionics_result import AvionicsResult
from backend.design.fixed_wing.avionics.avionics_validator import AvionicsValidator
from backend.design.fixed_wing.avionics.avionics_registry import AvionicsStrategyRegistry
from backend.design.fixed_wing.avionics.flight_controller_selector import FlightControllerSelector
from backend.design.fixed_wing.avionics.gps_selector import GPSSelector
from backend.design.fixed_wing.avionics.receiver_selector import ReceiverSelector
from backend.design.fixed_wing.avionics.telemetry_selector import TelemetrySelector
from backend.design.fixed_wing.avionics.companion_computer_selector import CompanionComputerSelector
from backend.design.fixed_wing.avionics.sensor_selector import SensorSelector
from backend.design.fixed_wing.avionics.navigation_analysis import NavigationAnalysis
from backend.design.fixed_wing.avionics.communication_analysis import CommunicationAnalysis
from backend.design.fixed_wing.avionics.power_analysis import PowerAnalysis


class AvionicsEngine:
    """
    Facade class managing the autopilot payload selection and power analysis pipeline.
    """

    def __init__(
        self,
        fc_selector: FlightControllerSelector | None = None,
        gps_selector: GPSSelector | None = None,
        rx_selector: ReceiverSelector | None = None,
        telem_selector: TelemetrySelector | None = None,
        comp_selector: CompanionComputerSelector | None = None,
        sensor_selector: SensorSelector | None = None,
        validator: AvionicsValidator | None = None,
    ) -> None:
        self._fc_selector = fc_selector if fc_selector else FlightControllerSelector()
        self._gps_selector = gps_selector if gps_selector else GPSSelector()
        self._rx_selector = rx_selector if rx_selector else ReceiverSelector()
        self._telem_selector = telem_selector if telem_selector else TelemetrySelector()
        self._comp_selector = comp_selector if comp_selector else CompanionComputerSelector()
        self._sensor_selector = sensor_selector if sensor_selector else SensorSelector()
        self._validator = validator if validator else AvionicsValidator()

    def process_avionics_design(
        self,
        requirements: AvionicsRequirements,
        profile: AvionicsProfile | None = None,
    ) -> AvionicsResult:
        """
        Sizes and validates the flight control, navigation, telemetry, and sensor systems.

        Args:
            requirements (AvionicsRequirements): Sizing requirements context.
            profile (AvionicsProfile | None): Safety configurations.

        Returns:
            AvionicsResult: Sized avionics payload, communication range, and power draws.
        """
        if profile is None:
            profile = AvionicsProfile()

        m_profile = requirements.mission_result.mission_profile
        category = m_profile.mission_category

        # 1. Fetch matching strategy from registry
        strategy_name = category.value if hasattr(category, 'value') else str(category)
        strategy = AvionicsStrategyRegistry.get(strategy_name)

        # 2. Extract telemetry range target
        range_target_km = m_profile.mission_range_km
        
        # Define constraints
        constraints = AvionicsConstraints(
            allowed_controllers=["Holybro Pixhawk 6X", "Holybro Pixhawk 6C", "Cube Orange+", "Matek H743-WING"],
            min_comms_range_km=range_target_km,
            required_gnss_count=profile.min_redundancy_level,
        )

        # 3. Select flight controller and firmware
        needs_redundancy = "Cargo" in strategy.name or "BVLOS" in strategy.name
        needs_visual_nav, needs_high_ai = strategy.needs_companion_computer()
        
        fc_record = self._fc_selector.select_flight_controller(
            needs_redundancy=needs_redundancy,
            needs_ethernet=needs_visual_nav,
        )
        _, firmware = strategy.select_autopilot(requirements)

        # 4. Select navigation configuration
        gnss_config, gnss_count = strategy.select_navigation(requirements)
        needs_rtk = gnss_config == GNSSConfiguration.RTK_GNSS
        gps_record = self._gps_selector.select_gps(needs_rtk=needs_rtk, needs_dual=gnss_count > 1)

        # 5. Select RC Receiver
        rx_record = self._rx_selector.select_receiver(target_range_km=range_target_km)

        # 6. Select Telemetry Modem
        _, needs_video = strategy.get_communication_targets()
        telemetry_record = self._telem_selector.select_telemetry(
            target_range_km=range_target_km, needs_video=needs_video
        )

        # 7. Select Companion Computer
        comp_record = self._comp_selector.select_companion_computer(
            needs_visual_nav=needs_visual_nav, needs_high_ai=needs_high_ai
        )

        # 8. Select Mission Sensors
        sensors_list = self._sensor_selector.select_sensors(strategy.name)

        # 9. Perform detailed performance analysis
        # Autopilot CPU load estimation
        cpu_load = 15.0  # baseline flight stabilization CPU usage
        if needs_visual_nav:
            cpu_load += 10.0  # serial Mavlink handling
        if needs_rtk:
            cpu_load += 8.0   # RTK corrections processing
        cpu_load += len(sensors_list) * 2.0

        nav_analysis = NavigationAnalysis(
            gnss_type=gnss_config.value if hasattr(gnss_config, 'value') else str(gnss_config),
            redundancy_level=gnss_count,
            waypoint_mission_support=True,
            visual_navigation_capable=needs_visual_nav,
            estimated_cpu_load_pct=round(cpu_load, 1),
            metadata={"selected_gps": gps_record.name, "autopilot_weight_g": fc_record.weight_g},
        )

        # Communication Link Budget
        comm_analysis = CommunicationAnalysis(
            max_range_km=telemetry_record.max_range_km,
            bandwidth_kbps=telemetry_record.max_bandwidth_kbps,
            redundancy_enabled=rx_record.typical_range_km >= range_target_km,
            failsafe_trigger_delay_s=15.0 if "BVLOS" in strategy.name else 5.0,
            metadata={"rc_receiver": rx_record.name, "rc_link_range_km": rx_record.typical_range_km},
        )

        # Power load analysis (BEC loads)
        # Sized continuous power: FC = 1.5W, GNSS = 0.5W, Rx = 0.1W, Telemetry = 1.0W
        watts_fc = 1.5 + (0.5 * gnss_count) + 0.1 + telemetry_record.power_w
        watts_comp = comp_record.power_w if comp_record else 0.0
        watts_sensors = sum(s.power_w for s in sensors_list)

        continuous_power = watts_fc + watts_comp + watts_sensors
        peak_power = continuous_power + 1.5  # peak telemetry burst draw

        # Pixhawk and Cube Pilot support dual BEC power inputs
        bec_backup = fc_record.triple_redundant

        pow_analysis = PowerAnalysis(
            continuous_power_w=round(continuous_power, 2),
            peak_power_w=round(peak_power, 2),
            backup_power_supported=bec_backup,
            current_draw_5v_a=round(continuous_power / 5.0, 2),
            metadata={
                "autopilot_power_w": round(watts_fc, 2),
                "companion_power_w": round(watts_comp, 2),
                "sensors_power_w": round(watts_sensors, 2),
            }
        )

        # 10. Validate sized avionics
        comp_name = comp_record.name if comp_record else "None"
        sensors_names = [s.name for s in sensors_list]

        warnings = self._validator.validate(
            requirements=requirements,
            constraints=constraints,
            selected_fc=fc_record.name,
            selected_sensors=sensors_names,
            selected_comp=comp_name,
            nav_anal=nav_analysis,
            comm_anal=comm_analysis,
            pow_anal=pow_analysis,
        )

        # 11. Compile notes and recommendations
        engineering_notes = [
            f"Avionics strategy: {strategy.name}.",
            f"Selected Autopilot: {fc_record.name} running {firmware.value}.",
            f"GNSS configuration: {gnss_config.value} ({gps_record.name}).",
            f"Companion Computer: {comp_name}.",
            f"Telemetry link: {telemetry_record.name} (max range: {telemetry_record.max_range_km} km).",
            f"Total continuous power: {continuous_power:.2f} W, current draw: {pow_analysis.current_draw_5v_a:.2f} A at 5V.",
        ]
        
        recommendations = strategy.get_recommendations()

        metadata = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.name,
        }

        # 12. Return compiled AvionicsResult
        return AvionicsResult(
            selected_flight_controller=fc_record.name,
            selected_firmware=firmware.value,
            selected_navigation_system=gnss_config.value,
            selected_receiver=rx_record.name,
            selected_telemetry=telemetry_record.name,
            selected_companion_computer=comp_name,
            selected_sensors=sensors_names,
            navigation_analysis=nav_analysis,
            communication_analysis=comm_analysis,
            power_analysis=pow_analysis,
            engineering_notes=engineering_notes,
            recommendations=recommendations,
            warnings=warnings,
            metadata=metadata,
        )
