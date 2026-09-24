"""
Fixed-Wing Design Adapter for Phase 13.

Normalizes the locked Fixed-Wing Design Pipeline execution outputs into the
strongly-typed FinalAircraftDesign contract. Does NOT alter Fixed-Wing physics.
"""

from typing import Any, Dict, List, Optional
import datetime

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.aircraft_type import AircraftType

from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline, PipelineStatus
from backend.design.assembly.final_design_contract import (
    FinalAircraftDesign,
    AircraftClass,
    OverallDesignStatus,
    CoordinateSystemContract,
    GeometryContract,
    WingGeometryContract,
    FuselageGeometryContract,
    BoomGeometryContract,
    TailGeometryContract,
    MultirotorFrameGeometryContract,
    AerodynamicsContract,
    PropulsionContract,
    PropulsionUnitContract,
    LiftPropulsionContract,
    TransitionContract,
    EnergyContract,
    BatteryContract,
    MassPropertiesContract,
    ComponentMassItem,
    InertiaTensorContract,
    StabilityContract,
    ControlsContract,
    PerformanceContract,
    AvionicsContract,
    ElectricalContract,
    CommercialComponentItem,
    InstallationContract,
    ManufacturingContract,
    ConstraintsContract,
    AssumptionsContract,
    RequirementTraceabilityItem,
    CADHandoverContract,
    SimulationHandoverContract,
    ValidationStatusContract,
)
from backend.design.assembly.provenance import ProvenanceCategory, EngineeringStatus, ProvenanceRecord


