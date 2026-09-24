"""
Fixed-Wing Wing Analysis Subsystem

Purpose:
    Defines the `WingAnalysis` dataclass and the `WingAnalysisService` class
    to evaluate aerodynamic, structural, and cruise performance parameters.

Role in Architecture:
    `WingAnalysisService` acts as a domain service to perform wing performance checks,
    filling the `WingAnalysis` structure.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Any
from backend.design.fixed_wing.wing.wing_geometry import WingGeometry
from backend.design.fixed_wing.wing.wing_requirements import WingRequirements, PlanformType


@dataclass(slots=True)
class WingAnalysis:
    """
    Aerodynamic, structural, and operational performance analysis metrics for the wing.

    Attributes:
        wing_loading_rating (str): Description of the wing loading (e.g. "Low", "Moderate", "High").
        lift_coefficient_cruise (float): Required cruise lift coefficient (C_L_cruise).
        estimated_stall_speed_kmh (float): Estimated wing stall speed in km/h based on assumed C_L_max.
        aerodynamic_efficiency_score (float): Sized wing aerodynamic efficiency rating (0.0 to 100.0).
        structural_efficiency_score (float): Sized wing structural efficiency rating (0.0 to 100.0).
        manufacturability_score (float): Ease of fabrication score (0.0 to 100.0).
        stall_characteristics_rating (str): Stall behavior rating (e.g. "Gentle tip-stall margin", "Rapid stall").
        cruise_suitability (float): Suitability score for cruise speed targets (0.0 to 100.0).
        endurance_suitability (float): Suitability score for endurance targets (0.0 to 100.0).
        payload_suitability (float): Suitability score for lifting payload constraints (0.0 to 100.0).
        analysis_details (Dict[str, float]): Any extra metrics.
    """

    wing_loading_rating: str
    lift_coefficient_cruise: float
    estimated_stall_speed_kmh: float
    aerodynamic_efficiency_score: float
    structural_efficiency_score: float
    manufacturability_score: float
    stall_characteristics_rating: str
    cruise_suitability: float
    endurance_suitability: float
    payload_suitability: float
    analysis_details: Dict[str, float] = field(default_factory=dict)


class WingAnalysisService:
    """
    Engineering evaluator for wing lift capability, stall behavior, and performance scores.
    """

    def analyze_wing(
        self,
        requirements: WingRequirements,
        geometry: WingGeometry,
        mtow_kg: float,
        structural_results: Dict[str, Any],
    ) -> WingAnalysis:
        """
        Runs the performance analysis for the sized wing.

        Args:
            requirements (WingRequirements): Input constraints.
            geometry (WingGeometry): Sized geometry.
            mtow_kg (float): Total mass under test.
            structural_results (Dict[str, Any]): Wing structural limits.

        Returns:
            WingAnalysis: Sized wing performance review.
        """
        g = 9.80665
        profile = requirements.mission_result.mission_profile
        rho = profile.air_density_kg_m3
        v_cruise_m_s = profile.cruise_speed_kmh / 3.6

        # 1. Cruise Lift Coefficient: C_L = (MTOW * g) / (0.5 * rho * V_cruise^2 * S)
        dynamic_pressure = 0.5 * rho * (v_cruise_m_s**2)
        lift_coefficient_cruise = (mtow_kg * g) / (dynamic_pressure * geometry.area_m2)

        # 2. Estimated Stall Speed: V_stall = sqrt( 2 * W / (rho * S * C_L_max) )
        # Assume clean wing C_L_max = 1.3
        c_l_max = 1.3
        v_stall = math.sqrt((2.0 * mtow_kg * g) / (rho * geometry.area_m2 * c_l_max))
        estimated_stall_speed_kmh = v_stall * 3.6

        # 3. Wing loading rating
        wl = geometry.wing_loading_kg_m2
        if wl < 10.0:
            wing_loading_rating = "Low (Glider/Trainer class)"
        elif wl < 25.0:
            wing_loading_rating = "Moderate (Survey/Utility class)"
        else:
            wing_loading_rating = "High (Cargo/Speed class)"

        # 4. Aerodynamic Efficiency Score (Heuristics)
        # Higher aspect ratio increases efficiency
        aero_score = 50.0 + (geometry.aspect_ratio - 4.0) * 2.5
        planform = requirements.preferred_planform or PlanformType.TAPERED
        if planform == PlanformType.ELLIPTICAL:
            aero_score += 10.0
        elif planform == PlanformType.TAPERED:
            aero_score += 5.0
        elif planform == PlanformType.RECTANGULAR:
            aero_score -= 5.0
        aero_score = max(0.0, min(100.0, aero_score))

        # 5. Structural Efficiency Score
        # Higher aspect ratio means high bending moments -> lower structural efficiency (higher weight)
        struct_score = 95.0 - (geometry.aspect_ratio - 4.0) * 3.0
        if planform in (PlanformType.TAPERED, PlanformType.TRAPEZOIDAL):
            struct_score += 5.0  # Taper reduces tip bending moment
        struct_score = max(0.0, min(100.0, struct_score))

        # 6. Manufacturability
        if planform == PlanformType.RECTANGULAR:
            mfg_score = 95.0
        elif planform in (PlanformType.TAPERED, PlanformType.TRAPEZOIDAL):
            mfg_score = 80.0
        elif planform == PlanformType.ELLIPTICAL:
            mfg_score = 35.0  # Curved spars/leading edges are very hard to build
        else:
            mfg_score = 65.0

        # 7. Stall characteristics
        if planform == PlanformType.RECTANGULAR:
            stall_characteristics_rating = "Excellent (Stalls at root first, maintains aileron control)"
        elif planform == PlanformType.ELLIPTICAL:
            stall_characteristics_rating = "Moderate (Stalls uniformly across span)"
        else:
            stall_characteristics_rating = "Good (Minor tip-stall risk, recommend washout twist)"

        # 8. Suitability scores
        cruise_suitability = 80.0
        if wl > 20.0:
            cruise_suitability += 10.0  # higher loading is better in gusty cruise conditions

        endurance_suitability = 70.0
        if geometry.aspect_ratio > 12.0:
            endurance_suitability += 20.0
        if wl < 12.0:
            endurance_suitability += 10.0

        payload_suitability = 60.0
        if wl > 15.0:
            payload_suitability += 20.0
        if structural_results.get("is_feasible", True):
            payload_suitability += 10.0

        cruise_suitability = max(0.0, min(100.0, cruise_suitability))
        endurance_suitability = max(0.0, min(100.0, endurance_suitability))
        payload_suitability = max(0.0, min(100.0, payload_suitability))

        return WingAnalysis(
            wing_loading_rating=wing_loading_rating,
            lift_coefficient_cruise=round(lift_coefficient_cruise, 4),
            estimated_stall_speed_kmh=round(estimated_stall_speed_kmh, 2),
            aerodynamic_efficiency_score=round(aero_score, 2),
            structural_efficiency_score=round(struct_score, 2),
            manufacturability_score=round(mfg_score, 2),
            stall_characteristics_rating=stall_characteristics_rating,
            cruise_suitability=round(cruise_suitability, 2),
            endurance_suitability=round(endurance_suitability, 2),
            payload_suitability=round(payload_suitability, 2),
            analysis_details={
                "dynamic_pressure_pa": round(dynamic_pressure, 2),
                "structural_efficiency_ratio": structural_results.get("structural_efficiency", 1.0),
            }
        )
