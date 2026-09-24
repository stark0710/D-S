from abc import ABC, abstractmethod
from typing import List

from .avionics_requirements import AvionicsRequirements
from .avionics_profile import AvionicsProfile
from .flight_controller_selector import FlightControllerSelector, FlightController
from .companion_computer import CompanionComputerSelector, CompanionComputer
from .sensor_suite import SensorSuite
from .navigation_system import NavigationSystem
from .communication_system import CommunicationSystem
from .flight_mode_manager import FlightModeManager
from .autonomy_stack import AutonomyStack
from .health_monitor import HealthMonitor
from .redundancy_manager import RedundancyAnalysis
from .time_synchronization import TimeSynchronization
from .avionics_analysis import AvionicsAnalysis
from .avionics_result import AvionicsResult

class AvionicsStrategy(ABC):
    @abstractmethod
    def design_avionics(self, reqs: AvionicsRequirements, profile: AvionicsProfile) -> AvionicsResult:
        pass

    def _estimate_analysis(
        self,
        fc: FlightController,
        cc: CompanionComputer,
        sensors: SensorSuite,
        comms: CommunicationSystem,
        autonomy: AutonomyStack,
        redundancy: RedundancyAnalysis,
        profile: AvionicsProfile
    ) -> AvionicsAnalysis:
        total_power = fc.power_draw_watts + cc.power_draw_watts + sensors.total_power_watts + comms.total_power_watts
        
        cpu_load = profile.baseline_cpu_stabilization_pct
        if comms.telemetry_redundancy:
            cpu_load += profile.serial_telemetry_cpu_load_pct
        if sensors.gnss_receiver_type in ["RTK", "Dual RTK"]:
            cpu_load += profile.rtk_gps_cpu_load_pct
        if autonomy.vision_based_navigation_active:
            cpu_load += profile.visual_nav_cpu_load_pct
        if autonomy.obstacle_avoidance_active:
            cpu_load += profile.obstacle_avoidance_cpu_load_pct
            
        mem_used = profile.memory_baseline_mb
        if sensors.gnss_receiver_type in ["RTK", "Dual RTK"]:
            mem_used += profile.memory_rtk_mb
        if autonomy.vision_based_navigation_active:
            mem_used += profile.memory_vision_mb
        if autonomy.obstacle_avoidance_active:
            mem_used += profile.memory_obstacle_avoidance_mb
            
        total_ram = fc.ram_mb
        if cc.name != "None":
            total_ram += cc.ram_mb
        mem_utilization_pct = min(99.0, (mem_used / total_ram) * 100.0) if total_ram > 0 else 0.0

        autonomy_score = autonomy.autonomy_level / 5.0
        
        reliability = 0.85
        if redundancy.flight_controller_redundancy == "Triple":
            reliability += 0.08
        elif redundancy.flight_controller_redundancy == "Dual":
            reliability += 0.04
        if redundancy.dual_gps_active:
            reliability += 0.03
        if redundancy.can_bus_redundancy:
            reliability += 0.02
        reliability = min(0.99, reliability)
        
        fault_tolerance = redundancy.hardware_fault_tolerance_level / 2.0
        maintainability = 0.90 - (0.05 * redundancy.hardware_fault_tolerance_level)
        
        nav_rating = 5.0
        if sensors.gnss_receiver_type == "RTK":
            nav_rating += 3.0
        elif sensors.gnss_receiver_type == "Dual RTK":
            nav_rating += 4.0
        if autonomy.vision_based_navigation_active:
            nav_rating += 1.0
        nav_rating = min(10.0, nav_rating)

        bus_util = 25.0
        if autonomy.vision_based_navigation_active:
            bus_util += 30.0
        if comms.has_video_link:
            bus_util += 20.0
        bus_util = min(95.0, bus_util)

        return AvionicsAnalysis(
            navigation_accuracy_rating=nav_rating,
            sensor_redundancy_level=sensors.imu_count + sensors.gnss_count,
            bus_utilization_pct=bus_util,
            cpu_utilization_pct=min(99.0, cpu_load),
            memory_utilization_pct=mem_utilization_pct,
            power_consumption_watts=total_power,
            autonomy_capability_score=autonomy_score,
            reliability_score=reliability,
            fault_tolerance_score=fault_tolerance,
            maintainability_score=maintainability
        )