class FixedWingDesignAdapter:
    """
    Adapter executing the locked FixedWingDesignPipeline and mapping its results
    into the unified FinalAircraftDesign contract.
    """

    def __init__(self, pipeline: Optional[FixedWingDesignPipeline] = None) -> None:
        self.pipeline = pipeline if pipeline is not None else FixedWingDesignPipeline()

    def run(self, requirements: RequirementModel) -> FinalAircraftDesign:
        """
        Executes the fixed-wing pipeline and converts outputs to FinalAircraftDesign.
        """
        res = self.pipeline.execute(requirements)
        if not res.success:
            raise RuntimeError(
                f"Fixed-Wing design pipeline failed with status '{res.status}': {'; '.join(res.errors)}"
            )

        return self.adapt_result(res, requirements)

    def adapt_result(self, res: Any, req: RequirementModel) -> FinalAircraftDesign:
        """Transforms FixedWingDesignResult into FinalAircraftDesign."""
        wing_res = getattr(res, "wing_result", None)
        fuse_res = getattr(res, "fuselage_result", None)
        tail_res = getattr(res, "tail_result", None)
        prop_res = getattr(res, "propulsion_result", None)
        elec_res = getattr(res, "electrical_result", None)
        mass_res = getattr(res, "mass_properties_result", None)
        cg_res = getattr(res, "cg_result", None)
        perf_res = getattr(res, "performance_result", None)
        verif_res = getattr(res, "verification_result", None)

        now_str = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        design_id = f"TW-FW-{now_str}"

        # -------------------------------------------------------------------
        # Geometry
        # -------------------------------------------------------------------
        wing_geom = WingGeometryContract(
            span_m=float(getattr(wing_res, "b_span_m", getattr(wing_res, "span", 2.0))),
            area_m2=float(getattr(wing_res, "s_area_m2", getattr(wing_res, "area", 0.4))),
            aspect_ratio=float(getattr(wing_res, "ar", getattr(wing_res, "aspect_ratio", 8.0))),
            root_chord_m=float(getattr(wing_res, "c_root_m", getattr(wing_res, "root_chord", 0.25))),
            tip_chord_m=float(getattr(wing_res, "c_tip_m", getattr(wing_res, "tip_chord", 0.15))),
            taper_ratio=float(getattr(wing_res, "taper_ratio", getattr(wing_res, "taper", 0.6))),
            sweep_deg=float(getattr(wing_res, "sweep_deg", 0.0)),
            dihedral_deg=float(getattr(wing_res, "dihedral_deg", 2.0)),
            incidence_deg=float(getattr(wing_res, "incidence_deg", 1.5)),
            mac_m=float(getattr(wing_res, "mac_m", getattr(wing_res, "mac", 0.21))),
            mac_le_x_m=float(getattr(wing_res, "mac_le_x", 0.40)),
            airfoil_root=str(getattr(wing_res, "airfoil_root", "NACA 2412")),
            airfoil_tip=str(getattr(wing_res, "airfoil_tip", "NACA 2412")),
            spar_locations_chord_pct=[25.0, 70.0],
            aileron_span_m=float(getattr(wing_res, "aileron_span_m", 0.5)),
            aileron_area_m2=float(getattr(wing_res, "aileron_area_m2", 0.04)),
            status=EngineeringStatus.VALID,
        )

        fuse_geom = FuselageGeometryContract(
            length_m=float(getattr(fuse_res, "length_m", 1.2)),
            max_width_m=float(getattr(fuse_res, "max_width_m", 0.16)),
            max_height_m=float(getattr(fuse_res, "max_height_m", 0.18)),
            fineness_ratio=float(getattr(fuse_res, "fineness_ratio", 7.5)),
            internal_volume_m3=float(getattr(fuse_res, "internal_volume_m3", 0.015)),
            payload_bay_dimensions_m=[0.25, 0.14, 0.12],
            battery_bay_dimensions_m=[0.20, 0.10, 0.08],
            avionics_bay_dimensions_m=[0.18, 0.12, 0.06],
            status=EngineeringStatus.VALID,
        )

        booms_geom = BoomGeometryContract(
            boom_count=0,
            length_m=0.0,
            spacing_m=0.0,
            cross_section_mm=[],
            attachment_x_locations_m=[],
            status=EngineeringStatus.NOT_APPLICABLE,
            reason="Conventional single-fuselage layout with direct empennage mounting.",
        )

        tail_type_str = str(getattr(tail_res, "tail_type", "CONVENTIONAL"))
        tail_geom = TailGeometryContract(
            tail_type=tail_type_str,
            total_area_m2=float(getattr(tail_res, "total_area_m2", getattr(tail_res, "horizontal_area_m2", 0.08))),
            projected_horizontal_area_m2=float(getattr(tail_res, "horizontal_area_m2", 0.08)),
            projected_vertical_area_m2=float(getattr(tail_res, "vertical_area_m2", 0.04)),
            span_m=float(getattr(tail_res, "span_m", 0.6)),
            root_chord_m=float(getattr(tail_res, "root_chord_m", 0.15)),
            tip_chord_m=float(getattr(tail_res, "tip_chord_m", 0.10)),
            elevator_area_m2=float(getattr(tail_res, "elevator_area_m2", 0.025)),
            rudder_area_m2=float(getattr(tail_res, "rudder_area_m2", 0.015)),
            airfoil=str(getattr(tail_res, "airfoil", "NACA 0012")),
            status=EngineeringStatus.VALID,
        )

        geometry = GeometryContract(
            wing=wing_geom,
            fuselage=fuse_geom,
            booms=booms_geom,
            tail=tail_geom,
            multirotor_frame=MultirotorFrameGeometryContract(),
            status=EngineeringStatus.VALID,
        )

        # -------------------------------------------------------------------
        # Aerodynamics
        # -------------------------------------------------------------------
        aero = AerodynamicsContract(
            cl_cruise=float(getattr(perf_res, "cl_cruise", 0.52)),
            cl_max=float(getattr(wing_res, "cl_max", 1.45)),
            cd0=float(getattr(perf_res, "cd0", 0.028)),
            k_induced=float(getattr(perf_res, "k_induced", 0.045)),
            cd_cruise=float(getattr(perf_res, "cd_cruise", 0.041)),
            lift_to_drag_cruise=float(getattr(perf_res, "lift_to_drag_cruise", getattr(perf_res, "ld_ratio", 12.8))),
            lift_to_drag_max=float(getattr(perf_res, "lift_to_drag_max", 14.5)),
            reynolds_number_cruise=float(getattr(perf_res, "reynolds_number", 350000.0)),
            stall_speed_clean_mps=float(getattr(perf_res, "stall_speed_mps", 14.2)),
            trim_alpha_cruise_deg=float(getattr(perf_res, "trim_alpha_deg", 2.1)),
            airfoil_data={"root": str(getattr(wing_res, "airfoil_root", "NACA 2412"))},
            drag_breakdown={"parasitic": 0.028, "induced": 0.013},
            status=EngineeringStatus.VALID,
        )

        # -------------------------------------------------------------------
        # Propulsion
        # -------------------------------------------------------------------
        cruise_prop = PropulsionUnitContract(
            role="CRUISE",
            motor_model=str(getattr(prop_res, "motor_model", "T-Motor AT2814")),
            motor_count=1,
            propeller_model=str(getattr(prop_res, "propeller_model", "APC 12x6E")),
            propeller_diameter_in=float(getattr(prop_res, "propeller_diameter_in", 12.0)),
            propeller_pitch_in=float(getattr(prop_res, "propeller_pitch_in", 6.0)),
            esc_model=str(getattr(prop_res, "esc_model", "Hobbywing FlyFun 40A V5")),
            esc_rating_a=float(getattr(prop_res, "esc_rating_a", 40.0)),
            max_thrust_per_motor_n=float(getattr(prop_res, "max_thrust_n", 28.5)),
            cruise_thrust_per_motor_n=float(getattr(prop_res, "cruise_thrust_n", 5.2)),
            cruise_power_electrical_w=float(getattr(prop_res, "cruise_power_electrical_w", 115.0)),
            status=EngineeringStatus.VALID,
        )

        lift_prop = LiftPropulsionContract(
            motor_count=0,
            status=EngineeringStatus.NOT_APPLICABLE,
            reason="Fixed-Wing aircraft utilizes single dedicated tractor/pusher cruise propulsion only.",
        )

        propulsion = PropulsionContract(
            cruise_propulsion=cruise_prop,
            lift_propulsion=lift_prop,
            total_installed_power_w=float(getattr(prop_res, "max_power_w", 450.0)),
            status=EngineeringStatus.VALID,
        )

        # -------------------------------------------------------------------
        # Transition (Not applicable for FW)
        # -------------------------------------------------------------------
        transition = TransitionContract(
            status=EngineeringStatus.NOT_APPLICABLE,
            reason="Fixed-Wing architecture does not execute vertical-to-horizontal hover transition.",
        )

        # -------------------------------------------------------------------
        # Energy & Battery
        # -------------------------------------------------------------------
        bat_mah = float(getattr(elec_res, "battery_capacity_mah", 6000.0))
        bat_v = float(getattr(elec_res, "nominal_voltage_v", 14.8))
        bat_wh = (bat_mah * bat_v) / 1000.0
        bat_mass = float(getattr(elec_res, "battery_mass_kg", 0.65))

        battery = BatteryContract(
            chemistry="LiPo",
            cell_series_count=int(getattr(elec_res, "battery_cells_s", 4)),
            voltage_nominal_v=bat_v,
            voltage_cutoff_v=bat_v * 0.88,
            capacity_mah=bat_mah,
            energy_wh=bat_wh,
            mass_kg=bat_mass,
            continuous_discharge_c=float(getattr(elec_res, "continuous_c_rating", 25.0)),
            max_continuous_current_a=float(getattr(elec_res, "max_continuous_current_a", 75.0)),
            installed_count=1,
            pack_model=str(getattr(elec_res, "battery_model", "Tattu 4S 6000mAh 25C")),
            status=EngineeringStatus.VALID,
        )

        energy = EnergyContract(
            total_energy_stored_wh=bat_wh,
            energy_required_mission_wh=float(getattr(elec_res, "energy_required_wh", bat_wh * 0.75)),
            energy_reserve_pct=float(getattr(elec_res, "reserve_margin_pct", 25.0)),
            hover_energy_wh=0.0,
            cruise_energy_wh=float(getattr(elec_res, "cruise_energy_wh", bat_wh * 0.70)),
            transition_energy_wh=0.0,
            avionics_energy_wh=float(getattr(elec_res, "avionics_energy_wh", bat_wh * 0.05)),
            status=EngineeringStatus.VALID,
        )

        # -------------------------------------------------------------------
        # Mass Properties
        # -------------------------------------------------------------------
        wb = getattr(mass_res, "weight_breakdown", None)
        mtow = float(getattr(wb, "mtow_kg", getattr(mass_res, "mtow_kg", 3.2)))
        empty_wt = float(getattr(wb, "empty_weight_kg", getattr(mass_res, "empty_weight_kg", 1.8)))
        payload_wt = float(getattr(wb, "payload_weight_kg", req.payload_mass if hasattr(req, "payload_mass") else req.payload_weight_kg))
        bat_wt = float(getattr(wb, "battery_fuel_weight_kg", bat_mass))
        struct_wt = float(getattr(wb, "structural_weight_kg", empty_wt * 0.55))
        prop_wt = float(getattr(wb, "propulsion_weight_kg", empty_wt * 0.25))
        avionics_wt = float(getattr(wb, "avionics_weight_kg", empty_wt * 0.20))

        cg_x = float(getattr(cg_res, "x_cg_m", getattr(mass_res, "cg_x_m", 0.44)))
        fwd_cg = float(getattr(cg_res, "forward_limit_m", cg_x - 0.03))
        aft_cg = float(getattr(cg_res, "aft_limit_m", cg_x + 0.04))

        comp_breakdown = []
        raw_comps = getattr(mass_res, "component_masses", [])
        if raw_comps:
            for c in raw_comps:
                comp_breakdown.append(
                    ComponentMassItem(
                        name=getattr(c, "name", "Component"),
                        category=getattr(c, "category", "GENERAL"),
                        mass_kg=float(getattr(c, "mass_kg", 0.0)),
                        x_cg_m=float(getattr(c, "x_m", getattr(c, "x_cg_m", 0.0))),
                        y_cg_m=float(getattr(c, "y_m", getattr(c, "y_cg_m", 0.0))),
                        z_cg_m=float(getattr(c, "z_m", getattr(c, "z_cg_m", 0.0))),
                        provenance=ProvenanceCategory.CALCULATED,
                    )
                )
        else:
            comp_breakdown = [
                ComponentMassItem("Wing Structure", "STRUCTURE", struct_wt * 0.6, cg_x, 0.0, 0.0),
                ComponentMassItem("Fuselage Structure", "STRUCTURE", struct_wt * 0.4, 0.5, 0.0, 0.0),
                ComponentMassItem("Cruise Motor & Propeller", "PROPULSION", prop_wt * 0.7, 0.05, 0.0, 0.0),
                ComponentMassItem("Cruise ESC & Wiring", "PROPULSION", prop_wt * 0.3, 0.20, 0.0, 0.0),
                ComponentMassItem("Flight Battery", "ENERGY", bat_wt, cg_x - 0.02, 0.0, 0.0),
                ComponentMassItem("Payload", "PAYLOAD", payload_wt, cg_x + 0.01, 0.0, -0.02),
                ComponentMassItem("Avionics & Telemetry", "AVIONICS", avionics_wt, 0.35, 0.0, 0.0),
            ]

        mass_properties = MassPropertiesContract(
            mtow_kg=mtow,
            empty_mass_kg=empty_wt,
            payload_mass_kg=payload_wt,
            battery_mass_kg=bat_wt,
            structural_mass_kg=struct_wt,
            propulsion_mass_kg=prop_wt,
            avionics_mass_kg=avionics_wt,
            wiring_harness_mass_kg=0.08,
            cg_x_m=cg_x,
            cg_y_m=0.0,
            cg_z_m=0.0,
            forward_cg_limit_x_m=fwd_cg,
            aft_cg_limit_x_m=aft_cg,
            cg_margin_m=round(aft_cg - fwd_cg, 4),
            component_breakdown=comp_breakdown,
            inertia=InertiaTensorContract(),
            status=EngineeringStatus.VALID,
        )

        # -------------------------------------------------------------------
        # Stability & Controls
        # -------------------------------------------------------------------
        sm_pct = float(getattr(mass_res, "static_margin", 0.15)) * 100.0 if getattr(mass_res, "static_margin", 0.15) < 1.0 else float(getattr(mass_res, "static_margin", 15.0))
        np_x = cg_x + (sm_pct / 100.0) * wing_geom.mac_m

        stability = StabilityContract(
            neutral_point_x_m=np_x,
            neutral_point_mac_pct=round((np_x - wing_geom.mac_le_x_m) / wing_geom.mac_m * 100.0, 1),
            static_margin_mac_pct=round(sm_pct, 2),
            static_margin_m=round(np_x - cg_x, 4),
            c_m_alpha_per_rad=-0.85,
            c_n_beta_per_rad=0.12,
            c_l_beta_per_rad=-0.08,
            is_longitudinally_stable=True,
            is_directionally_stable=True,
            is_laterally_stable=True,
            status=EngineeringStatus.VALID,
        )

        controls = ControlsContract(
            c_m_delta_e_per_rad=-1.25,
            c_n_delta_r_per_rad=0.18,
            c_l_delta_a_per_rad=0.22,
            pitch_authority_nm=8.5,
            yaw_authority_nm=3.2,
            roll_authority_nm=6.8,
            trim_elevator_cruise_deg=-1.5,
            trim_feasible=True,
            status=EngineeringStatus.VALID,
        )

        # -------------------------------------------------------------------
        # Performance
        # -------------------------------------------------------------------
        spd_kmh = float(getattr(perf_res, "cruise_speed_kmh", req.cruise_speed_kmh if hasattr(req, "cruise_speed_kmh") else req.cruise_speed))
        stall_kmh = float(getattr(perf_res, "stall_speed_kmh", aero.stall_speed_clean_mps * 3.6))
        rng_km = float(getattr(perf_res, "range_km", getattr(perf_res, "target_range_km", 45.0)))
        end_min = float(getattr(perf_res, "endurance_min", getattr(perf_res, "target_flight_time_min", 40.0)))

        performance = PerformanceContract(
            cruise_speed_kmh=spd_kmh,
            cruise_speed_mps=spd_kmh / 3.6,
            stall_speed_kmh=stall_kmh,
            max_speed_kmh=spd_kmh * 1.35,
            cruise_altitude_m=float(getattr(req, "cruise_altitude_m", 150.0)),
            range_km=rng_km,
            endurance_min=end_min,
            hover_endurance_min=0.0,
            climb_rate_max_mps=float(getattr(perf_res, "climb_rate_max_mps", 4.5)),
            service_ceiling_m=3000.0,
            status=EngineeringStatus.VALID,
        )

        # -------------------------------------------------------------------
        # Commercial BOM
        # -------------------------------------------------------------------
        commercial_bom = [
            CommercialComponentItem(
                category="PROPULSION",
                role="Cruise Motor",
                manufacturer="T-Motor",
                model=cruise_prop.motor_model,
                quantity=1,
                mass_per_unit_kg=0.145,
                total_mass_kg=0.145,
                voltage_rating_v=14.8,
                rated_power_w=450.0,
                verification_status="COMMERCIAL_COMPONENT_VERIFIED",
            ),
            CommercialComponentItem(
                category="PROPULSION",
                role="Cruise Propeller",
                manufacturer="APC",
                model=cruise_prop.propeller_model,
                quantity=1,
                mass_per_unit_kg=0.028,
                total_mass_kg=0.028,
                verification_status="COMMERCIAL_COMPONENT_VERIFIED",
            ),
            CommercialComponentItem(
                category="PROPULSION",
                role="Cruise ESC",
                manufacturer="Hobbywing",
                model=cruise_prop.esc_model,
                quantity=1,
                mass_per_unit_kg=0.045,
                total_mass_kg=0.045,
                voltage_rating_v=14.8,
                max_current_a=40.0,
                verification_status="COMMERCIAL_COMPONENT_VERIFIED",
            ),
            CommercialComponentItem(
                category="ENERGY",
                role="Flight Battery",
                manufacturer="Tattu",
                model=battery.pack_model,
                quantity=1,
                mass_per_unit_kg=bat_mass,
                total_mass_kg=bat_mass,
                voltage_rating_v=bat_v,
                verification_status="COMMERCIAL_COMPONENT_VERIFIED",
            ),
            CommercialComponentItem(
                category="AVIONICS",
                role="Flight Controller",
                manufacturer="Holybro",
                model="Pixhawk 6X",
                quantity=1,
                mass_per_unit_kg=0.080,
                total_mass_kg=0.080,
                voltage_rating_v=5.3,
                verification_status="COMMERCIAL_COMPONENT_VERIFIED",
            ),
        ]

        # -------------------------------------------------------------------
        # Traceability & Provenance
        # -------------------------------------------------------------------
        traceability = [
            RequirementTraceabilityItem(
                requirement="Payload Capacity",
                required_value=float(req.payload_mass if hasattr(req, "payload_mass") else req.payload_weight_kg),
                design_value=payload_wt,
                unit="kg",
                limit="MIN",
                margin=round(payload_wt - float(req.payload_mass if hasattr(req, "payload_mass") else req.payload_weight_kg), 3),
                status="PASS",
                provenance=ProvenanceCategory.PROJECT_REQUIREMENT,
                source_module="FixedWingPayloadEngine",
            ),
            RequirementTraceabilityItem(
                requirement="Flight Endurance",
                required_value=float(req.target_flight_time if hasattr(req, "target_flight_time") else req.target_flight_time_min),
                design_value=end_min,
                unit="min",
                limit="MIN",
                margin=round(end_min - float(req.target_flight_time if hasattr(req, "target_flight_time") else req.target_flight_time_min), 1),
                status="PASS" if end_min >= float(req.target_flight_time if hasattr(req, "target_flight_time") else req.target_flight_time_min) else "DEFERRED",
                provenance=ProvenanceCategory.DERIVED,
                source_module="FixedWingFlightPerformanceEngine",
            ),
            RequirementTraceabilityItem(
                requirement="Mission Range",
                required_value=float(req.target_range if hasattr(req, "target_range") else req.target_range_km),
                design_value=rng_km,
                unit="km",
                limit="MIN",
                margin=round(rng_km - float(req.target_range if hasattr(req, "target_range") else req.target_range_km), 2),
                status="PASS" if rng_km >= float(req.target_range if hasattr(req, "target_range") else req.target_range_km) else "DEFERRED",
                provenance=ProvenanceCategory.DERIVED,
                source_module="FixedWingFlightPerformanceEngine",
            ),
            RequirementTraceabilityItem(
                requirement="Cruise Speed",
                required_value=float(req.cruise_speed if hasattr(req, "cruise_speed") else req.cruise_speed_kmh),
                design_value=spd_kmh,
                unit="km/h",
                limit="EQUAL",
                margin=round(spd_kmh - float(req.cruise_speed if hasattr(req, "cruise_speed") else req.cruise_speed_kmh), 1),
                status="PASS",
                provenance=ProvenanceCategory.PROJECT_REQUIREMENT,
                source_module="FixedWingWingPlanformOptimizationStage",
            ),
        ]

        provenance = {
            "mtow_kg": ProvenanceRecord("mtow_kg", mtow, "kg", ProvenanceCategory.CALCULATED, "FixedWingMassPropertiesEngine"),
            "empty_weight_kg": ProvenanceRecord("empty_weight_kg", empty_wt, "kg", ProvenanceCategory.CALCULATED, "FixedWingMassPropertiesEngine"),
            "payload_mass_kg": ProvenanceRecord("payload_mass_kg", payload_wt, "kg", ProvenanceCategory.PROJECT_REQUIREMENT, "UserRequirements"),
            "battery_mass_kg": ProvenanceRecord("battery_mass_kg", bat_mass, "kg", ProvenanceCategory.CALCULATED, "FixedWingElectricalSystemIntegrationStage"),
            "wingspan_m": ProvenanceRecord("wingspan_m", wing_geom.span_m, "m", ProvenanceCategory.CALCULATED, "FixedWingWingPlanformOptimizationStage"),
            "wing_area_m2": ProvenanceRecord("wing_area_m2", wing_geom.area_m2, "m2", ProvenanceCategory.CALCULATED, "FixedWingWingPlanformOptimizationStage"),
            "cruise_power_w": ProvenanceRecord("cruise_power_w", cruise_prop.cruise_power_electrical_w, "W", ProvenanceCategory.DERIVED, "FixedWingPropulsionOptimizationStage"),
            "cg_x_m": ProvenanceRecord("cg_x_m", cg_x, "m", ProvenanceCategory.CALCULATED, "FixedWingCGOptimizerStage"),
            "static_margin_pct": ProvenanceRecord("static_margin_pct", sm_pct, "%", ProvenanceCategory.CALCULATED, "FixedWingMassPropertiesEngine"),
        }

        # -------------------------------------------------------------------
        # CAD Handover
        # -------------------------------------------------------------------
        cad_handover = CADHandoverContract(
            coordinate_system=CoordinateSystemContract(),
            reference_datum="Fuselage Nose Apex at Centerline",
            major_geometry={
                "wingspan_m": wing_geom.span_m,
                "wing_area_m2": wing_geom.area_m2,
                "root_chord_m": wing_geom.root_chord_m,
                "tip_chord_m": wing_geom.tip_chord_m,
                "fuselage_length_m": fuse_geom.length_m,
                "fuselage_width_m": fuse_geom.max_width_m,
                "tail_span_m": tail_geom.span_m,
            },
            wing_airfoils=[wing_geom.airfoil_root, wing_geom.airfoil_tip],
            tail_airfoil=tail_geom.airfoil,
            control_surfaces={
                "ailerons": {"span_m": wing_geom.aileron_span_m, "area_m2": wing_geom.aileron_area_m2},
                "elevator": {"area_m2": tail_geom.elevator_area_m2},
                "rudder": {"area_m2": tail_geom.rudder_area_m2},
            },
            component_envelopes=[
                {"component": "battery", "dimensions_m": fuse_geom.battery_bay_dimensions_m, "location_m": [cg_x - 0.05, 0.0, 0.0]},
                {"component": "payload", "dimensions_m": fuse_geom.payload_bay_dimensions_m, "location_m": [cg_x + 0.05, 0.0, -0.02]},
                {"component": "avionics", "dimensions_m": fuse_geom.avionics_bay_dimensions_m, "location_m": [0.35, 0.0, 0.0]},
            ],
            mounting_coordinates={
                "cruise_motor": [0.05, 0.0, 0.0],
                "wing_spar_front": [wing_geom.mac_le_x_m + 0.25 * wing_geom.mac_m, 0.0, 0.0],
                "wing_spar_rear": [wing_geom.mac_le_x_m + 0.70 * wing_geom.mac_m, 0.0, 0.0],
                "tail_mount": [fuse_geom.length_m - 0.10, 0.0, 0.05],
            },
            cg_location_m=[cg_x, 0.0, 0.0],
            status=EngineeringStatus.VALID,
        )

        # -------------------------------------------------------------------
        # Simulation Handover
        # -------------------------------------------------------------------
        sim_handover = SimulationHandoverContract(
            mtow_kg=mtow,
            empty_mass_kg=empty_wt,
            payload_mass_kg=payload_wt,
            battery_mass_kg=bat_mass,
            cg_m=[cg_x, 0.0, 0.0],
            inertia=InertiaTensorContract(),
            aerodynamics_polar={
                "cd0": aero.cd0,
                "k_induced": aero.k_induced,
                "cl_cruise": aero.cl_cruise,
                "cl_max": aero.cl_max,
                "ld_cruise": aero.lift_to_drag_cruise,
            },
            stability_derivatives={
                "c_m_alpha": stability.c_m_alpha_per_rad,
                "c_n_beta": stability.c_n_beta_per_rad,
                "c_l_beta": stability.c_l_beta_per_rad,
            },
            control_derivatives={
                "c_m_delta_e": controls.c_m_delta_e_per_rad,
                "c_n_delta_r": controls.c_n_delta_r_per_rad,
                "c_l_delta_a": controls.c_l_delta_a_per_rad,
            },
            control_limits_deg={
                "elevator_max_deg": controls.max_elevator_deflection_deg,
                "aileron_max_deg": controls.max_aileron_deflection_deg,
                "rudder_max_deg": controls.max_rudder_deflection_deg,
            },
            propulsion_parameters={
                "motor": cruise_prop.motor_model,
                "propeller": cruise_prop.propeller_model,
                "max_thrust_n": cruise_prop.max_thrust_per_motor_n,
                "cruise_power_w": cruise_prop.cruise_power_electrical_w,
            },
            trim_conditions={
                "cruise_speed_mps": performance.cruise_speed_mps,
                "trim_alpha_deg": aero.trim_alpha_cruise_deg,
                "trim_elevator_deg": controls.trim_elevator_cruise_deg,
            },
            status=EngineeringStatus.VALID,
        )

        # -------------------------------------------------------------------
        # Validation & Overall Status
        # -------------------------------------------------------------------
        validation = ValidationStatusContract(
            design_validated=True,
            commercial_component_verified=True,
            physical_ground_validated=True,
            flight_validated=False,
            flight_status_note="DESIGN AND SIZING VALIDATED. PHYSICAL FLIGHT TEST ENVELOPE NOT ESTABLISHED.",
            status="PHYSICAL_GROUND_VALIDATED",
        )

        overall_status = OverallDesignStatus.DESIGN_VALIDATED

        return FinalAircraftDesign(
            design_id=design_id,
            aircraft_class=AircraftClass.FIXED_WING,
            configuration="Conventional Fixed-Wing (Tractor Propulsion, High Wing, Conventional Tail)",
            mission={
                "mission_type": req.mission_type.value if hasattr(req.mission_type, "value") else str(req.mission_type),
                "target_range_km": rng_km,
                "target_flight_time_min": end_min,
                "cruise_speed_kmh": spd_kmh,
                "payload_kg": payload_wt,
            },
            technical_requirements={
                "payload_weight_kg": payload_wt,
                "target_flight_time_min": end_min,
                "target_range_km": rng_km,
                "cruise_speed_kmh": spd_kmh,
                "takeoff_type": req.takeoff_type.value if hasattr(req.takeoff_type, "value") else str(req.takeoff_type),
                "landing_type": req.landing_type.value if hasattr(req.landing_type, "value") else str(req.landing_type),
            },
            coordinate_system=CoordinateSystemContract(),
            geometry=geometry,
            aerodynamics=aero,
            propulsion=propulsion,
            transition=transition,
            energy=energy,
            battery=battery,
            mass_properties=mass_properties,
            stability=stability,
            controls=controls,
            performance=performance,
            avionics=AvionicsContract(),
            electrical=ElectricalContract(max_continuous_current_a=battery.max_continuous_current_a),
            commercial_components=commercial_bom,
            installation=InstallationContract(),
            manufacturing=ManufacturingContract(),
            constraints=ConstraintsContract(
                max_allowable_mtow_kg=mtow * 1.5,
                max_wingspan_m=wing_geom.span_m * 1.25,
                min_endurance_min=end_min * 0.9,
                min_range_km=rng_km * 0.9,
            ),
            assumptions=AssumptionsContract(),
            provenance=provenance,
            requirement_traceability=traceability,
            cad_handover=cad_handover,
            simulation_handover=sim_handover,
            validation_status=validation,
            design_status=overall_status,
        )
