from abc import ABC, abstractmethod
from typing import List

from .payload_requirements import PayloadRequirements
from .payload_profile import PayloadProfile
from .payload_selector import PayloadSelector, Payload
from .payload_mount import PayloadMount
from .payload_bay import PayloadBay
from .payload_interfaces import PayloadInterfaces
from .payload_power import PayloadPower
from .payload_thermal import PayloadThermal
from .payload_cg import PayloadCG
from .payload_analysis import PayloadAnalysis
from .payload_result import PayloadResult

class PayloadStrategy(ABC):
    @abstractmethod
    def design_payload(self, reqs: PayloadRequirements, profile: PayloadProfile) -> PayloadResult:
        pass

    def _calculate_cg_shift(self, payload: Payload, mount: PayloadMount, reqs: PayloadRequirements) -> PayloadCG:
        # Extract base aircraft CG and mass
        try:
            mtow = reqs.mission_result.mission_analysis.estimated_mtow_kg
        except AttributeError:
            mtow = 25.0
            
        base_cg_x = 0.0
        base_cg_y = 0.0
        base_cg_z = 0.0
        
        # Sized payload weight
        total_payload_weight = payload.weight_kg + mount.weight_kg
        
        # Sized payload position relative to base CG (e.g. forward, under, or lateral)
        payload_cg_x = 0.15 # 15cm forward of base CG
        payload_cg_y = 0.0
        payload_cg_z = -0.10 # 10cm below base CG (typical camera gimbal)
        
        composite_cg_x = (base_cg_x * mtow + payload_cg_x * total_payload_weight) / (mtow + total_payload_weight)
        composite_cg_y = (base_cg_y * mtow + payload_cg_y * total_payload_weight) / (mtow + total_payload_weight)
        composite_cg_z = (base_cg_z * mtow + payload_cg_z * total_payload_weight) / (mtow + total_payload_weight)
        
        shift_x = composite_cg_x - base_cg_x
        shift_y = composite_cg_y - base_cg_y
        shift_z = composite_cg_z - base_cg_z
        
        try:
            mac = reqs.wing_result.wing_geometry.mean_aerodynamic_chord_m
        except AttributeError:
            mac = 0.40 # Default Mean Aerodynamic Chord
            
        shift_pct_mac = (shift_x / mac) * 100.0 if mac > 0 else 0.0
        
        return PayloadCG(
            payload_cg_x_m=payload_cg_x, payload_cg_y_m=payload_cg_y, payload_cg_z_m=payload_cg_z,
            aircraft_base_cg_x_m=base_cg_x, aircraft_base_cg_y_m=base_cg_y, aircraft_base_cg_z_m=base_cg_z,
            composite_cg_x_m=composite_cg_x, composite_cg_y_m=composite_cg_y, composite_cg_z_m=composite_cg_z,
            cg_shift_x_m=shift_x, cg_shift_y_m=shift_y, cg_shift_z_m=shift_z,
            cg_shift_pct_mac=shift_pct_mac
        )

    def _estimate_analysis(
        self, payload: Payload, mount: PayloadMount, bay: PayloadBay, cg: PayloadCG,
        power: PayloadPower, thermal: PayloadThermal, interfaces: PayloadInterfaces
    ) -> PayloadAnalysis:
        vol_payload = payload.width_m * payload.height_m * payload.length_m
        efficiency = (vol_payload / bay.bay_volume_m3) * 100.0 if bay.bay_volume_m3 > 0 else 0.0
        
        access = 0.90 if interfaces.maintenance_accessibility == "High" else (0.70 if interfaces.maintenance_accessibility == "Medium" else 0.40)
        
        load_ratio = (payload.weight_kg + mount.weight_kg) / bay.max_load_kg if bay.max_load_kg > 0 else 0.0
        power_ratio = (power.continuous_power_watts) / 100.0
        thermal_ratio = thermal.heat_generated_watts / 80.0
        bw_util = (interfaces.data_bandwidth_mbps / 100.0) * 100.0
        
        suitability = 0.95
        if not bay.fit_status:
            suitability -= 0.30
            
        return PayloadAnalysis(
            packaging_efficiency_pct=min(99.0, efficiency),
            accessibility_score=access,
            cg_shift_pct=abs(cg.cg_shift_pct_mac),
            structural_load_ratio=load_ratio,
            power_consumption_pct=min(99.0, power_ratio * 100.0),
            thermal_load_ratio=thermal_ratio,
            data_bandwidth_utilization_pct=min(99.0, bw_util),
            mission_suitability_score=min(1.0, suitability),
            maintainability_rating="Excellent" if access >= 0.8 else ("Good" if access >= 0.6 else "Fair")
        )