class SurveyAvionicsStrategy(AvionicsStrategy):
    def design_avionics(self, reqs: AvionicsRequirements, profile: AvionicsProfile) -> AvionicsResult:
        fc = FlightControllerSelector().select(
            redundancy_level=2, preferred=reqs.preferred_flight_controller
        )
        cc = CompanionComputerSelector().select(
            required_tops=0.1, preferred=reqs.preferred_companion_computer
        )
        
        sensors = SensorSuite(
            has_gnss=True, gnss_receiver_type="RTK", gnss_count=1,
            has_imu=True, imu_count=2,
            has_magnetometer=True, magnetometer_count=2,
            has_barometer=True, barometer_count=2,
            has_airspeed=True, airspeed_type="Pitot",
            has_rangefinder=True, rangefinder_type="Lidar",
            has_optical_flow=False,
            total_power_watts=3.5, total_weight_kg=0.15
        )
        
        nav = NavigationSystem(
            fusion_algorithm="EKF3", rtk_active=True, rtk_accuracy_m=0.02,
            vision_positioning_active=False, dead_reckoning_capable=True,
            sensor_voting_active=True, gps_heading_active=False,
            estimated_position_accuracy_m=0.02, estimated_heading_accuracy_deg=1.0
        )
        
        comms = CommunicationSystem(
            telemetry_frequency_mhz=915.0, telemetry_redundancy=False,
            has_rc_link=True, rc_frequency_mhz=433.0,
            has_video_link=False, video_frequency_ghz=0.0,
            has_satellite_link=False,
            internal_data_buses=["CAN", "UART", "I2C"],
            can_topology="Single", ethernet_topology="None",
            total_power_watts=4.0, total_weight_kg=0.08
        )
        
        autonomy = AutonomyStack(
            waypoint_navigation_active=True, obstacle_avoidance_active=False,
            precision_landing_active=True, vision_based_navigation_active=False,
            geofencing_active=True, terrain_following_active=True,
            return_to_land_failsafe=True, autonomy_level=3
        )
        
        health = HealthMonitor(
            pre_flight_checks_active=True, in_flight_sensor_voting=True,
            battery_health_monitoring=True, vibration_monitoring_active=True,
            actuator_feedback_active=False, telemetry_link_watchdog=True,
            esc_telemetry_active=True
        )
        
        redundancy = RedundancyAnalysis(
            dual_gps_active=False, sensor_voting_active=True,
            flight_controller_redundancy="Dual", power_input_redundancy=True,
            can_bus_redundancy=False, hardware_fault_tolerance_level=1,
            estimated_mttf_hours=25000.0
        )
        
        timesync = TimeSynchronization(
            synchronization_protocol="NTP", time_offset_limit_ms=5.0,
            clock_source="GPS PPS", camera_trigger_sync_active=True,
            imu_gps_pps_aligned=True
        )
        
        analysis = self._estimate_analysis(fc, cc, sensors, comms, autonomy, redundancy, profile)
        
        notes = ["Configured for high precision survey.", f"Using flight controller: {fc.name}."]
        recs = ["Deploy high accuracy base station for RTK corrections.", "Ensure RTK link signal matches telemetry coverage."]
        
        return AvionicsResult(
            flight_controller=fc, companion_computer=cc, sensor_suite=sensors,
            navigation_system=nav, communication_system=comms, autonomy_stack=autonomy,
            health_monitor=health, redundancy_analysis=redundancy,
            time_synchronization=timesync, analysis=analysis,
            engineering_notes=notes, recommendations=recs, warnings=[]
        )

