"""
VTOL Requirement Model Subsystem.

Purpose:
    Defines the authoritative `VTOLRequirementModel` class capturing all canonical
    and VTOL-specific sizing requirements for the Torq Wings VTOL Design Studio.

Role in Architecture:
    `VTOLRequirementModel` extends the canonical `RequirementModel`, preserving all
    mission, payload, endurance, environment, optimization priority, and design mode
    definitions while introducing typed, authoritative parameters for vertical hover,
    conversion/transition, and dual-propulsion configuration sizing.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Dict
from enum import Enum

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.vtol.mission.mission_requirements import (
    VTOLType,
    VTOLMissionCategory,
    TakeoffMethod,
    LandingMethod,
    EnvironmentType,
    AutonomyLevel,
    HoverRequirements as MissionHoverReq,
    TransitionRequirements as MissionTransReq,
    CruiseRequirements as MissionCruiseReq,
    MissionRequirements,
)


@dataclass(slots=True)
class VTOLRequirementModel(RequirementModel):
    """
    Authoritative domain model encapsulating user-specified VTOL aircraft requirements.

    Inherits all canonical fields from `RequirementModel` and adds typed parameters
    governing the hover, transition, and configuration disciplines.
    """

    # VTOL-Specific Configuration & Sizing Parameters
    vtol_type: VTOLType = VTOLType.QUADPLANE
    hover_duration_min: float = 5.0
    hover_altitude_m: float = 100.0
    climb_rate_vertical_m_s: float = 2.5
    descent_rate_vertical_m_s: float = 2.0
    wind_limit_hover_kts: float = 15.0
    transition_speed_kmh: float = 65.0
    transition_duration_s: float = 15.0
    transition_altitude_m: float = 120.0
    max_transition_pitch_deg: float = 20.0
    lift_motor_count: int = 4
    cruise_motor_count: int = 1
    rotor_diameter_m: Optional[float] = None
    system_voltage_v: Optional[float] = None
    hover_thrust_to_weight_target: Optional[float] = None

    @property
    def payload_mass(self) -> float:
        return self.payload_weight_kg

    @property
    def target_range(self) -> float:
        return self.target_range_km

    @property
    def target_flight_time(self) -> float:
        return self.target_flight_time_min

    @property
    def cruise_speed(self) -> float:
        return self.cruise_speed_kmh

    @property
    def mtow_limit(self) -> float | None:
        return self.maximum_takeoff_weight_kg

    @classmethod
    def create(
        cls,
        mission_type: MissionType = MissionType.SURVEY,
        payload_mass: Optional[float] = None,
        payload_weight_kg: Optional[float] = None,
        target_range: Optional[float] = None,
        target_range_km: Optional[float] = None,
        target_flight_time: Optional[float] = None,
        target_flight_time_min: Optional[float] = None,
        cruise_speed: Optional[float] = None,
        cruise_speed_kmh: Optional[float] = None,
        vtol_type: VTOLType = VTOLType.QUADPLANE,
        hover_duration_min: float = 5.0,
        transition_speed_kmh: float = 65.0,
        lift_motor_count: int = 4,
        cruise_motor_count: int = 1,
        rotor_diameter_m: Optional[float] = None,
        system_voltage_v: Optional[float] = None,
        hover_thrust_to_weight_target: Optional[float] = None,
        takeoff_type: TakeoffType = TakeoffType.VERTICAL,
        landing_type: LandingType = LandingType.VERTICAL,
        environment: OperatingEnvironment = OperatingEnvironment.RURAL,
        optimization_priority: OptimizationPriority = OptimizationPriority.BALANCED,
        design_mode: DesignMode = DesignMode.MANUAL,
        mtow_limit: Optional[float] = None,
        maximum_takeoff_weight_kg: Optional[float] = None,
        budget: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "VTOLRequirementModel":
        pld = payload_weight_kg if payload_weight_kg is not None else (payload_mass if payload_mass is not None else 2.0)
        rng = target_range_km if target_range_km is not None else (target_range if target_range is not None else 40.0)
        endur = target_flight_time_min if target_flight_time_min is not None else (target_flight_time if target_flight_time is not None else 30.0)
        spd = cruise_speed_kmh if cruise_speed_kmh is not None else (cruise_speed if cruise_speed is not None else 90.0)
        mtow = maximum_takeoff_weight_kg if maximum_takeoff_weight_kg is not None else mtow_limit

        return cls(
            mission_type=mission_type,
            payload_weight_kg=float(pld),
            target_flight_time_min=float(endur),
            target_range_km=float(rng),
            cruise_speed_kmh=float(spd),
            aircraft_type=AircraftType.VTOL,
            maximum_takeoff_weight_kg=float(mtow) if mtow is not None else None,
            budget=float(budget) if budget is not None else None,
            takeoff_type=takeoff_type,
            landing_type=landing_type,
            environment=environment,
            optimization_priority=optimization_priority,
            design_mode=design_mode,
            metadata=dict(metadata or {}),
            vtol_type=vtol_type,
            hover_duration_min=hover_duration_min,
            transition_speed_kmh=transition_speed_kmh,
            lift_motor_count=lift_motor_count,
            cruise_motor_count=cruise_motor_count,
            rotor_diameter_m=float(rotor_diameter_m) if rotor_diameter_m is not None else None,
            system_voltage_v=float(system_voltage_v) if system_voltage_v is not None else None,
            hover_thrust_to_weight_target=float(hover_thrust_to_weight_target) if hover_thrust_to_weight_target is not None else None,
        )

    def __post_init__(self) -> None:
        # Default aircraft_type to VTOL
        if self.aircraft_type is None:
            object.__setattr__(self, "aircraft_type", AircraftType.VTOL)

    @classmethod
    def from_requirement_model(
        cls,
        req: RequirementModel,
        vtol_type: Optional[VTOLType] = None,
        hover_duration_min: Optional[float] = None,
        hover_altitude_m: Optional[float] = None,
        transition_speed_kmh: Optional[float] = None,
        transition_duration_s: Optional[float] = None,
        lift_motor_count: Optional[int] = None,
        cruise_motor_count: Optional[int] = None,
        rotor_diameter_m: Optional[float] = None,
        system_voltage_v: Optional[float] = None,
        hover_thrust_to_weight_target: Optional[float] = None,
        **kwargs: Any,
    ) -> "VTOLRequirementModel":
        """
        Constructs a typed `VTOLRequirementModel` from a canonical `RequirementModel`.
        Reads VTOL parameters from arguments or inspects `req.metadata`.
        """
        meta = req.metadata or {}

        # Resolve VTOL type
        resolved_vtol_type = vtol_type
        if resolved_vtol_type is None and "preferred_vtol_type" in meta:
            vt_val = str(meta["preferred_vtol_type"]).strip().lower()
            for vt in VTOLType:
                if vt.value.lower() == vt_val or vt.name.lower() == vt_val:
                    resolved_vtol_type = vt
                    break
        if resolved_vtol_type is None:
            resolved_vtol_type = VTOLType.QUADPLANE

        # Resolve rotor diameter
        resolved_rotor_diam = rotor_diameter_m
        if resolved_rotor_diam is None and "rotor_diameter_m" in meta:
            resolved_rotor_diam = float(meta["rotor_diameter_m"])

        # Resolve voltage
        resolved_voltage = system_voltage_v
        if resolved_voltage is None and "system_voltage_v" in meta:
            resolved_voltage = float(meta["system_voltage_v"])

        # Resolve hover T/W target
        resolved_tw = hover_thrust_to_weight_target
        if resolved_tw is None and "hover_thrust_to_weight_target" in meta:
            resolved_tw = float(meta["hover_thrust_to_weight_target"])
        elif resolved_tw is None and "preferred_hover_margin" in meta:
            resolved_tw = float(meta["preferred_hover_margin"])

        return cls(
            mission_type=req.mission_type,
            payload_weight_kg=req.payload_weight_kg,
            target_flight_time_min=req.target_flight_time_min,
            target_range_km=req.target_range_km,
            cruise_speed_kmh=req.cruise_speed_kmh,
            aircraft_type=AircraftType.VTOL,
            maximum_takeoff_weight_kg=req.maximum_takeoff_weight_kg,
            budget=req.budget,
            takeoff_type=req.takeoff_type,
            landing_type=req.landing_type,
            environment=req.environment,
            optimization_priority=req.optimization_priority,
            design_mode=req.design_mode,
            metadata=dict(meta),
            vtol_type=resolved_vtol_type,
            hover_duration_min=hover_duration_min if hover_duration_min is not None else float(meta.get("hover_duration_min", 5.0)),
            hover_altitude_m=hover_altitude_m if hover_altitude_m is not None else float(meta.get("hover_altitude_m", 100.0)),
            climb_rate_vertical_m_s=float(meta.get("climb_rate_vertical_m_s", 2.5)),
            descent_rate_vertical_m_s=float(meta.get("descent_rate_vertical_m_s", 2.0)),
            wind_limit_hover_kts=float(meta.get("wind_limit_hover_kts", 15.0)),
            transition_speed_kmh=transition_speed_kmh if transition_speed_kmh is not None else float(meta.get("transition_speed_kmh", 65.0)),
            transition_duration_s=transition_duration_s if transition_duration_s is not None else float(meta.get("transition_duration_s", 15.0)),
            transition_altitude_m=float(meta.get("transition_altitude_m", 120.0)),
            max_transition_pitch_deg=float(meta.get("max_transition_pitch_deg", 20.0)),
            lift_motor_count=lift_motor_count if lift_motor_count is not None else int(meta.get("lift_motor_count", 4)),
            cruise_motor_count=cruise_motor_count if cruise_motor_count is not None else int(meta.get("cruise_motor_count", 1)),
            rotor_diameter_m=resolved_rotor_diam,
            system_voltage_v=resolved_voltage,
            hover_thrust_to_weight_target=resolved_tw,
        )

    def to_mission_requirements(self) -> MissionRequirements:
        """
        Translates this typed VTOL requirement model to internal `MissionRequirements`.
        """
        cat_mapping = {
            MissionType.MAPPING: VTOLMissionCategory.MAPPING,
            MissionType.SURVEY: VTOLMissionCategory.SURVEY,
            MissionType.INSPECTION: VTOLMissionCategory.INSPECTION,
            MissionType.DELIVERY: VTOLMissionCategory.DELIVERY,
            MissionType.AGRICULTURE: VTOLMissionCategory.AGRICULTURE,
        }
        category = cat_mapping.get(self.mission_type, VTOLMissionCategory.SURVEY)

        hover = MissionHoverReq(
            hover_duration_min=self.hover_duration_min,
            hover_altitude_m=self.hover_altitude_m,
            wind_limit_hover_kts=self.wind_limit_hover_kts,
            climb_rate_vertical_m_s=self.climb_rate_vertical_m_s,
            descent_rate_vertical_m_s=self.descent_rate_vertical_m_s,
        )

        transition = MissionTransReq(
            transition_speed_kmh=self.transition_speed_kmh,
            transition_duration_s=self.transition_duration_s,
            transition_altitude_m=self.transition_altitude_m,
            max_transition_pitch_deg=self.max_transition_pitch_deg,
        )

        cruise = MissionCruiseReq(
            cruise_speed_kmh=self.cruise_speed_kmh,
            cruise_altitude_m=float(self.metadata.get("cruise_altitude_m", 150.0)),
            cruise_range_km=self.target_range_km,
            cruise_endurance_min=self.target_flight_time_min,
            wind_limit_cruise_kts=float(self.metadata.get("wind_limit_cruise_kts", 20.0)),
        )

        takeoff_m = TakeoffMethod.VERTICAL
        if self.takeoff_type == TakeoffType.RUNWAY:
            takeoff_m = TakeoffMethod.RUNWAY

        landing_m = LandingMethod.VERTICAL
        if self.landing_type == LandingType.RUNWAY:
            landing_m = LandingMethod.RUNWAY

        env = EnvironmentType.RURAL
        if self.environment == OperatingEnvironment.URBAN:
            env = EnvironmentType.URBAN

        meta = dict(self.metadata)
        meta["optimization_priority"] = self.optimization_priority.value
        meta["design_mode"] = self.design_mode.value
        meta["lift_motor_count"] = self.lift_motor_count
        meta["cruise_motor_count"] = self.cruise_motor_count
        if self.rotor_diameter_m is not None:
            meta["rotor_diameter_m"] = self.rotor_diameter_m
        if self.system_voltage_v is not None:
            meta["system_voltage_v"] = self.system_voltage_v
        if self.hover_thrust_to_weight_target is not None:
            meta["hover_thrust_to_weight_target"] = self.hover_thrust_to_weight_target

        return MissionRequirements(
            mission_category=category,
            vtol_type=self.vtol_type,
            payload_kg=self.payload_weight_kg,
            hover_reqs=hover,
            transition_reqs=transition,
            cruise_reqs=cruise,
            max_altitude_m=float(self.metadata.get("max_altitude_m", 1000.0)),
            environment=env,
            takeoff_method=takeoff_m,
            landing_method=landing_m,
            wind_limit_max_kts=float(self.metadata.get("wind_limit_max_kts", 22.0)),
            temperature_limit_min_c=float(self.metadata.get("temperature_limit_min_c", -10.0)),
            temperature_limit_max_c=float(self.metadata.get("temperature_limit_max_c", 40.0)),
            rain_tolerance=str(self.metadata.get("rain_tolerance", "Light")),
            autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
            safety_requirements=str(self.metadata.get("safety_requirements", "Dual GNSS and parachute backup")),
            budget=self.budget,
            manufacturing_preference=str(self.metadata.get("manufacturing_preference", "Composite")),
            metadata=meta,
        )