class SurveyPayloadStrategy(PayloadStrategy):
    def design_payload(self, reqs: PayloadRequirements, profile: PayloadProfile) -> PayloadResult:
        payload = PayloadSelector().select("RGB Camera", reqs.preferred_payload_type)
        
        mount = PayloadMount(
            mount_type=reqs.preferred_mount_type or "Gimbal 3-Axis",
            weight_kg=0.25, power_draw_watts=5.0,
            vibration_isolation=True, quick_release=True,
            drag_coefficient=profile.aerodynamic_drag_coefficient_gimbal
        )
        
        bay = PayloadBay(
            width_m=0.30, height_m=0.20, length_m=0.20,
            max_load_kg=5.0, bay_volume_m3=0.012,
            fit_status=(payload.width_m <= 0.30 and payload.height_m <= 0.20 and payload.length_m <= 0.20),
            clearance_x_m=0.30 - payload.width_m, clearance_y_m=0.20 - payload.height_m, clearance_z_m=0.20 - payload.length_m
        )
        
        interfaces = PayloadInterfaces(
            data_connections=payload.data_interfaces, control_protocol="Mavlink",
            maintenance_accessibility="High", data_bandwidth_mbps=payload.data_bandwidth_mbps,
            quick_release_compatible=True
        )
        
        power = PayloadPower(
            continuous_power_watts=payload.power_draw_watts + mount.power_draw_watts,
            peak_power_watts=(payload.power_draw_watts + mount.power_draw_watts) * 1.5,
            voltage_volts=payload.voltage_volts,
            required_current_amps=(payload.power_draw_watts + mount.power_draw_watts) / payload.voltage_volts if payload.voltage_volts > 0 else 0.0,
            fuse_rating_amps=3.0, power_source="BEC 12V"
        )
        
        thermal = PayloadThermal(
            heat_generated_watts=payload.heat_dissipation_watts, cooling_type="Passive",
            airflow_cfm_required=0.0, operating_temperature_max_c=60.0, cooling_margin_c=15.0
        )
        
        cg = self._calculate_cg_shift(payload, mount, reqs)
        analysis = self._estimate_analysis(payload, mount, bay, cg, power, thermal, interfaces)
        
        notes = ["Survey strategy configured with stabilizer gimbal."]
        recs = ["Calibrate gimbal IMU offsets prior to mapping sorties."]
        
        return PayloadResult(
            payload_selection=payload, payload_mount=mount, payload_bay=bay,
            payload_interfaces=interfaces, payload_power=power, payload_thermal=thermal,
            payload_cg=cg, payload_analysis=analysis,
            engineering_notes=notes, recommendations=recs, warnings=[]
        )