class CargoAvionicsStrategy(AvionicsStrategy):
    def design_avionics(self, reqs: AvionicsRequirements, profile: AvionicsProfile) -> AvionicsResult:
        fc = FlightControllerSelector().select(
            redundancy_level=3, preferred=reqs.preferred_flight_controller
        )
        cc = CompanionComputerSelector().select(
            required_tops=0.0, preferred=reqs.preferred_companion_computer
        )
        
        sensors = SensorSuite(
            has_gnss=True, gnss_receiver_type="Dual RTK", gnss_count=2,
            has_imu=True, imu_count=3,
            has_magnetometer=True, magnetometer_count=3,
            has_barometer=True, barometer_count=2,
            has_airspeed=True, airspeed_type="Dual Pitot",
            has_rangefinder=True, rangefinder_type="Radar",
            has_optical_flow=False,
            total_power_watts=6.0, total_weight_kg=0.25
        )
        
        nav = NavigationSystem(
            fusion_algorithm="EKF3", rtk_active=True, rtk_accuracy_m=0.02,
            vision_positioning_active=False, dead_reckoning_capable=True,
            sensor_voting_active=True, gps_heading_active=True,
            estimated_position_accuracy_m=0.02, estimated_heading_accuracy_deg=0.5
        )
        
        comms = CommunicationSystem(
            telemetry_frequency_mhz=915.0, telemetry_redundancy=True,
            has_rc_link=True, rc_frequency_mhz=868.0,
            has_video_link=False, video_frequency_ghz=0.0,
            has_satellite_link=True,
            internal_data_buses=["CAN", "UART", "I2C"],
            can_topology="Dual redundant", ethernet_topology="None",
            total_power_watts=8.0, total_weight_kg=0.18
        )
        
        autonomy = AutonomyStack(
            waypoint_navigation_active=True, obstacle_avoidance_active=False,
            precision_landing_active=True, vision_based_navigation_active=False,
            geofencing_active=True, terrain_following_active=False,
            return_to_land_failsafe=True, autonomy_level=3
        )
        
        health = HealthMonitor(
            pre_flight_checks_active=True, in_flight_sensor_voting=True,
            battery_health_monitoring=True, vibration_monitoring_active=True,
            actuator_feedback_active=True, telemetry_link_watchdog=True,
            esc_telemetry_active=True
        )
        
        redundancy = RedundancyAnalysis(
            dual_gps_active=True, sensor_voting_active=True,
            flight_controller_redundancy="Triple", power_input_redundancy=True,
            can_bus_redundancy=True, hardware_fault_tolerance_level=2,
            estimated_mttf_hours=80000.0
        )
        
        timesync = TimeSynchronization(
            synchronization_protocol="NTP", time_offset_limit_ms=5.0,
            clock_source="GPS PPS", camera_trigger_sync_active=False,
            imu_gps_pps_aligned=True
        )
        
        analysis = self._estimate_analysis(fc, cc, sensors, comms, autonomy, redundancy, profile)
        
        notes = ["Designed for safety-critical cargo transport.", f"Flight controller: {fc.name}."]
        recs = ["Utilize dual CAN configurations to prevent single bus faults from loss of control."]
        
        return AvionicsResult(
            flight_controller=fc, companion_computer=cc, sensor_suite=sensors,
            navigation_system=nav, communication_system=comms, autonomy_stack=autonomy,
            health_monitor=health, redundancy_analysis=redundancy,
            time_synchronization=timesync, analysis=analysis,
            engineering_notes=notes, recommendations=recs, warnings=[]
        )

