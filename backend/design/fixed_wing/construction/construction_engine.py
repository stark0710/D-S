"""
Fixed-Wing Construction Configuration Selection Engine

Purpose:
    Selects or evaluates the optimal aircraft construction architecture (C1 to C6)
    based on mission requirements, operational flight envelope, and structural demands.

Role in Architecture:
    Implements the decision engine for the Construction Architecture Selection stage,
    operating in either Engineering Advisor Mode (automated scoring) or Manual Mode (user-directed).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

from backend.design.fixed_wing.construction.construction_types import (
    ConstructionConfigurationId,
    ConstructionConfigurationSpecification,
    ConstructionCatalog,
    StiffnessLevel,
    ManufacturingComplexity,
)


@dataclass(slots=True)
class ConstructionSelectionResult:
    """
    Detailed output of the Construction Configuration Selection Engine.
    """
    selected_configuration: ConstructionConfigurationSpecification
    ranked_configurations: List[Tuple[ConstructionConfigurationSpecification, float, str]]
    scores: Dict[str, float]
    rejected_configurations: List[Tuple[ConstructionConfigurationSpecification, str]]
    engineering_rationale: str
    warnings: List[str] = field(default_factory=list)
    mode: str = "ENGINEERING_ADVISOR"  # "ENGINEERING_ADVISOR" or "MANUAL"
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConstructionConfigurationSelectionEngine:
    """
    Engineering engine for selecting and scoring construction configurations.
    """

    def select_configuration(
        self,
        mission_requirements: Any,
        wing_geometry: Optional[Any] = None,
        fuselage_geometry: Optional[Any] = None,
        manual_config_id: Optional[ConstructionConfigurationId | str] = None,
    ) -> ConstructionSelectionResult:
        """
        Executes construction configuration selection.
        """
        if manual_config_id is not None:
            return self._execute_manual_mode(manual_config_id, mission_requirements, wing_geometry)
        else:
            return self._execute_advisor_mode(mission_requirements, wing_geometry, fuselage_geometry)

    def _execute_manual_mode(
        self,
        manual_config_id: ConstructionConfigurationId | str,
        mission_requirements: Any,
        wing_geometry: Optional[Any],
    ) -> ConstructionSelectionResult:
        """
        Honors explicit user selection while validating physical feasibility.
        """
        try:
            cfg = ConstructionCatalog.get(manual_config_id)
        except KeyError:
            cfg = ConstructionCatalog.C1_FOAM_CORE_COMPOSITE

        warnings: List[str] = []
        payload_kg = getattr(mission_requirements, "payload_weight_kg", 0.5) or 0.5
        speed_kmh = getattr(mission_requirements, "cruise_speed_kmh", 80.0) or 80.0
        span_m = getattr(wing_geometry, "span_m", 2.0) if wing_geometry else 2.0

        p_min, p_max = cfg.recommended_payload_range_kg
        if payload_kg > p_max * 1.2:
            warnings.append(
                f"Manual configuration '{cfg.name}' recommended max payload is {p_max:.1f} kg; "
                f"mission requires {payload_kg:.1f} kg. Spar and joint reinforcements will be necessary."
            )
        elif payload_kg < p_min * 0.5:
            warnings.append(
                f"Manual configuration '{cfg.name}' is heavier than necessary for payload {payload_kg:.2f} kg."
            )

        s_min, s_max = cfg.recommended_speed_range_kmh
        if speed_kmh > s_max:
            warnings.append(
                f"Cruise speed {speed_kmh:.1f} km/h exceeds recommended structural speed limit of {s_max:.1f} km/h "
                f"for '{cfg.name}'. Risk of aeroelastic flutter or skin deformation."
            )

        rationale = (
            f"Manual selection mode active: User explicitly designated '{cfg.name}'. "
            f"Architecture: {cfg.description}"
        )

        all_cfgs = ConstructionCatalog.get_all()
        ranked = [(c, 100.0 if c.configuration_id == cfg.configuration_id else 50.0, "Manual Selection") for c in all_cfgs]
        scores = {c.configuration_id.value: (100.0 if c.configuration_id == cfg.configuration_id else 50.0) for c in all_cfgs}

        return ConstructionSelectionResult(
            selected_configuration=cfg,
            ranked_configurations=ranked,
            scores=scores,
            rejected_configurations=[],
            engineering_rationale=rationale,
            warnings=warnings,
            mode="MANUAL",
            metadata={"user_selected_id": cfg.configuration_id.value}
        )

    def _execute_advisor_mode(
        self,
        mission_requirements: Any,
        wing_geometry: Optional[Any],
        fuselage_geometry: Optional[Any],
    ) -> ConstructionSelectionResult:
        """
        Evaluates and ranks all six configurations via multi-criteria scoring.
        """
        payload_kg = float(getattr(mission_requirements, "payload_weight_kg", 0.5) or 0.5)
        range_km = float(getattr(mission_requirements, "target_range_km", 30.0) or 30.0)
        endurance_min = float(getattr(mission_requirements, "target_flight_time_min", 30.0) or 30.0)
        speed_kmh = float(getattr(mission_requirements, "cruise_speed_kmh", 80.0) or 80.0)
        span_m = float(getattr(wing_geometry, "span_m", 2.2) if wing_geometry else 2.2)
        
        mission_type_obj = getattr(mission_requirements, "mission_type", "SURVEY")
        mission_str = mission_type_obj.value if hasattr(mission_type_obj, "value") else str(mission_type_obj).upper()

        ranked: List[Tuple[ConstructionConfigurationSpecification, float, str]] = []
        scores: Dict[str, float] = {}
        rejected: List[Tuple[ConstructionConfigurationSpecification, str]] = []
        warnings: List[str] = []

        for cfg in ConstructionCatalog.get_all():
            score = 100.0
            reasons = []
            is_rejected = False
            rejection_reason = ""

            # 1. Payload criteria
            p_min, p_max = cfg.recommended_payload_range_kg
            if payload_kg > p_max * 1.5:
                is_rejected = True
                rejection_reason = f"Payload {payload_kg:.2f} kg severely exceeds structural envelope ({p_max:.1f} kg max)."
            elif payload_kg > p_max:
                penalty = (payload_kg - p_max) * 20.0
                score -= penalty
                reasons.append(f"Payload above nominal limit (-{penalty:.1f} pts)")
            elif payload_kg < p_min * 0.6:
                penalty = 15.0
                score -= penalty
                reasons.append(f"Over-structured for small payload (-{penalty:.1f} pts)")

            # 2. Cruise Speed criteria
            s_min, s_max = cfg.recommended_speed_range_kmh
            if speed_kmh > s_max * 1.3:
                is_rejected = True
                rejection_reason = f"Cruise airspeed {speed_kmh:.1f} km/h presents severe aeroelastic flutter risk for this construction."
            elif speed_kmh > s_max:
                penalty = (speed_kmh - s_max) * 0.8
                score -= penalty
                reasons.append(f"Speed exceeds recommended aero limit (-{penalty:.1f} pts)")

            # 3. Wingspan & Aspect ratio criteria
            w_min, w_max = cfg.recommended_wingspan_range_m
            if span_m > w_max * 1.25:
                score -= 25.0
                reasons.append(f"Wingspan {span_m:.2f} m exceeds typical stiffness limit for {cfg.name}")
            elif span_m < w_min * 0.8:
                score -= 10.0

            # 4. Mission Type Alignment
            if any(m in mission_str for m in ["SURVEY", "MAPPING"]):
                # Demands high dimensional stability and vibration resistance
                if cfg.structural_stiffness_level in (StiffnessLevel.HIGH, StiffnessLevel.VERY_HIGH):
                    score += 15.0
                    reasons.append("High structural stiffness ideal for optical photogrammetry overlap (+15 pts)")
                else:
                    score -= 30.0
                    reasons.append("Insufficient stiffness for precise surveying optics (-30 pts)")
            elif "CARGO" in mission_str or "DELIVERY" in mission_str:
                if cfg.configuration_id == ConstructionConfigurationId.C1_FOAM_CORE_COMPOSITE:
                    score += 20.0
                else:
                    score -= 15.0
            elif "EDUCATIONAL" in mission_str or "HOBBY" in mission_str or "STUDENT" in mission_str:
                if cfg.manufacturing_complexity == ManufacturingComplexity.SIMPLE_HOBBY:
                    score += 30.0
                    reasons.append("Simple hobby tooling ideal for educational low-cost build (+30 pts)")
                elif cfg.manufacturing_complexity == ManufacturingComplexity.INTERMEDIATE:
                    score += 10.0
                    reasons.append("Intermediate wood/film build suitable for students (+10 pts)")
                else:
                    score -= 25.0
                    reasons.append("Advanced composite manufacturing too complex for basic student builds (-25 pts)")
            elif "RESEARCH" in mission_str:
                if cfg.manufacturing_complexity in (ManufacturingComplexity.SIMPLE_HOBBY, ManufacturingComplexity.INTERMEDIATE):
                    score += 15.0
                    reasons.append("Accessible tooling and easy repairability (+15 pts)")
            elif "SURVEILLANCE" in mission_str or "SECURITY" in mission_str:
                if payload_kg <= 0.4 and (range_km <= 15.0 or endurance_min <= 30.0):
                    if cfg.configuration_id == ConstructionConfigurationId.C3_BALSA_CARBON_SKELETON_FILM:
                        score += 25.0
                        reasons.append("Ultra-lightweight skeleton ideal for short-range low-MTOW surveillance (+25 pts)")
                    elif cfg.configuration_id == ConstructionConfigurationId.C4_FOAM_DEPRON_FILM:
                        score += 15.0
                    else:
                        score -= 10.0
                        reasons.append("Over-structured for ultra-lightweight surveillance (-10 pts)")

            # 5. Range & Endurance alignment
            if range_km > 50.0 or endurance_min > 60.0:
                if cfg.configuration_id in (ConstructionConfigurationId.C1_FOAM_CORE_COMPOSITE, ConstructionConfigurationId.C2_BALSA_SKELETON_COMPOSITE):
                    score += 15.0
                    reasons.append("High aerodynamic surface efficiency supports long-range endurance (+15 pts)")
                else:
                    score -= 20.0
                    reasons.append("Lower aerodynamic efficiency limits long-range performance (-20 pts)")

            final_score = max(0.0, min(100.0, score))
            scores[cfg.configuration_id.value] = round(final_score, 1)

            if is_rejected:
                rejected.append((cfg, rejection_reason))
            else:
                justification = "; ".join(reasons) if reasons else "Compatible with mission baseline"
                ranked.append((cfg, round(final_score, 1), justification))

        # Sort ranked list descending by score
        ranked.sort(key=lambda x: x[1], reverse=True)

        if not ranked:
            # Fallback if everything was rejected
            selected = ConstructionCatalog.C1_FOAM_CORE_COMPOSITE
            warnings.append("All configurations were marginally constrained; selected C1 Foam-Core Composite as robust baseline.")
        else:
            selected = ranked[0][0]

        rationale = (
            f"Selected construction architecture '{selected.name}' with score {scores[selected.configuration_id.value]:.1f}/100. "
            f"Rationale: {selected.description} "
            f"Matches mission category '{mission_str}', payload {payload_kg:.2f} kg, cruise speed {speed_kmh:.1f} km/h, and wingspan {span_m:.2f} m."
        )

        return ConstructionSelectionResult(
            selected_configuration=selected,
            ranked_configurations=ranked,
            scores=scores,
            rejected_configurations=rejected,
            engineering_rationale=rationale,
            warnings=warnings,
            mode="ENGINEERING_ADVISOR",
            metadata={
                "payload_kg": payload_kg,
                "range_km": range_km,
                "speed_kmh": speed_kmh,
                "span_m": span_m,
                "mission_category": mission_str,
            }
        )
