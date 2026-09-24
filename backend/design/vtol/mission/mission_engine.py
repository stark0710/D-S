"""
VTOL Mission Engine Subsystem

Purpose:
    Defines the `MissionEngine` facade class orchestrating the VTOL Mission
    Engineering Framework execution loop.
"""

from typing import List, Dict, Any
import math
from datetime import datetime

from backend.design.vtol.mission.mission_requirements import (
    MissionRequirements,
    VTOLMissionCategory,
    TakeoffMethod,
    LandingMethod,
)
from backend.design.vtol.mission.mission_profile import MissionProfile
from backend.design.vtol.mission.mission_constraints import MissionConstraints
from backend.design.vtol.mission.mission_analysis import MissionAnalysis
from backend.design.vtol.mission.mission_result import MissionResult
from backend.design.vtol.mission.mission_validator import MissionValidator
from backend.design.vtol.mission.mission_registry import VTOLMissionStrategyRegistry
from backend.design.vtol.mission.mission_state import VTOLMissionProfileSequence


class MissionEngine:
    """
    Facade orchestrator driving VTOL mission requirements collection,
    validation, and engineering analysis.
    """

    def __init__(
        self,
        validator: MissionValidator | None = None,
    ) -> None:
        self._validator = validator if validator else MissionValidator()

    def process_mission(self, requirements: MissionRequirements) -> MissionResult:
        """
        Processes and analyzes the raw VTOL mission requirements.

        Args:
            requirements (MissionRequirements): Raw inputs.

        Returns:
            MissionResult: Consolidated design parameters and energy metrics.
        """
        # 1. Validate requirements (raises MissionValidationError if invalid)
        self._validator.validate(requirements)

        # 2. Retrieve corresponding strategy
        strategy = VTOLMissionStrategyRegistry.get(requirements.mission_category)

        # 3. Calculate atmospheric densities
        rho_hover = self._calculate_air_density(requirements.hover_reqs.hover_altitude_m)
        rho_cruise = self._calculate_air_density(requirements.cruise_reqs.cruise_altitude_m)

        # 4. Preliminary MTOW Sizing
        mtow = strategy.estimate_mtow(requirements)

        # 5. Physics & Energy Estimations
        physics = strategy.estimate_physics(requirements, mtow, rho_hover, rho_cruise)

        # 6. Formulate Feasibility & Risks
        feasibility_score = 100.0
        warnings: List[str] = []
        notes: List[str] = [
            f"VTOL Mission category parsed as: {requirements.mission_category.name}.",
            f"Target VTOL layout configuration: {requirements.vtol_type.value}.",
            f"Calculated standard air density at hover ({requirements.hover_reqs.hover_altitude_m} m): {rho_hover:.4f} kg/m³.",
            f"Calculated standard air density at cruise ({requirements.cruise_reqs.cruise_altitude_m} m): {rho_cruise:.4f} kg/m³.",
            f"Sized preliminary MTOW: {mtow:.2f} kg based on payload fraction of {strategy.get_target_payload_fraction() * 100:.1f}%.",
        ]

        # Feasibility scoring deductions
        if requirements.payload_kg > 40.0:
            feasibility_score -= 15.0
            warnings.append(f"Heavy payload of {requirements.payload_kg} kg requires high lift propulsion, limiting cruise range.")
        if requirements.cruise_reqs.cruise_range_km > 200.0:
            feasibility_score -= 15.0
            warnings.append("Extreme range target (> 200 km) may exceed current lithium battery energy densities.")
        if requirements.hover_reqs.hover_duration_min > 25.0:
            feasibility_score -= 10.0
            warnings.append("Extended hover duration (> 25 min) causes high thermal buildup in VTOL motors.")
        if requirements.wind_limit_max_kts > 25.0:
            feasibility_score -= 10.0
            warnings.append(f"High wind limit ({requirements.wind_limit_max_kts} kts) demands extra yaw/roll control margins.")

        # Minimum budget warning
        if requirements.budget is not None and requirements.budget < 3000.0:
            warnings.append("Low budget allocated. Materials optimization and off-the-shelf components are recommended.")

        feasibility_score = max(10.0, min(100.0, feasibility_score))

        # Complexity category
        c_score = physics["complexity_score"]
        if c_score < 0.4:
            complexity_cat = "Low"
        elif c_score <= 0.7:
            complexity_cat = "Medium"
        else:
            complexity_cat = "High"

        # 7. Assemble Profile
        total_endurance = (
            requirements.hover_reqs.hover_duration_min
            + requirements.cruise_reqs.cruise_endurance_min
            + (requirements.transition_reqs.transition_duration_s / 60.0)
        )

        profile = MissionProfile(
            mission_category=requirements.mission_category,
            vtol_type=requirements.vtol_type,
            payload_kg=requirements.payload_kg,
            total_endurance_min=round(total_endurance, 2),
            total_range_km=requirements.cruise_reqs.cruise_range_km,
            air_density_hover_kg_m3=round(rho_hover, 4),
            air_density_cruise_kg_m3=round(rho_cruise, 4),
            energy_demand_hover_kwh=physics["energy_hover_kwh"],
            energy_demand_cruise_kwh=physics["energy_cruise_kwh"],
            energy_demand_transition_kwh=physics["energy_transition_kwh"],
            total_energy_demand_kwh=physics["total_energy_kwh"],
            complexity_score=c_score,
            complexity_category=complexity_cat,
            metadata={"estimated_hover_power_w": physics["power_hover_w"], "estimated_cruise_power_w": physics["power_cruise_w"]},
        )

        # 8. Assemble Analysis
        analysis = MissionAnalysis(
            hover_priority=strategy.get_hover_priority(),
            cruise_priority=strategy.get_cruise_priority(),
            transition_complexity=strategy.get_transition_complexity(),
            estimated_mtow_kg=round(mtow, 2),
            lift_to_drag_ratio_est=strategy.get_lift_to_drag_ratio(),
            hover_thrust_to_weight_est=strategy.get_hover_thrust_to_weight(),
            mission_energy_demand_kwh=physics["total_energy_kwh"],
            mission_risk_score=physics["risk_score"],
            mission_feasibility_score=feasibility_score,
            metadata={"estimated_hover_power_w": physics["power_hover_w"], "estimated_cruise_power_w": physics["power_cruise_w"]},
        )

        # 9. Recommendations
        recs = strategy.get_recommendations(requirements, profile)
        if requirements.takeoff_method == TakeoffMethod.VERTICAL:
            recs.append("Configure a multi-rotor altitude hold controller for autonomous hover climbout.")
        if requirements.landing_method == LandingMethod.VERTICAL:
            recs.append("Verify failsafe return-to-land hover locations have clear sensor visibility.")

        # Construct authoritative 10-phase mission sequence representation
        mission_seq = VTOLMissionProfileSequence.build_default_sequence(
            hover_duration_min=float(requirements.hover_reqs.hover_duration_min),
            transition_duration_s=float(requirements.transition_reqs.transition_duration_s),
            cruise_endurance_min=float(requirements.cruise_reqs.cruise_endurance_min),
            cruise_speed_kmh=float(requirements.cruise_reqs.cruise_speed_kmh),
            transition_speed_kmh=float(requirements.transition_reqs.transition_speed_kmh),
            hover_altitude_m=float(requirements.hover_reqs.hover_altitude_m),
            cruise_altitude_m=float(requirements.cruise_reqs.cruise_altitude_m),
        )

        # Metadata info
        meta = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.__class__.__name__,
        }

        return MissionResult(
            mission_profile=profile,
            hover_requirements=requirements.hover_reqs,
            transition_requirements=requirements.transition_reqs,
            cruise_requirements=requirements.cruise_reqs,
            mission_analysis=analysis,
            mission_sequence=mission_seq,
            engineering_notes=notes,
            recommendations=recs,
            warnings=warnings,
            metadata=meta,
        )

    def _calculate_air_density(self, altitude_m: float) -> float:
        """
        Computes standard atmosphere (ISA) density in kg/m³ for a given altitude.
        """
        rho_sl = 1.225
        if altitude_m <= 0.0:
            return rho_sl
        # ISA temperature lapse rate approximation
        temp_k = 288.15 - 0.0065 * altitude_m
        pressure_pa = 101325.0 * math.pow((temp_k / 288.15), 5.25588)
        density = pressure_pa / (287.05 * temp_k)
        return density