class MappingAvionicsStrategy(AvionicsStrategy):
    def design_avionics(self, reqs: AvionicsRequirements, profile: AvionicsProfile) -> AvionicsResult:
        fc = FlightControllerSelector().select(
            redundancy_level=2, preferred=reqs.preferred_flight_controller
        )
        cc = CompanionComputerSelector().select(
            required_tops=0.5, preferred=reqs.preferred_companion_computer
        )
        
        sensors = SensorSuite(
            has_gnss=True, gnss_receiver_type="Dual RTK", gnss_count=2,
            has_imu=True, imu_count=2,
            has_magnetometer=True, magnetometer_count=2,
            has_barometer=True, barometer_count=1,
            has_airspeed=True, airspeed_type="Pitot",
            has_rangefinder=True, rangefinder_type="Lidar",
            has_optical_flow=True,
            total_power_watts=5.0, total_weight_kg=0.20
        )
        
        nav = NavigationSystem(
            fusion_algorithm="EKF3", rtk_active=True, rtk_accuracy_m=0.02,
            vision_positioning_active=False, dead_reckoning_capable=True,
            sensor_voting_active=True, gps_heading_active=True,
            estimated_position_accuracy_m=0.02, estimated_heading_accuracy_deg=0.8
        )
        
        comms = CommunicationSystem(
            telemetry_frequency_mhz=915.0, telemetry_redundancy=False,
            has_rc_link=True, rc_frequency_mhz=433.0,
            has_video_link=True, video_frequency_ghz=5.8,
            has_satellite_link=False,
            internal_data_buses=["CAN", "UART", "I2C", "Ethernet"],
            can_topology="Single", ethernet_topology="Direct",
            total_power_watts=7.0, total_weight_kg=0.12
        )
        
        autonomy = AutonomyStack(
            waypoint_navigation_active=True, obstacle_avoidance_active=True,
            precision_landing_active=True, vision_based_navigation_active=False,
            geofencing_active=True, terrain_following_active=True,
            return_to_land_failsafe=True, autonomy_level=4
        )
        
        health = HealthMonitor(
            pre_flight_checks_active=True, in_flight_sensor_voting=True,
            battery_health_monitoring=True, vibration_monitoring_active=True,
            actuator_feedback_active=False, telemetry_link_watchdog=True,
            esc_telemetry_active=True
        )
        
        redundancy = RedundancyAnalysis(
            dual_gps_active=True, sensor_voting_active=True,
            flight_controller_redundancy="Dual", power_input_redundancy=True,
            can_bus_redundancy=False, hardware_fault_tolerance_level=1,
            estimated_mttf_hours=35000.0
        )
        
        timesync = TimeSynchronization(
            synchronization_protocol="NTP", time_offset_limit_ms=2.0,
            clock_source="GPS PPS", camera_trigger_sync_active=True,
            imu_gps_pps_aligned=True
        )
        
        analysis = self._estimate_analysis(fc, cc, sensors, comms, autonomy, redundancy, profile)
        
        notes = ["Mapping configuration optimized for camera geotagging sync."]
        recs = ["Sync camera shutter to GNSS PPS rising edge for sub-centimeter geotags."]
        
        return AvionicsResult(
            flight_controller=fc, companion_computer=cc, sensor_suite=sensors,
            navigation_system=nav, communication_system=comms, autonomy_stack=autonomy,
            health_monitor=health, redundancy_analysis=redundancy,
            time_synchronization=timesync, analysis=analysis,
            engineering_notes=notes, recommendations=recs, warnings=[]
        )

