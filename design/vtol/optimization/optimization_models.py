"""
VTOL Optimization Domain Models.

Purpose:
    Typed dataclasses defining candidate designs, evaluation metrics,
    Pareto states, and consolidated optimization results for the Phase 7
    Multidisciplinary Optimization & Pareto Analysis framework.
"""

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Dict, List, Optional


class OptimizationStatus(str, Enum):
    """Overall status of multi-objective design optimization."""
    SUCCESS = "SUCCESS"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    NO_FEASIBLE_CANDIDATES = "NO_FEASIBLE_CANDIDATES"
    NO_FEASIBLE_DESIGNS = "NO_FEASIBLE_DESIGNS"
    FAILED = "FAILED"


class EvaluationStatus(str, Enum):
    """Feasibility and calculation status for an individual candidate."""
    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    EVALUATION_ERROR = "EVALUATION_ERROR"


class OptimizationProvenance(str, Enum):
    """Parameter provenance classifications."""
    DERIVED = "DERIVED"
    PROJECT_REQUIREMENT = "PROJECT_REQUIREMENT"
    CONFIGURABLE_ASSUMPTION = "CONFIGURABLE_ASSUMPTION"
    ASSUMPTION_BASED = "ASSUMPTION_BASED"
    UNRESOLVED_INPUT = "UNRESOLVED_INPUT"
    DEFERRED = "DEFERRED"


@dataclass(slots=True)
class DesignCandidate:
    """A distinct set of design variables and requirements defining a single evaluation candidate."""
    candidate_id: str
    variables: Dict[str, float]
    mission_overrides: Dict[str, Any] = field(default_factory=dict)
    candidate_hash: str = ""

    def __post_init__(self) -> None:
        if not self.candidate_hash:
            # Deterministic hash based on rounded values to prevent float representation noise
            var_repr = json.dumps({k: round(float(v), 4) for k, v in sorted(self.variables.items())}, sort_keys=True)
            miss_repr = json.dumps({k: str(v) for k, v in sorted(self.mission_overrides.items())}, sort_keys=True)
            combined = f"{var_repr}|{miss_repr}"
            self.candidate_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "candidate_hash": self.candidate_hash,
            "variables": {k: round(v, 4) for k, v in self.variables.items()},
            "mission_overrides": self.mission_overrides,
        }


