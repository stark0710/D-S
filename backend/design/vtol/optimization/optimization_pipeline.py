"""
Torq Wings VTOL Phase 7 - Optimization Pipeline.

Coordinates multidisciplinary design space exploration, deterministic candidate
evaluation via authoritative Phase 1–6 evaluators, constraint checking,
objective extraction, and Pareto front extraction.
"""

import itertools
import logging
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from .optimization_models import (
    DesignCandidate,
    DesignEvaluation,
    EvaluationStatus,
    OptimizationProvenance,
    OptimizationResult,
    OptimizationStatus,
)
from .design_variables import (
    OptimizationVariable,
    STANDARD_VTOL_VARIABLES,
    validate_variable_bounds,
)
from .objective_model import (
    ObjectiveDefinition,
    STANDARD_OBJECTIVES,
)
from .constraint_model import (
    ConstraintDefinition,
    STANDARD_CONSTRAINTS,
)
from .design_evaluator import VTOLDesignEvaluator
from .pareto import (
    extract_pareto_front,
    extract_best_by_objective,
)

logger = logging.getLogger(__name__)


class VTOLOptimizationPipeline:
    """
    Multidisciplinary Optimization orchestrator for Torq Wings hybrid VTOL.

    Wraps authoritative Phases 1–6 models to perform deterministic design-space
    sweeps and true Pareto front synthesis.
    """

    def __init__(
        self,
        evaluator: Optional[VTOLDesignEvaluator] = None,
        variables: Optional[List[OptimizationVariable]] = None,
        objectives: Optional[List[ObjectiveDefinition]] = None,
        constraints: Optional[List[ConstraintDefinition]] = None,
    ):
        self.evaluator = evaluator or VTOLDesignEvaluator()
        self.variables = variables or [v for v in STANDARD_VTOL_VARIABLES.values() if v.is_active]
        self.objectives = objectives or [
            STANDARD_OBJECTIVES["mtow_kg"],
            STANDARD_OBJECTIVES["endurance_min"],
            STANDARD_OBJECTIVES["total_mission_energy_wh"],
        ]
        self.constraints = constraints or list(STANDARD_CONSTRAINTS.values())

    def generate_grid_candidates(
        self,
        active_variables: Optional[List[OptimizationVariable]] = None,
        resolution_per_var: int = 3,
        base_mission_overrides: Optional[Dict[str, Any]] = None,
    ) -> List[DesignCandidate]:
        """
        Generate deterministic Cartesian grid of design candidates.
        """
        vars_to_use = active_variables or [v for v in self.variables if v.is_active]
        base_mission = base_mission_overrides or {}

        if not vars_to_use:
            # Single baseline candidate
            return [DesignCandidate(
                candidate_id="CAND_000_BASE",
                variables={},
                mission_overrides=base_mission,
            )]

        var_values_list: List[List[Tuple[str, float]]] = []
        for var in vars_to_use:
            sampled_vals = var.sample_discrete(steps=resolution_per_var)
            var_values_list.append([(var.name, val) for val in sampled_vals])

        candidates: List[DesignCandidate] = []
        for idx, combination in enumerate(itertools.product(*var_values_list)):
            cand_vars = {k: v for k, v in combination}
            cand_id = f"CAND_{idx:04d}"
            candidates.append(DesignCandidate(
                candidate_id=cand_id,
                variables=cand_vars,
                mission_overrides=base_mission,
            ))

        return candidates

    def run_optimization(
        self,
        candidates: Optional[List[DesignCandidate]] = None,
        active_variables: Optional[List[OptimizationVariable]] = None,
        objectives: Optional[List[ObjectiveDefinition]] = None,
        constraints: Optional[List[ConstraintDefinition]] = None,
        search_method: str = "CARTESIAN_GRID",
        resolution_per_var: int = 3,
        base_mission_overrides: Optional[Dict[str, Any]] = None,
    ) -> OptimizationResult:
        """
        Execute deterministic optimization search and Pareto front extraction.
        """
        t0 = time.time()
        vars_used = active_variables or self.variables
        objs_used = objectives or self.objectives
        cons_used = constraints or self.constraints

        # Bound validation
        for var in vars_used:
            validate_variable_bounds(var)

        # Candidate generation if not provided directly
        if candidates is None:
            candidates = self.generate_grid_candidates(
                active_variables=vars_used,
                resolution_per_var=resolution_per_var,
                base_mission_overrides=base_mission_overrides,
            )

        total_candidates = len(candidates)
        evaluations: List[DesignEvaluation] = []
        cached_before = self.evaluator.cached_evaluations_count

        logger.info(
            "Starting VTOL Phase 7 optimization sweep: %d candidates, %d objectives, %d constraints",
            total_candidates, len(objs_used), len(cons_used)
        )

        for cand in candidates:
            ev = self.evaluator.evaluate_candidate(
                candidate=cand,
                objectives=objs_used,
                constraints=cons_used,
            )
            evaluations.append(ev)

        cached_after = self.evaluator.cached_evaluations_count
        cached_hits = total_candidates - (cached_after - cached_before)
        if cached_hits < 0:
            cached_hits = 0

        # Partition candidates into Pareto front, dominated, infeasible, and error sets
        partition = extract_pareto_front(evaluations, objs_used)

        feasible_count = len(partition.pareto_front) + len(partition.dominated_candidates)
        infeasible_count = len(partition.infeasible_candidates)
        error_count = len(partition.error_candidates)
        pareto_count = len(partition.pareto_front)
        dominated_count = len(partition.dominated_candidates)

        # Extract best candidate along each objective
        best_by_obj = extract_best_by_objective(partition.pareto_front, objs_used)

        # Determine overall optimization status
        if pareto_count > 0:
            status = OptimizationStatus.COMPLETED
        elif feasible_count == 0 and total_candidates > 0:
            status = OptimizationStatus.NO_FEASIBLE_DESIGNS
        else:
            status = OptimizationStatus.COMPLETED

        # Provenance matrix mapping
        provenance_matrix: Dict[str, str] = {}
        for v in vars_used:
            prov_val = v.provenance.value if hasattr(v.provenance, "value") else str(v.provenance)
            provenance_matrix[f"var.{v.name}"] = prov_val
        for obj in objs_used:
            prov_val = obj.provenance.value if hasattr(obj.provenance, "value") else str(obj.provenance)
            provenance_matrix[f"obj.{obj.name}"] = prov_val
        for con in cons_used:
            prov_val = con.provenance.value if hasattr(con.provenance, "value") else str(con.provenance)
            provenance_matrix[f"con.{con.name}"] = prov_val

        provenance_matrix["static_margin_boundaries_+5_+15_mac"] = OptimizationProvenance.CONFIGURABLE_ASSUMPTION.value
        provenance_matrix["aft_cg_boundary_44.23_mac"] = OptimizationProvenance.ASSUMPTION_BASED.value
        provenance_matrix["6dof_dynamic_stability"] = OptimizationProvenance.DEFERRED.value

        deferred_items = [
            "Dynamic 6-DOF simulation & frequency-domain stability verification (DEFERRED)",
            "Commercial hardware component selection (COTS motors, ESCs, cells) (DEFERRED to Phase 8)",
            "High-fidelity CFD and wind-tunnel aero calibration (DEFERRED)",
            "Aeroelastic flutter and structural FEA optimization (DEFERRED)",
            "Bill-of-materials pricing and supplier budget optimization (DEFERRED to Phase 8)",
        ]

        warnings: List[str] = []
        if infeasible_count > 0:
            warnings.append(
                f"{infeasible_count} of {total_candidates} candidates were INFEASIBLE and excluded from Pareto front."
            )
        if error_count > 0:
            warnings.append(
                f"{error_count} of {total_candidates} candidates encountered EVALUATION_ERROR during subsystem calculations."
            )
        if pareto_count == 0:
            warnings.append("No feasible Pareto-optimal design candidates were identified within search domain.")

        runtime_s = round(time.time() - t0, 3)

        result = OptimizationResult(
            optimization_status=status,
            search_method=search_method,
            problem_definition={
                "search_method": search_method,
                "resolution_per_var": resolution_per_var,
                "base_mission_overrides": base_mission_overrides or {},
                "active_variable_names": [v.name for v in vars_used if v.is_active],
                "objective_names": [o.name for o in objs_used],
                "constraint_names": [c.name for c in cons_used],
            },
            design_variables=[v.to_dict() for v in vars_used],
            objectives=[o.to_dict() for o in objs_used],
            constraints=[c.to_dict() for c in cons_used],
            total_candidates=total_candidates,
            evaluated_candidates=total_candidates - cached_hits,
            cached_evaluations=cached_hits,
            feasible_count=feasible_count,
            infeasible_count=infeasible_count,
            dominated_count=dominated_count,
            error_count=error_count,
            pareto_count=pareto_count,
            pareto_front=partition.pareto_front,
            all_evaluations=evaluations,
            best_by_objective=best_by_obj,
            evaluation_metadata={
                "runtime_seconds": runtime_s,
                "evaluations_per_sec": round(total_candidates / max(runtime_s, 0.001), 2),
                "is_deterministic": True,
            },
            provenance_matrix=provenance_matrix,
            warnings=warnings,
            deferred_items=deferred_items,
        )

        return result