class LongEnduranceAvionicsStrategy(AvionicsStrategy):
    def design_avionics(self, reqs: AvionicsRequirements, profile: AvionicsProfile) -> AvionicsResult:
        fc = FlightControllerSelector().select(
            redundancy_level=2, preferred=reqs.preferred_flight_controller
        )
        cc = CompanionComputerSelector().select(
            required_tops=0.0, preferred=reqs.preferred_companion_computer
        )
        
        sensors = SensorSuite(
            has_gnss=True, gnss_receiver_type="Standard", gnss_count=1,
            has_imu=True, imu_count=2,
            has_magnetometer=True, magnetometer_count=1,
            has_barometer=True, barometer_count=1,
            has_airspeed=True, airspeed_type="Pitot",
            has_rangefinder=False, rangefinder_type="None",
            has_optical_flow=False,
            total_power_watts=1.5, total_weight_kg=0.05
        )
        
        nav = NavigationSystem(
            fusion_algorithm="EKF2", rtk_active=False, rtk_accuracy_m=1.5,
            vision_positioning_active=False, dead_reckoning_capable=True,
            sensor_voting_active=True, gps_heading_active=False,
            estimated_position_accuracy_m=1.5, estimated_heading_accuracy_deg=2.0
        )
        
        comms = CommunicationSystem(
            telemetry_frequency_mhz=915.0, telemetry_redundancy=False,
            has_rc_link=True, rc_frequency_mhz=868.0,
            has_video_link=False, video_frequency_ghz=0.0,
            has_satellite_link=False,
            internal_data_buses=["CAN", "UART", "I2C"],
            can_topology="Single", ethernet_topology="None",
            total_power_watts=3.0, total_weight_kg=0.05
        )
        
        autonomy = AutonomyStack(
            waypoint_navigation_active=True, obstacle_avoidance_active=False,
            precision_landing_active=False, vision_based_navigation_active=False,
            geofencing_active=True, terrain_following_active=False,
            return_to_land_failsafe=True, autonomy_level=2
        )
        
        health = HealthMonitor(
            pre_flight_checks_active=True, in_flight_sensor_voting=True,
            battery_health_monitoring=True, vibration_monitoring_active=False,
            actuator_feedback_active=False, telemetry_link_watchdog=True,
            esc_telemetry_active=False
        )
        
        redundancy = RedundancyAnalysis(
            dual_gps_active=False, sensor_voting_active=True,
            flight_controller_redundancy="Dual", power_input_redundancy=False,
            can_bus_redundancy=False, hardware_fault_tolerance_level=0,
            estimated_mttf_hours=15000.0
        )
        
        timesync = TimeSynchronization(
            synchronization_protocol="None", time_offset_limit_ms=10.0,
            clock_source="Autopilot RTC", camera_trigger_sync_active=False,
            imu_gps_pps_aligned=False
        )
        
        analysis = self._estimate_analysis(fc, cc, sensors, comms, autonomy, redundancy, profile)
        
        notes = ["Power optimized configuration for maximum flight time."]
        recs = ["Limit companion compute interfaces; select lightweight materials for wire harnesses."]
        
        return AvionicsResult(
            flight_controller=fc, companion_computer=cc, sensor_suite=sensors,
            navigation_system=nav, communication_system=comms, autonomy_stack=autonomy,
            health_monitor=health, redundancy_analysis=redundancy,
            time_synchronization=timesync, analysis=analysis,
            engineering_notes=notes, recommendations=recs, warnings=[]
        )

class MilitaryAvionicsStrategy(AvionicsStrategy):
    def design_avionics(self, reqs: AvionicsRequirements, profile: AvionicsProfile) -> AvionicsResult:
        fc = FlightControllerSelector().select(
            redundancy_level=3, needs_ethernet=True, preferred=reqs.preferred_flight_controller
        )
        cc = CompanionComputerSelector().select(
            required_tops=100.0, needs_ethernet=True, preferred=reqs.preferred_companion_computer
        )
        
        sensors = SensorSuite(
            has_gnss=True, gnss_receiver_type="Anti-jamming", gnss_count=2,
            has_imu=True, imu_count=3,
            has_magnetometer=True, magnetometer_count=3,
            has_barometer=True, barometer_count=3,
            has_airspeed=True, airspeed_type="Triple Pitot",
            has_rangefinder=True, rangefinder_type="Lidar",
            has_optical_flow=True,
            total_power_watts=12.0, total_weight_kg=0.50
        )
        
        nav = NavigationSystem(
            fusion_algorithm="EKF3", rtk_active=True, rtk_accuracy_m=0.02,
            vision_positioning_active=True, dead_reckoning_capable=True,
            sensor_voting_active=True, gps_heading_active=True,
            estimated_position_accuracy_m=0.02, estimated_heading_accuracy_deg=0.2
        )
        
        comms = CommunicationSystem(
            telemetry_frequency_mhz=1400.0, telemetry_redundancy=True,
            has_rc_link=True, rc_frequency_mhz=868.0,
            has_video_link=True, video_frequency_ghz=5.8,
            has_satellite_link=True,
            internal_data_buses=["CAN", "UART", "I2C", "Ethernet", "SPI"],
            can_topology="Dual redundant", ethernet_topology="Switched",
            total_power_watts=25.0, total_weight_kg=0.60
        )
        
        autonomy = AutonomyStack(
            waypoint_navigation_active=True, obstacle_avoidance_active=True,
            precision_landing_active=True, vision_based_navigation_active=True,
            geofencing_active=True, terrain_following_active=True,
            return_to_land_failsafe=True, autonomy_level=5
        )
        
        health = HealthMonitor(
            pre_flight_checks_active=True, in_flight_sensor_voting=True,
            battery_health_monitoring=True, vibration_monitoring_active=True,
            actuator_feedback_active=True, telemetry_link_watchdog=True,
            esc_telemetry_active=True
        )
        
        redundancy = RedundancyAnalysis(
            dual_gps_active=True, sensor_voting_active=True,
            flight_controller_redundancy="Triple", power_input_redundancy=True,
            can_bus_redundancy=True, hardware_fault_tolerance_level=2,
            estimated_mttf_hours=120000.0
        )
        
        timesync = TimeSynchronization(
            synchronization_protocol="PTP", time_offset_limit_ms=0.1,
            clock_source="GPS PPS", camera_trigger_sync_active=True,
            imu_gps_pps_aligned=True
        )
        
        analysis = self._estimate_analysis(fc, cc, sensors, comms, autonomy, redundancy, profile)
        
        notes = ["Tactical military avionics stack with anti-jamming and vision odometry."]
        recs = ["Enforce shield coatings on companion computer interfaces to limit EMI."]
        
        return AvionicsResult(
            flight_controller=fc, companion_computer=cc, sensor_suite=sensors,
            navigation_system=nav, communication_system=comms, autonomy_stack=autonomy,
            health_monitor=health, redundancy_analysis=redundancy,
            time_synchronization=timesync, analysis=analysis,
            engineering_notes=notes, recommendations=recs, warnings=[]
        )

