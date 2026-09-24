"""
Fixed-Wing Tail Analysis Subsystem

Purpose:
    Defines the `TailAnalysis` class and the `TailAnalysisService` class
    to conduct tail stability volume calculations and trim capability assessments.

Role in Architecture:
    `TailAnalysisService` evaluates pitched/yaw stability margins and control surface authority indices,
    representing them inside `TailAnalysis`.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class TailAnalysis:
    """
    aerodynamic and control authority analysis metrics for the empennage.

    Attributes:
        horizontal_volume_coefficient (float): Sized horizontal tail volume coefficient (V_h).
        vertical_volume_coefficient (float): Sized vertical tail volume coefficient (V_v).
        pitch_stability_rating (str): Stability classification for pitching.
        yaw_stability_rating (str): Stability classification for yawing.
        pitch_control_authority (float): Pitch authority score (0.0 to 100.0).
        yaw_control_authority (float): Yaw authority score (0.0 to 100.0).
        trim_capability (str): Trim authority review (e.g. "Excellent", "High trim drag").
        structural_simplicity_score (float): Ease of mounting score (0.0 to 100.0).
        manufacturability_score (float): Ease of fabrication score (0.0 to 100.0).
        mission_suitability (float): Suitability score for design category targets (0.0 to 100.0).
        analysis_details (Dict[str, float]): Any extra metrics.
    """

    horizontal_volume_coefficient: float
    vertical_volume_coefficient: float
    pitch_stability_rating: str
    yaw_stability_rating: str
    pitch_control_authority: float
    yaw_control_authority: float
    trim_capability: str
    structural_simplicity_score: float
    manufacturability_score: float
    mission_suitability: float
    analysis_details: Dict[str, float] = field(default_factory=dict)


class TailAnalysisService:
    """
    aerodynamic analyzer calculating stability indexes and checking trim margins.
    """

    def analyze_tail_performance(
        self,
        wing_area_m2: float,
        mac_m: float,
        span_m: float,
        horizontal_area_m2: float,
        vertical_area_m2: float,
        tail_arm_m: float,
        tail_style: str,
        elevator_chord_ratio: float,
        rudder_chord_ratio: float,
        c_m0: float = -0.05,
    ) -> TailAnalysis:
        """
        Calculates tail volume coefficients and evaluates pitching/yaw authority and trim limits.
        """
        # Volume coefficient calculations
        # V_h = (S_h * l_t) / (S * c_mac)
        v_h = (horizontal_area_m2 * tail_arm_m) / (wing_area_m2 * mac_m)

        # V_v = (S_v * l_t) / (S * b)
        v_v = (vertical_area_m2 * tail_arm_m) / (wing_area_m2 * span_m)

        # 1. Pitch stability rating
        if v_h >= 0.55:
            pitch_stability_rating = "Excellent (Highly stable, gentle stall recovery)"
        elif v_h >= 0.40:
            pitch_stability_rating = "Good (Standard utility aircraft stability)"
        else:
            pitch_stability_rating = "Moderate (High pitch agility, low damping)"

        # 2. Yaw stability rating
        if v_v >= 0.045:
            yaw_stability_rating = "Excellent (Stable, good spiral damping)"
        elif v_v >= 0.030:
            yaw_stability_rating = "Good (Standard directional tracking)"
        else:
            yaw_stability_rating = "Moderate (Agile yaw, risk of Dutch Roll)"

        # 3. Control surface authority
        # Elevators typically cover 25-35% chord.
        pitch_control = 50.0 + (elevator_chord_ratio - 0.20) * 250.0
        pitch_control = max(0.0, min(100.0, pitch_control))

        yaw_control = 50.0 + (rudder_chord_ratio - 0.20) * 250.0
        yaw_control = max(0.0, min(100.0, yaw_control))

        # 4. Trim capability
        # A highly negative c_m0 requires higher V_h or elevator deflection to trim.
        if abs(c_m0) > 0.11 and v_h < 0.50:
            trim_capability = "Poor (High negative moment requires large deflection, high trim drag)"
        elif abs(c_m0) > 0.08 and v_h < 0.40:
            trim_capability = "Moderate (Elevator deflection required to trim)"
        else:
            trim_capability = "Excellent (Minimal trim drag penalty)"

        # 5. Structural Simplicity & Manufacturability
        structural_simplicity_score = 80.0
        manufacturability_score = 80.0

        if tail_style == "Conventional":
            structural_simplicity_score = 95.0
            manufacturability_score = 95.0
        elif tail_style == "V-Tail":
            structural_simplicity_score = 85.0
            manufacturability_score = 75.0  # V-tail mixers are harder to build
        elif tail_style == "Inverted V-Tail":
            structural_simplicity_score = 80.0
            manufacturability_score = 70.0  # Inverted V-tail is complex to mount and mix
        elif tail_style == "T-Tail":
            structural_simplicity_score = 70.0  # High structural moment at top of fin
            manufacturability_score = 80.0
        elif tail_style in ("Twin Boom", "Twin Tail"):
            structural_simplicity_score = 65.0
            manufacturability_score = 70.0

        # 6. Mission Suitability (stub value, Strategy overrides this)
        mission_suitability = 85.0

        return TailAnalysis(
            horizontal_volume_coefficient=round(v_h, 3),
            vertical_volume_coefficient=round(v_v, 3),
            pitch_stability_rating=pitch_stability_rating,
            yaw_stability_rating=yaw_stability_rating,
            pitch_control_authority=round(pitch_control, 1),
            yaw_control_authority=round(yaw_control, 1),
            trim_capability=trim_capability,
            structural_simplicity_score=structural_simplicity_score,
            manufacturability_score=manufacturability_score,
            mission_suitability=mission_suitability,
            analysis_details={
                "pitch_volume_coefficient": round(v_h, 4),
                "yaw_volume_coefficient": round(v_v, 4),
            }
        )
