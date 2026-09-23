"""
Data models for Fixed-Wing Pareto Front Extraction.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class ObjectiveDirection(str, Enum):
    """Optimization objective direction."""
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


@dataclass(slots=True)
class ParetoObjectiveDefinition:
    """Metadata defining a Pareto objective dimension."""
    name: str
    direction: ObjectiveDirection
    unit: str
    description: str


@dataclass(slots=True)
class ParetoObjectiveValue:
    """Evaluated metric value for a specific candidate objective."""
    name: str
    direction: ObjectiveDirection
    value: float
    unit: str


@dataclass(slots=True)
class ParetoTolerance:
    """Physical engineering tolerances for dominance and deduplication."""
    mtow_kg: float = 0.010       # 10 grams
    endurance_min: float = 0.1   # 6 seconds
    range_km: float = 0.1        # 100 meters
    payload_kg: float = 0.005    # 5 grams
    efficiency: float = 0.05     # 0.05 in L/D units

    def get_tolerance(self, objective_name: str) -> float:
        norm = objective_name.lower()
        if "mtow" in norm:
            return self.mtow_kg
        elif "endurance" in norm:
            return self.endurance_min
        elif "range" in norm:
            return self.range_km
        elif "payload" in norm:
            return self.payload_kg
        elif "efficiency" in norm:
            return self.efficiency
        return 1e-4


@dataclass(slots=True)
class ParetoCandidate:
    """
    A single aircraft design candidate evaluated within the Pareto objective space.
    """
    candidate_id: str
    is_feasible: bool
    pareto_rank: int = 1
    is_selected_design: bool = False
    objectives: Dict[str, ParetoObjectiveValue] = field(default_factory=dict)
    engineering_summary: Dict[str, Any] = field(default_factory=dict)
    technical_specifications: Dict[str, Any] = field(default_factory=dict)
    provenance: str = "Aircraft Sizing Engine"
    specification: Optional[Any] = None

    def get_value(self, name: str) -> float:
        if name in self.objectives:
            return self.objectives[name].value
        raise KeyError(f"Objective '{name}' not found on candidate '{self.candidate_id}'")


@dataclass(slots=True)
class ParetoFrontResult:
    """
    Consolidated output payload of Pareto-front extraction.
    """
    enabled: bool
    objective_definitions: List[ParetoObjectiveDefinition] = field(default_factory=list)
    candidate_count: int = 0
    feasible_candidate_count: int = 0
    dominated_candidate_count: int = 0
    deduplicated_count: int = 0
    front_size: int = 0
    front: List[ParetoCandidate] = field(default_factory=list)
    methodology: str = "Bounded Feasible Candidate Nondominated Sorting"
    warnings: List[str] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