class CargoPayloadStrategy(PayloadStrategy):
    def design_payload(self, reqs: PayloadRequirements, profile: PayloadProfile) -> PayloadResult:
        payload = PayloadSelector().select("Cargo Pod", reqs.preferred_payload_type)
        
        mount = PayloadMount(
            mount_type=reqs.preferred_mount_type or "Cargo Rails",
            weight_kg=0.30, power_draw_watts=0.0,
            vibration_isolation=False, quick_release=True,
            drag_coefficient=profile.aerodynamic_drag_coefficient_cargo_pod
        )
        
        bay = PayloadBay(
            width_m=0.50, height_m=0.40, length_m=0.40,
            max_load_kg=15.0, bay_volume_m3=0.08,
            fit_status=(payload.width_m <= 0.50 and payload.height_m <= 0.40 and payload.length_m <= 0.40),
            clearance_x_m=0.50 - payload.width_m, clearance_y_m=0.40 - payload.height_m, clearance_z_m=0.40 - payload.length_m
        )
        
        interfaces = PayloadInterfaces(
            data_connections=payload.data_interfaces, control_protocol="GPIO",
            maintenance_accessibility="Medium", data_bandwidth_mbps=payload.data_bandwidth_mbps,
            quick_release_compatible=True
        )
        
        power = PayloadPower(
            continuous_power_watts=payload.power_draw_watts,
            peak_power_watts=payload.power_draw_watts * 2.0,
            voltage_volts=12.0,
            required_current_amps=payload.power_draw_watts / 12.0 if payload.power_draw_watts > 0 else 0.0,
            fuse_rating_amps=1.5, power_source="BEC 12V"
        )
        
        thermal = PayloadThermal(
            heat_generated_watts=0.0, cooling_type="Passive",
            airflow_cfm_required=0.0, operating_temperature_max_c=50.0, cooling_margin_c=25.0
        )
        
        cg = self._calculate_cg_shift(payload, mount, reqs)
        analysis = self._estimate_analysis(payload, mount, bay, cg, power, thermal, interfaces)
        
        notes = ["Cargo pod designed for mechanical quick release."]
        recs = ["Ensure payload release locks have safety manual overrides."]
        
        return PayloadResult(
            payload_selection=payload, payload_mount=mount, payload_bay=bay,
            payload_interfaces=interfaces, payload_power=power, payload_thermal=thermal,
            payload_cg=cg, payload_analysis=analysis,
            engineering_notes=notes, recommendations=recs, warnings=[]
        )

class MappingPayloadStrategy(PayloadStrategy):
    def design_payload(self, reqs: PayloadRequirements, profile: PayloadProfile) -> PayloadResult:
        payload = PayloadSelector().select("Mapping Camera", reqs.preferred_payload_type)
        
        mount = PayloadMount(
            mount_type=reqs.preferred_mount_type or "Gimbal 2-Axis",
            weight_kg=0.20, power_draw_watts=4.0,
            vibration_isolation=True, quick_release=True,
            drag_coefficient=profile.aerodynamic_drag_coefficient_gimbal
        )
        
        bay = PayloadBay(
            width_m=0.30, height_m=0.20, length_m=0.20,
            max_load_kg=4.0, bay_volume_m3=0.012,
            fit_status=(payload.width_m <= 0.30 and payload.height_m <= 0.20 and payload.length_m <= 0.20),
            clearance_x_m=0.30 - payload.width_m, clearance_y_m=0.20 - payload.height_m, clearance_z_m=0.20 - payload.length_m
        )
        
        interfaces = PayloadInterfaces(
            data_connections=payload.data_interfaces, control_protocol="Mavlink",
            maintenance_accessibility="High", data_bandwidth_mbps=payload.data_bandwidth_mbps,
            quick_release_compatible=True
        )
        
        power = PayloadPower(
            continuous_power_watts=payload.power_draw_watts + mount.power_draw_watts,
            peak_power_watts=(payload.power_draw_watts + mount.power_draw_watts) * 1.5,
            voltage_volts=payload.voltage_volts,
            required_current_amps=(payload.power_draw_watts + mount.power_draw_watts) / payload.voltage_volts if payload.voltage_volts > 0 else 0.0,
            fuse_rating_amps=3.0, power_source="BEC 12V"
        )
        
        thermal = PayloadThermal(
            heat_generated_watts=payload.heat_dissipation_watts, cooling_type="Passive",
            airflow_cfm_required=0.0, operating_temperature_max_c=55.0, cooling_margin_c=18.0
        )
        
        cg = self._calculate_cg_shift(payload, mount, reqs)
        analysis = self._estimate_analysis(payload, mount, bay, cg, power, thermal, interfaces)
        
        notes = ["Mapping setup configured with downward isolation frame."]
        recs = ["Integrate RTK trigger sync to align exposure triggers to GPS logs."]
        
        return PayloadResult(
            payload_selection=payload, payload_mount=mount, payload_bay=bay,
            payload_interfaces=interfaces, payload_power=power, payload_thermal=thermal,
            payload_cg=cg, payload_analysis=analysis,
            engineering_notes=notes, recommendations=recs, warnings=[]
        )

