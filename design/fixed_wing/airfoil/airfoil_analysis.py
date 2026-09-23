"""
Fixed-Wing Airfoil Analysis Subsystem

Purpose:
    Defines the `AirfoilAnalysis` dataclass and the `AirfoilAnalysisService` class
    to conduct aerodynamic efficiency and moment checks.

Role in Architecture:
    Combines the results of polar computations and Reynolds analysis into high-level, human-readable
    performance evaluations (stall, cruise stability, moment implications).
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from backend.design.fixed_wing.airfoil.airfoil_database import AirfoilRecord
from backend.design.fixed_wing.airfoil.polar_analysis import PolarData
from backend.design.fixed_wing.airfoil.reynolds_analysis import ReynoldsAnalysis


@dataclass(slots=True)
class AirfoilAnalysis:
    """
    aerodynamic analysis compiling section drag, moments, and speed sensitivity.

    Attributes:
        cruise_efficiency_score (float): Cruise L/D section ratio.
        low_speed_performance (str): Evaluation of stall and low-speed flight lift capability.
        high_speed_performance (str): Evaluation of high-speed drag profiles.
        reynolds_sensitivity (str): Sensitivity classification (e.g. "Low sensitivity", "High laminar separation bubble risk").
        stall_behavior_description (str): Description of stall onset characteristics.
        moment_implication_warning (str | None): Safety warning about horizontal tail trim loads due to C_m0.
        analysis_summary (str): textual summary of the wing airfoil sizing metrics.
    """

    cruise_efficiency_score: float
    low_speed_performance: str
    high_speed_performance: str
    reynolds_sensitivity: str
    stall_behavior_description: str
    moment_implication_warning: str | None
    analysis_summary: str


class AirfoilAnalysisService:
    """
    Aerodynamic advisor analyzing moment loads and flight envelope efficiency.
    """

    def analyze_airfoil_performance(
        self,
        airfoil: AirfoilRecord,
        polar_root: PolarData,
        polar_tip: PolarData,
        reynolds: ReynoldsAnalysis,
    ) -> AirfoilAnalysis:
        # 1. Cruise efficiency (based on mean/root)
        cruise_eff = polar_root.cruise_l_d

        # 2. Low speed performance
        cl_max = polar_root.max_lift_coeff
        if cl_max > 1.6:
            low_speed_performance = "Excellent (Ultra high lift section, ideal for short field cargo)"
        elif cl_max > 1.3:
            low_speed_performance = "Good (Solid maximum lift capability, docile slow speed holding)"
        else:
            low_speed_performance = "Moderate (Low lift capability, requires higher landing speeds)"

        # 3. High speed performance
        cd_min = airfoil.c_d0_ref
        if cd_min < 0.006:
            high_speed_performance = "Excellent (Very low drag coefficient, laminar flow section)"
        elif cd_min < 0.010:
            high_speed_performance = "Good (Moderate drag profile)"
        else:
            high_speed_performance = "Poor (High profile drag, not suited for high-speed flight)"

        # 4. Reynolds sensitivity
        # check difference in Cd at stall Re vs cruise Re at Cl=0.4
        cd_low_re = airfoil.get_drag_coefficient(0.4, reynolds.re_root_stall)
        cd_high_re = airfoil.get_drag_coefficient(0.4, reynolds.re_root_cruise)
        drag_increase_ratio = (cd_low_re - cd_high_re) / cd_high_re
        if drag_increase_ratio > 0.35:
            reynolds_sensitivity = "High sensitivity (Risk of laminar separation bubbles or stall at low Reynolds numbers)"
        else:
            reynolds_sensitivity = "Low sensitivity (Stable boundary layer transition)"

        # 5. Stall behavior description
        if airfoil.airfoil_type == "Symmetrical":
            stall_desc = "Docile and symmetric stall characteristics, with gradual recovery."
        elif airfoil.thickness_ratio > 0.12:
            stall_desc = "Gentle stall characteristics due to thick leading edge radius."
        else:
            stall_desc = "Sharp stall characteristic. Washout twist is highly recommended to protect tip region."

        # 6. Pitching moment warning
        c_m0 = airfoil.c_m0
        if c_m0 < -0.10:
            moment_warning = (
                f"Airfoil has a high negative pitching moment (C_m0 = {c_m0}). "
                "Requires a larger tail volume or longer tail boom to balance pitching loads, increasing trim drag."
            )
        elif c_m0 > 0.0:
            moment_warning = (
                f"Airfoil has a positive pitching moment (C_m0 = {c_m0}), which is self-stabilizing. "
                "Ideal for tailless or flying wing configurations."
            )
        else:
            moment_warning = None

        # 7. Summary
        summary = (
            f"Airfoil '{airfoil.name}' evaluated. Cruise section efficiency: L/D = {cruise_eff:.1f}. "
            f"Max lift coefficient: Cl_max = {cl_max:.2f}. Zero-lift moment: C_m0 = {c_m0:.3f}."
        )

        return AirfoilAnalysis(
            cruise_efficiency_score=round(cruise_eff, 2),
            low_speed_performance=low_speed_performance,
            high_speed_performance=high_speed_performance,
            reynolds_sensitivity=reynolds_sensitivity,
            stall_behavior_description=stall_desc,
            moment_implication_warning=moment_warning,
            analysis_summary=summary,
        )
