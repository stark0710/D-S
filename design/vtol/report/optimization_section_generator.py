from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class OptimizationSection:
    """
    Pareto tradeoffs and gradient limits.
    """
    title: str
    pareto_tradeoffs_list: List[str]
    sensitivities_summary: Dict[str, str]
    fitness_improvements: str