class AgriculturePayloadStrategy(PayloadStrategy):
    def design_payload(self, reqs: PayloadRequirements, profile: PayloadProfile) -> PayloadResult:
        payload = PayloadSelector().select("Agricultural Sprayer", reqs.preferred_payload_type)
        
        mount = PayloadMount(
            mount_type=reqs.preferred_mount_type or "Fixed",
            weight_kg=0.50, power_draw_watts=0.0,
            vibration_isolation=False, quick_release=False,
            drag_coefficient=0.50
        )
        
        bay = PayloadBay(
            width_m=1.00, height_m=0.30, length_m=0.30,
            max_load_kg=20.0, bay_volume_m3=0.09,
            fit_status=(payload.width_m <= 1.00 and payload.height_m <= 0.30 and payload.length_m <= 0.30),
            clearance_x_m=1.00 - payload.width_m, clearance_y_m=0.30 - payload.height_m, clearance_z_m=0.30 - payload.length_m
        )
        
        interfaces = PayloadInterfaces(
            data_connections=payload.data_interfaces, control_protocol="CAN",
            maintenance_accessibility="High", data_bandwidth_mbps=payload.data_bandwidth_mbps,
            quick_release_compatible=False
        )
        
        power = PayloadPower(
            continuous_power_watts=payload.power_draw_watts,
            peak_power_watts=payload.power_draw_watts * 1.5,
            voltage_volts=payload.voltage_volts,
            required_current_amps=payload.power_draw_watts / payload.voltage_volts if payload.voltage_volts > 0 else 0.0,
            fuse_rating_amps=5.0, power_source="Main Battery"
        )
        
        thermal = PayloadThermal(
            heat_generated_watts=payload.heat_dissipation_watts, cooling_type="Active Fan",
            airflow_cfm_required=15.0, operating_temperature_max_c=65.0, cooling_margin_c=12.0
        )
        
        cg = self._calculate_cg_shift(payload, mount, reqs)
        analysis = self._estimate_analysis(payload, mount, bay, cg, power, thermal, interfaces)
        
        notes = ["Agricultural sprayer layout sizing complete."]
        recs = ["Ensure liquid tank partitions prevent fluid slosh from shifting the dynamic CG."]
        
        return PayloadResult(
            payload_selection=payload, payload_mount=mount, payload_bay=bay,
            payload_interfaces=interfaces, payload_power=power, payload_thermal=thermal,
            payload_cg=cg, payload_analysis=analysis,
            engineering_notes=notes, recommendations=recs, warnings=[]
        )

class EmergencyPayloadStrategy(PayloadStrategy):
    def design_payload(self, reqs: PayloadRequirements, profile: PayloadProfile) -> PayloadResult:
        payload = PayloadSelector().select("Medical Payload", reqs.preferred_payload_type)
        
        mount = PayloadMount(
            mount_type=reqs.preferred_mount_type or "Gimbal 2-Axis",
            weight_kg=0.20, power_draw_watts=2.0,
            vibration_isolation=True, quick_release=True,
            drag_coefficient=profile.aerodynamic_drag_coefficient_gimbal
        )
        
        bay = PayloadBay(
            width_m=0.40, height_m=0.30, length_m=0.30,
            max_load_kg=8.0, bay_volume_m3=0.036,
            fit_status=(payload.width_m <= 0.40 and payload.height_m <= 0.30 and payload.length_m <= 0.30),
            clearance_x_m=0.40 - payload.width_m, clearance_y_m=0.30 - payload.height_m, clearance_z_m=0.30 - payload.length_m
        )
        
        interfaces = PayloadInterfaces(
            data_connections=payload.data_interfaces, control_protocol="Mavlink",
            maintenance_accessibility="High", data_bandwidth_mbps=payload.data_bandwidth_mbps,
            quick_release_compatible=True
        )
        
        power = PayloadPower(
            continuous_power_watts=payload.power_draw_watts + mount.power_draw_watts,
            peak_power_watts=(payload.power_draw_watts + mount.power_draw_watts) * 1.5,
            voltage_volts=payload.voltage_volts,
            required_current_amps=(payload.power_draw_watts + mount.power_draw_watts) / payload.voltage_volts if payload.voltage_volts > 0 else 0.0,
            fuse_rating_amps=3.0, power_source="BEC 12V"
        )
        
        thermal = PayloadThermal(
            heat_generated_watts=payload.heat_dissipation_watts, cooling_type="Active Fan",
            airflow_cfm_required=5.0, operating_temperature_max_c=50.0, cooling_margin_c=10.0
        )
        
        cg = self._calculate_cg_shift(payload, mount, reqs)
        analysis = self._estimate_analysis(payload, mount, bay, cg, power, thermal, interfaces)
        
        notes = ["Emergency response payload configured with thermal cooler support."]
        recs = ["Deploy high performance quick release locks for fast vaccine pod swap times."]
        
        return PayloadResult(
            payload_selection=payload, payload_mount=mount, payload_bay=bay,
            payload_interfaces=interfaces, payload_power=power, payload_thermal=thermal,
            payload_cg=cg, payload_analysis=analysis,
            engineering_notes=notes, recommendations=recs, warnings=[]
        )