class ResearchAvionicsStrategy(AvionicsStrategy):
    def design_avionics(self, reqs: AvionicsRequirements, profile: AvionicsProfile) -> AvionicsResult:
        fc = FlightControllerSelector().select(
            redundancy_level=2, preferred=reqs.preferred_flight_controller
        )
        cc = CompanionComputerSelector().select(
            required_tops=21.0, preferred=reqs.preferred_companion_computer
        )
        
        sensors = SensorSuite(
            has_gnss=True, gnss_receiver_type="RTK", gnss_count=1,
            has_imu=True, imu_count=2,
            has_magnetometer=True, magnetometer_count=2,
            has_barometer=True, barometer_count=2,
            has_airspeed=True, airspeed_type="Pitot",
            has_rangefinder=True, rangefinder_type="Radar",
            has_optical_flow=True,
            total_power_watts=8.0, total_weight_kg=0.30
        )
        
        nav = NavigationSystem(
            fusion_algorithm="EKF3", rtk_active=True, rtk_accuracy_m=0.02,
            vision_positioning_active=True, dead_reckoning_capable=True,
            sensor_voting_active=True, gps_heading_active=False,
            estimated_position_accuracy_m=0.05, estimated_heading_accuracy_deg=1.0
        )
        
        comms = CommunicationSystem(
            telemetry_frequency_mhz=915.0, telemetry_redundancy=False,
            has_rc_link=True, rc_frequency_mhz=433.0,
            has_video_link=True, video_frequency_ghz=5.8,
            has_satellite_link=False,
            internal_data_buses=["CAN", "UART", "I2C", "Ethernet", "SPI"],
            can_topology="Single", ethernet_topology="Direct",
            total_power_watts=12.0, total_weight_kg=0.25
        )
        
        autonomy = AutonomyStack(
            waypoint_navigation_active=True, obstacle_avoidance_active=True,
            precision_landing_active=True, vision_based_navigation_active=True,
            geofencing_active=True, terrain_following_active=True,
            return_to_land_failsafe=True, autonomy_level=4
        )
        
        health = HealthMonitor(
            pre_flight_checks_active=True, in_flight_sensor_voting=True,
            battery_health_monitoring=True, vibration_monitoring_active=True,
            actuator_feedback_active=True, telemetry_link_watchdog=True,
            esc_telemetry_active=True
        )
        
        redundancy = RedundancyAnalysis(
            dual_gps_active=False, sensor_voting_active=True,
            flight_controller_redundancy="Dual", power_input_redundancy=True,
            can_bus_redundancy=False, hardware_fault_tolerance_level=1,
            estimated_mttf_hours=30000.0
        )
        
        timesync = TimeSynchronization(
            synchronization_protocol="PTP", time_offset_limit_ms=0.5,
            clock_source="GPS PPS", camera_trigger_sync_active=True,
            imu_gps_pps_aligned=True
        )
        
        analysis = self._estimate_analysis(fc, cc, sensors, comms, autonomy, redundancy, profile)
        
        notes = ["Highly modular research configuration."]
        recs = ["Utilize dedicated companion processor power isolation modules."]
        
        return AvionicsResult(
            flight_controller=fc, companion_computer=cc, sensor_suite=sensors,
            navigation_system=nav, communication_system=comms, autonomy_stack=autonomy,
            health_monitor=health, redundancy_analysis=redundancy,
            time_synchronization=timesync, analysis=analysis,
            engineering_notes=notes, recommendations=recs, warnings=[]
        )