@dataclass(slots=True)
class DesignEvaluation:
    """Complete multidisciplinary evaluation result for a single candidate."""
    candidate_id: str
    candidate_hash: str
    variables: Dict[str, float] = field(default_factory=dict)
    mission_inputs: Dict[str, Any] = field(default_factory=dict)
    status: EvaluationStatus = EvaluationStatus.FEASIBLE

    # Mass & CG outputs (Phase 5)
    mtow_kg: float = 0.0
    empty_mass_kg: float = 0.0
    payload_mass_kg: float = 0.0
    battery_mass_kg: float = 0.0
    cg_x_m: float = 0.0
    cg_pct_mac: float = 0.0

    # Aerodynamics & Stability outputs (Phase 6)
    neutral_point_x_m: float = 0.0
    static_margin_fraction: float = 0.0
    static_margin_pct: float = 0.0
    is_statically_stable: bool = False
    vtail_area_m2: float = 0.0
    vtail_dihedral_deg: float = 0.0
    ruddervator_area_m2: float = 0.0
    aileron_area_m2: float = 0.0

    # Derivatives (Phase 6)
    c_m_alpha_per_rad: float = 0.0
    c_m_delta_e_per_rad: float = 0.0
    c_n_beta_per_rad: float = 0.0
    c_n_delta_r_per_rad: float = 0.0
    c_l_beta_per_rad: float = 0.0
    c_l_delta_a_per_rad: float = 0.0

    # Control & Trim outputs (Phase 6)
    trim_status: str = "TRIM_UNRESOLVED"
    cruise_trim_elevator_deg: float = 0.0
    control_authority_status: str = "AUTHORITY_UNRESOLVED"

    # Energy & Power outputs (Phase 2, 3, 4)
    hover_power_w: float = 0.0
    transition_energy_wh: float = 0.0
    cruise_power_w: float = 0.0
    total_mission_energy_wh: float = 0.0
    battery_capacity_wh: float = 0.0

    # Mission Performance outputs
    cruise_speed_kmh: float = 0.0
    range_km: float = 0.0
    endurance_min: float = 0.0
    stall_speed_m_s: float = 0.0

    # Optimization outputs
    objectives: Dict[str, float] = field(default_factory=dict)
    constraint_results: List[Dict[str, Any]] = field(default_factory=list)
    violated_constraints: List[str] = field(default_factory=list)
    is_feasible: bool = False
    is_pareto_optimal: bool = False

    # Diagnostics & Provenance
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def objective_values(self) -> Dict[str, float]:
        """Alias for objectives dictionary."""
        return self.objectives

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "candidate_hash": self.candidate_hash,
            "status": self.status.value,
            "is_feasible": self.is_feasible,
            "is_pareto_optimal": self.is_pareto_optimal,
            "variables": {k: round(v, 4) for k, v in self.variables.items()},
            "objectives": {k: round(v, 4) for k, v in self.objectives.items()},
            "violated_constraints": self.violated_constraints,
            "sizing": {
                "mtow_kg": round(self.mtow_kg, 3),
                "empty_mass_kg": round(self.empty_mass_kg, 3),
                "payload_mass_kg": round(self.payload_mass_kg, 3),
                "battery_mass_kg": round(self.battery_mass_kg, 3),
                "cg_x_m": round(self.cg_x_m, 4),
                "cg_pct_mac": round(self.cg_pct_mac, 2),
            },
            "stability_and_control": {
                "neutral_point_x_m": round(self.neutral_point_x_m, 4),
                "static_margin_pct": round(self.static_margin_pct, 2),
                "is_statically_stable": self.is_statically_stable,
                "vtail_area_m2": round(self.vtail_area_m2, 4),
                "vtail_dihedral_deg": round(self.vtail_dihedral_deg, 2),
                "ruddervator_area_m2": round(self.ruddervator_area_m2, 4),
                "aileron_area_m2": round(self.aileron_area_m2, 4),
                "c_m_alpha_per_rad": round(self.c_m_alpha_per_rad, 4),
                "c_m_delta_e_per_rad": round(self.c_m_delta_e_per_rad, 4),
                "c_n_beta_per_rad": round(self.c_n_beta_per_rad, 4),
                "c_n_delta_r_per_rad": round(self.c_n_delta_r_per_rad, 4),
                "c_l_beta_per_rad": round(self.c_l_beta_per_rad, 4),
                "c_l_delta_a_per_rad": round(self.c_l_delta_a_per_rad, 4),
                "trim_status": self.trim_status,
                "cruise_trim_elevator_deg": round(self.cruise_trim_elevator_deg, 2),
                "control_authority_status": self.control_authority_status,
            },
            "energy_and_power": {
                "hover_power_w": round(self.hover_power_w, 1),
                "transition_energy_wh": round(self.transition_energy_wh, 2),
                "cruise_power_w": round(self.cruise_power_w, 1),
                "total_mission_energy_wh": round(self.total_mission_energy_wh, 2),
                "battery_capacity_wh": round(self.battery_capacity_wh, 2),
            },
            "performance": {
                "cruise_speed_kmh": round(self.cruise_speed_kmh, 1),
                "range_km": round(self.range_km, 2),
                "endurance_min": round(self.endurance_min, 1),
                "stall_speed_m_s": round(self.stall_speed_m_s, 2),
            },
            "constraint_results": self.constraint_results,
            "errors": self.errors,
            "warnings": self.warnings,
            "provenance": self.provenance,
        }


@dataclass(slots=True)
class OptimizationResult:
    """Consolidated Phase 7 multidisciplinary optimization and Pareto front result."""
    optimization_status: OptimizationStatus
    search_method: str
    design_variables: List[Dict[str, Any]]
    objectives: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    total_candidates: int
    evaluated_candidates: int
    cached_evaluations: int
    feasible_count: int
    infeasible_count: int
    dominated_count: int = 0
    error_count: int = 0
    pareto_count: int = 0
    problem_definition: Dict[str, Any] = field(default_factory=dict)
    pareto_front: List[DesignEvaluation] = field(default_factory=list)
    all_evaluations: List[DesignEvaluation] = field(default_factory=list)
    best_by_objective: Dict[str, Any] = field(default_factory=dict)
    evaluation_metadata: Dict[str, Any] = field(default_factory=dict)
    provenance_matrix: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    deferred_items: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "optimization_status": self.optimization_status.value,
            "search_method": self.search_method,
            "problem_definition": self.problem_definition,
            "counts": {
                "total_candidates": self.total_candidates,
                "evaluated_candidates": self.evaluated_candidates,
                "cached_evaluations": self.cached_evaluations,
                "feasible_count": self.feasible_count,
                "infeasible_count": self.infeasible_count,
                "dominated_count": self.dominated_count,
                "error_count": self.error_count,
                "pareto_count": self.pareto_count,
            },
            "design_variables": self.design_variables,
            "objectives": self.objectives,
            "constraints": self.constraints,
            "pareto_front": [p.to_dict() for p in self.pareto_front],
            "best_by_objective": {
                obj_name: cand.to_dict() if hasattr(cand, "to_dict") else cand
                for obj_name, cand in self.best_by_objective.items()
            },
            "evaluation_metadata": self.evaluation_metadata,
            "provenance_matrix": self.provenance_matrix,
            "warnings": self.warnings,
            "deferred_items": self.deferred_items,
        }