class MilitaryPayloadStrategy(PayloadStrategy):
    def design_payload(self, reqs: PayloadRequirements, profile: PayloadProfile) -> PayloadResult:
        payload = PayloadSelector().select("Radar", reqs.preferred_payload_type)
        
        mount = PayloadMount(
            mount_type=reqs.preferred_mount_type or "Fixed",
            weight_kg=0.40, power_draw_watts=0.0,
            vibration_isolation=True, quick_release=True,
            drag_coefficient=0.25
        )
        
        bay = PayloadBay(
            width_m=0.30, height_m=0.20, length_m=0.20,
            max_load_kg=10.0, bay_volume_m3=0.012,
            fit_status=(payload.width_m <= 0.30 and payload.height_m <= 0.20 and payload.length_m <= 0.20),
            clearance_x_m=0.30 - payload.width_m, clearance_y_m=0.20 - payload.height_m, clearance_z_m=0.20 - payload.length_m
        )
        
        interfaces = PayloadInterfaces(
            data_connections=payload.data_interfaces, control_protocol="Mavlink",
            maintenance_accessibility="High", data_bandwidth_mbps=payload.data_bandwidth_mbps,
            quick_release_compatible=True
        )
        
        power = PayloadPower(
            continuous_power_watts=payload.power_draw_watts + mount.power_draw_watts,
            peak_power_watts=(payload.power_draw_watts + mount.power_draw_watts) * 2.0,
            voltage_volts=payload.voltage_volts,
            required_current_amps=(payload.power_draw_watts + mount.power_draw_watts) / payload.voltage_volts if payload.voltage_volts > 0 else 0.0,
            fuse_rating_amps=4.0, power_source="Main Battery"
        )
        
        thermal = PayloadThermal(
            heat_generated_watts=payload.heat_dissipation_watts, cooling_type="Active Fan",
            airflow_cfm_required=20.0, operating_temperature_max_c=75.0, cooling_margin_c=20.0
        )
        
        cg = self._calculate_cg_shift(payload, mount, reqs)
        analysis = self._estimate_analysis(payload, mount, bay, cg, power, thermal, interfaces)
        
        notes = ["Military grade surveillance configuration applied."]
        recs = ["Enforce EMI shielding on payload wire bundles."]
        
        return PayloadResult(
            payload_selection=payload, payload_mount=mount, payload_bay=bay,
            payload_interfaces=interfaces, payload_power=power, payload_thermal=thermal,
            payload_cg=cg, payload_analysis=analysis,
            engineering_notes=notes, recommendations=recs, warnings=[]
        )