class BalancedAvionicsStrategy(AvionicsStrategy):
    def design_avionics(self, reqs: AvionicsRequirements, profile: AvionicsProfile) -> AvionicsResult:
        fc = FlightControllerSelector().select(
            redundancy_level=2, preferred=reqs.preferred_flight_controller
        )
        cc = CompanionComputerSelector().select(
            required_tops=6.0, preferred=reqs.preferred_companion_computer
        )
        
        sensors = SensorSuite(
            has_gnss=True, gnss_receiver_type="RTK", gnss_count=1,
            has_imu=True, imu_count=2,
            has_magnetometer=True, magnetometer_count=2,
            has_barometer=True, barometer_count=2,
            has_airspeed=True, airspeed_type="Pitot",
            has_rangefinder=True, rangefinder_type="Lidar",
            has_optical_flow=True,
            total_power_watts=5.0, total_weight_kg=0.20
        )
        
        nav = NavigationSystem(
            fusion_algorithm="EKF3", rtk_active=True, rtk_accuracy_m=0.02,
            vision_positioning_active=True, dead_reckoning_capable=True,
            sensor_voting_active=True, gps_heading_active=False,
            estimated_position_accuracy_m=0.05, estimated_heading_accuracy_deg=1.0
        )
        
        comms = CommunicationSystem(
            telemetry_frequency_mhz=915.0, telemetry_redundancy=False,
            has_rc_link=True, rc_frequency_mhz=433.0,
            has_video_link=True, video_frequency_ghz=5.8,
            has_satellite_link=False,
            internal_data_buses=["CAN", "UART", "I2C", "Ethernet"],
            can_topology="Single", ethernet_topology="Direct",
            total_power_watts=8.0, total_weight_kg=0.15
        )
        
        autonomy = AutonomyStack(
            waypoint_navigation_active=True, obstacle_avoidance_active=True,
            precision_landing_active=True, vision_based_navigation_active=True,
            geofencing_active=True, terrain_following_active=True,
            return_to_land_failsafe=True, autonomy_level=4
        )
        
        health = HealthMonitor(
            pre_flight_checks_active=True, in_flight_sensor_voting=True,
            battery_health_monitoring=True, vibration_monitoring_active=True,
            actuator_feedback_active=True, telemetry_link_watchdog=True,
            esc_telemetry_active=True
        )
        
        redundancy = RedundancyAnalysis(
            dual_gps_active=False, sensor_voting_active=True,
            flight_controller_redundancy="Dual", power_input_redundancy=True,
            can_bus_redundancy=False, hardware_fault_tolerance_level=1,
            estimated_mttf_hours=32000.0
        )
        
        timesync = TimeSynchronization(
            synchronization_protocol="PTP", time_offset_limit_ms=0.5,
            clock_source="GPS PPS", camera_trigger_sync_active=True,
            imu_gps_pps_aligned=True
        )
        
        analysis = self._estimate_analysis(fc, cc, sensors, comms, autonomy, redundancy, profile)
        
        notes = ["Balanced industrial/commercial flight layout."]
        recs = ["Recommended for inspection and rescue configurations."]
        
        return AvionicsResult(
            flight_controller=fc, companion_computer=cc, sensor_suite=sensors,
            navigation_system=nav, communication_system=comms, autonomy_stack=autonomy,
            health_monitor=health, redundancy_analysis=redundancy,
            time_synchronization=timesync, analysis=analysis,
            engineering_notes=notes, recommendations=recs, warnings=[]
        )
