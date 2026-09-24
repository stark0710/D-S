"""
Fixed-Wing Wing Sizer Subsystem

Purpose:
    Defines the `WingSizer` class, which handles the core calculations for wing area, span, and aspect ratio.

Role in Architecture:
    `WingSizer` translates aerodynamic requirements (stall speed, MTOW, density) into
    wing planform area and aspect ratio values using physics-based sizing formulas.
"""

import math
from typing import Dict, Any
from backend.design.fixed_wing.wing.wing_requirements import WingRequirements, PlanformType
from backend.design.fixed_wing.wing.wing_geometry import WingGeometry
from backend.design.fixed_wing.wing.wing_constraints import WingConstraints
from backend.design.fixed_wing.wing.wing_structure_interface import WingStructureInterface


class DefaultWingStructure(WingStructureInterface):
    """
    Default structural estimator for wings, assuming standard composite/aluminum materials.
    """

    def estimate_wing_weight_kg(
        self, geometry: WingGeometry, design_load_factor: float, structural_factor: float = 1.0
    ) -> float:
        # Empirically based fixed-wing UAV wing weight estimation:
        # weight = structural_factor * (span * area^0.5 * design_load_factor^0.5 * 0.15)
        # Sized for typical light UAV weight fractions.
        weight = structural_factor * (geometry.span_m * math.sqrt(geometry.area_m2) * math.sqrt(design_load_factor) * 0.22)
        return round(weight, 3)

    def evaluate_structural_feasibility(
        self, geometry: WingGeometry, mtow_kg: float, design_load_factor: float
    ) -> Dict[str, Any]:
        # Maximum bending moment estimate at wing root (semi-span cantilever beam):
        # M_root = (MTOW * g * load_factor) * (span / 4) * 0.5 (triangular lift distribution)
        g = 9.80665
        total_lift_n = mtow_kg * g * design_load_factor
        bending_moment_nm = (total_lift_n / 2.0) * (geometry.span_m / 4.0) * 0.5 # approximation

        # Structural efficiency: ratio of lift capability to wing weight
        wing_weight = self.estimate_wing_weight_kg(geometry, design_load_factor)
        efficiency = (mtow_kg * design_load_factor) / max(0.1, wing_weight)

        # Suggested spar thickness: mock estimation for illustration
        spar_thickness = (bending_moment_nm / 1e5) * 5.0 + 1.0

        return {
            "is_feasible": wing_weight < (mtow_kg * 0.25),  # Wing shouldn't exceed 25% of MTOW
            "structural_efficiency": round(efficiency, 2),
            "max_bending_moment_nm": round(bending_moment_nm, 2),
            "suggested_spar_thickness_mm": round(spar_thickness, 2),
        }


class WingSizer:
    """
    Sizing service responsible for solving wing area and aspect ratio equations.
    """

    def __init__(self, structure_evaluator: WingStructureInterface | None = None) -> None:
        self._structure = structure_evaluator if structure_evaluator else DefaultWingStructure()

    def size_wing(
        self,
        requirements: WingRequirements,
        constraints: WingConstraints,
        target_aspect_ratio: float,
        typical_wing_loading_kg_m2: float,
    ) -> Dict[str, float]:
        """
        Solves wing equations based on stall constraints, MTOW, and aspect ratio.
        """
        mission_profile = requirements.mission_result.mission_profile
        g = 9.80665

        # 1. Estimate MTOW
        # Reconcile MTOW from current iteration state, mass result, seed, or user constraint
        if getattr(mission_profile, "current_iteration_mtow_kg", None) is not None:
            mtow_kg = mission_profile.current_iteration_mtow_kg
        elif hasattr(requirements, "mass_result") and getattr(requirements, "mass_result", None) is not None:
            mass_res = getattr(requirements, "mass_result")
            mtow_kg = getattr(mass_res, "maximum_takeoff_weight_kg", None) or sum(c.mass_kg for c in mass_res.component_masses)
        elif getattr(mission_profile, "initial_mtow_seed_kg", None) is not None:
            mtow_kg = mission_profile.initial_mtow_seed_kg
        elif mission_profile.maximum_takeoff_weight_limit_kg is not None:
            mtow_kg = mission_profile.maximum_takeoff_weight_limit_kg
        else:
            mtow_kg = max(2.0, mission_profile.payload_kg * 3.5)

        # Ensure we have a valid MTOW
        mtow_kg = max(1.0, mtow_kg)

        # 2. Determine Wing Loading based on Stall Speed
        rho = mission_profile.air_density_kg_m3
        c_l_max = 1.4  # typical maximum lift coefficient for clean UAV wing

        # If stall speed is specified
        if mission_profile.stall_speed_target_kmh:
            v_stall_m_s = mission_profile.stall_speed_target_kmh / 3.6
            # W/S = 0.5 * rho * V_stall^2 * C_L_max
            wing_loading_n_m2 = 0.5 * rho * (v_stall_m_s**2) * c_l_max
            wing_loading_kg_m2 = wing_loading_n_m2 / g
        else:
            # Fallback to speed-derived or typical strategy value
            v_cruise_m_s = mission_profile.cruise_speed_kmh / 3.6
            v_stall_m_s = v_cruise_m_s / 1.5
            wing_loading_n_m2 = 0.5 * rho * (v_stall_m_s**2) * c_l_max
            wing_loading_kg_m2 = wing_loading_n_m2 / g

        # Reconcile user overrides
        if requirements.preferred_wing_loading is not None:
            wing_loading_kg_m2 = requirements.preferred_wing_loading

        # Apply constraints
        wing_loading_kg_m2 = max(
            constraints.min_wing_loading_kg_m2,
            min(constraints.max_wing_loading_kg_m2, wing_loading_kg_m2)
        )

        # 3. Calculate Wing Area
        area_m2 = mtow_kg / wing_loading_kg_m2

        # 4. Aspect Ratio selection
        aspect_ratio = target_aspect_ratio
        if requirements.preferred_aspect_ratio is not None:
            aspect_ratio = requirements.preferred_aspect_ratio

        aspect_ratio = max(
            constraints.min_aspect_ratio,
            min(constraints.max_aspect_ratio, aspect_ratio)
        )

        # Enforce geometric root chord compatibility constraint if specified
        if getattr(constraints, "min_root_chord_m", None) is not None and constraints.min_root_chord_m > 0.0:
            # Conservative tapered upper bound for aspect ratio:
            # c_root = 2*sqrt(S) / (sqrt(AR)*(1+lambda)) >= min_root_chord
            # Assuming average taper lambda ~ 0.5: 1+lambda = 1.5
            req_chord = constraints.min_root_chord_m
            max_ar_geom = ((2.0 * math.sqrt(area_m2)) / (req_chord * 1.5)) ** 2
            if max_ar_geom >= constraints.min_aspect_ratio:
                aspect_ratio = min(aspect_ratio, max_ar_geom)

        # 5. Wingspan calculations
        # b = sqrt(S * AR)
        span = math.sqrt(area_m2 * aspect_ratio)

        # Reconcile wingspan constraints (e.g. storage/regulation limit)
        if constraints.max_wingspan_m is not None and span > constraints.max_wingspan_m:
            span = constraints.max_wingspan_m
            # Re-adjust aspect ratio to maintain required area: AR = b^2 / S
            aspect_ratio = (span**2) / area_m2

        return {
            "area_m2": round(area_m2, 4),
            "aspect_ratio": round(aspect_ratio, 4),
            "span_m": round(span, 4),
            "wing_loading_kg_m2": round(wing_loading_kg_m2, 4),
            "mtow_kg": round(mtow_kg, 4),
        }