class ResearchPayloadStrategy(PayloadStrategy):
    def design_payload(self, reqs: PayloadRequirements, profile: PayloadProfile) -> PayloadResult:
        payload = PayloadSelector().select("Scientific Instruments", reqs.preferred_payload_type)
        
        mount = PayloadMount(
            mount_type=reqs.preferred_mount_type or "Fixed",
            weight_kg=0.30, power_draw_watts=0.0,
            vibration_isolation=True, quick_release=True,
            drag_coefficient=0.30
        )
        
        bay = PayloadBay(
            width_m=0.40, height_m=0.30, length_m=0.30,
            max_load_kg=8.0, bay_volume_m3=0.036,
            fit_status=(payload.width_m <= 0.40 and payload.height_m <= 0.30 and payload.length_m <= 0.30),
            clearance_x_m=0.40 - payload.width_m, clearance_y_m=0.30 - payload.height_m, clearance_z_m=0.30 - payload.length_m
        )
        
        interfaces = PayloadInterfaces(
            data_connections=payload.data_interfaces, control_protocol="Custom",
            maintenance_accessibility="High", data_bandwidth_mbps=payload.data_bandwidth_mbps,
            quick_release_compatible=True
        )
        
        power = PayloadPower(
            continuous_power_watts=payload.power_draw_watts + mount.power_draw_watts,
            peak_power_watts=(payload.power_draw_watts + mount.power_draw_watts) * 1.5,
            voltage_volts=payload.voltage_volts,
            required_current_amps=(payload.power_draw_watts + mount.power_draw_watts) / payload.voltage_volts if payload.voltage_volts > 0 else 0.0,
            fuse_rating_amps=3.0, power_source="BEC 12V"
        )
        
        thermal = PayloadThermal(
            heat_generated_watts=payload.heat_dissipation_watts, cooling_type="Active Fan",
            airflow_cfm_required=10.0, operating_temperature_max_c=60.0, cooling_margin_c=15.0
        )
        
        cg = self._calculate_cg_shift(payload, mount, reqs)
        analysis = self._estimate_analysis(payload, mount, bay, cg, power, thermal, interfaces)
        
        notes = ["Research payload strategist layout complete."]
        recs = ["Utilize modular mounting interfaces for fast science payload reconfiguration."]
        
        return PayloadResult(
            payload_selection=payload, payload_mount=mount, payload_bay=bay,
            payload_interfaces=interfaces, payload_power=power, payload_thermal=thermal,
            payload_cg=cg, payload_analysis=analysis,
            engineering_notes=notes, recommendations=recs, warnings=[]
        )

class BalancedPayloadStrategy(PayloadStrategy):
    def design_payload(self, reqs: PayloadRequirements, profile: PayloadProfile) -> PayloadResult:
        payload = PayloadSelector().select("Multispectral Camera", reqs.preferred_payload_type)
        
        mount = PayloadMount(
            mount_type=reqs.preferred_mount_type or "Gimbal 2-Axis",
            weight_kg=0.20, power_draw_watts=4.0,
            vibration_isolation=True, quick_release=True,
            drag_coefficient=profile.aerodynamic_drag_coefficient_gimbal
        )
        
        bay = PayloadBay(
            width_m=0.30, height_m=0.20, length_m=0.20,
            max_load_kg=4.0, bay_volume_m3=0.012,
            fit_status=(payload.width_m <= 0.30 and payload.height_m <= 0.20 and payload.length_m <= 0.20),
            clearance_x_m=0.30 - payload.width_m, clearance_y_m=0.20 - payload.height_m, clearance_z_m=0.20 - payload.length_m
        )
        
        interfaces = PayloadInterfaces(
            data_connections=payload.data_interfaces, control_protocol="Mavlink",
            maintenance_accessibility="High", data_bandwidth_mbps=payload.data_bandwidth_mbps,
            quick_release_compatible=True
        )
        
        power = PayloadPower(
            continuous_power_watts=payload.power_draw_watts + mount.power_draw_watts,
            peak_power_watts=(payload.power_draw_watts + mount.power_draw_watts) * 1.5,
            voltage_volts=payload.voltage_volts,
            required_current_amps=(payload.power_draw_watts + mount.power_draw_watts) / payload.voltage_volts if payload.voltage_volts > 0 else 0.0,
            fuse_rating_amps=3.0, power_source="BEC 12V"
        )
        
        thermal = PayloadThermal(
            heat_generated_watts=payload.heat_dissipation_watts, cooling_type="Passive",
            airflow_cfm_required=0.0, operating_temperature_max_c=60.0, cooling_margin_c=15.0
        )
        
        cg = self._calculate_cg_shift(payload, mount, reqs)
        analysis = self._estimate_analysis(payload, mount, bay, cg, power, thermal, interfaces)
        
        notes = ["Balanced payload configuration sized."]
        recs = ["Deploy standard quick release mounting frame for multi-mission swapping capability."]
        
        return PayloadResult(
            payload_selection=payload, payload_mount=mount, payload_bay=bay,
            payload_interfaces=interfaces, payload_power=power, payload_thermal=thermal,
            payload_cg=cg, payload_analysis=analysis,
            engineering_notes=notes, recommendations=recs, warnings=[]
        )
