"""
VTOL Tail Sizing Result Subsystem

Purpose:
    Defines the consolidated `TailResult` dataclass outputted by the tail stage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from backend.design.vtol.tail.tail_geometry import TailGeometry
from backend.design.vtol.tail.tail_structure import TailStructure
from backend.design.vtol.tail.tail_controls import TailControls
from backend.design.vtol.tail.tail_analysis import TailStabilityAnalysis, TailControlAnalysis


@dataclass(slots=True)
class TailResult:
    """
    Consolidated tail sizing package detailing geometry, controls, and stability.

    Attributes:
        tail_geometry (TailGeometry): Sized stabilizer areas and spans.
        tail_structure (TailStructure): Weight and boom dimensions.
        control_surfaces (TailControls): Sized elevators/rudders and mixing type.
        stability_analysis (TailStabilityAnalysis): static margins and G capability.
        control_analysis (TailControlAnalysis): Control effectiveness and wash effects.
        engineering_notes (List[str]): Sizing observations.
        recommendations (List[str]): Downstream recommendations.
        warnings (List[str]): Stability margin warnings.
        metadata (Dict[str, Any]): execution timestamps and versions.
    """

    tail_geometry: TailGeometry
    tail_structure: TailStructure
    control_surfaces: TailControls
    stability_analysis: TailStabilityAnalysis
    control_analysis: TailControlAnalysis
    authoritative_stability_result: Any = None
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "tail_geometry": {
                "tail_configuration": self.tail_geometry.tail_configuration,
                "tail_arm_m": self.tail_geometry.tail_arm_m,
                "horizontal_area_m2": self.tail_geometry.horizontal_area_m2,
                "horizontal_span_m": self.tail_geometry.horizontal_span_m,
                "horizontal_aspect_ratio": self.tail_geometry.horizontal_aspect_ratio,
                "vertical_area_m2": self.tail_geometry.vertical_area_m2,
                "vertical_span_m": self.tail_geometry.vertical_span_m,
                "vertical_aspect_ratio": self.tail_geometry.vertical_aspect_ratio,
                "v_tail_angle_deg": self.tail_geometry.v_tail_angle_deg,
                "metadata": dict(self.tail_geometry.metadata),
            },
            "tail_structure": {
                "structural_concept": self.tail_structure.structural_concept,
                "estimated_tail_weight_kg": self.tail_structure.estimated_tail_weight_kg,
                "boom_diameter_mm": self.tail_structure.boom_diameter_mm,
                "boom_material": self.tail_structure.boom_material,
                "metadata": dict(self.tail_structure.metadata),
            },
            "control_surfaces": {
                "elevator_area_m2": self.control_surfaces.elevator_area_m2,
                "elevator_span_m": self.control_surfaces.elevator_span_m,
                "rudder_area_m2": self.control_surfaces.rudder_area_m2,
                "rudder_span_m": self.control_surfaces.rudder_span_m,
                "control_mixing_type": self.control_surfaces.control_mixing_type,
                "metadata": dict(self.control_surfaces.metadata),
            },
            "stability_analysis": {
                "longitudinal_stability_score": self.stability_analysis.longitudinal_stability_score,
                "directional_stability_score": self.stability_analysis.directional_stability_score,
                "static_margin_percent": self.stability_analysis.static_margin_percent,
                "neutral_point_percent": self.stability_analysis.neutral_point_percent,
                "trim_capability_deg": self.stability_analysis.trim_capability_deg,
                "metadata": dict(self.stability_analysis.metadata),
            },
            "control_analysis": {
                "pitch_effectiveness": self.control_analysis.pitch_effectiveness,
                "yaw_effectiveness": self.control_analysis.yaw_effectiveness,
                "transition_authority": self.control_analysis.transition_authority,
                "rotor_downwash_interference_index": self.control_analysis.rotor_downwash_interference_index,
                "slipstream_influence_factor": self.control_analysis.slipstream_influence_factor,
                "hover_mode_control_authority": self.control_analysis.hover_mode_control_authority,
                "metadata": dict(self.control_analysis.metadata),
            },
            "engineering_notes": list(self.engineering_notes),
            "recommendations": list(self.recommendations),
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }
        if self.authoritative_stability_result is not None:
            if hasattr(self.authoritative_stability_result, "to_dict"):
                data["authoritative_stability_result"] = self.authoritative_stability_result.to_dict()
            else:
                data["authoritative_stability_result"] = self.authoritative_stability_result
        return data
