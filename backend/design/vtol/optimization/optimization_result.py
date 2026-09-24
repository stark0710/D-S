from dataclasses import dataclass, field
from typing import Any, Dict, List

from .design_variables import DesignVariables
from .pareto_analysis import ParetoFront
from .tradeoff_analysis import TradeoffAnalysis
from .sensitivity_analysis import SensitivityAnalysis
from .optimization_history import OptimizationHistory
from .objective_functions import ObjectiveValues
from .constraint_functions import ConstraintSummary
from .optimization_analysis import OptimizationAnalysis

@dataclass(slots=True)
class OptimizationResult:
    """
    Consolidated outputs of the VTOL Design Optimization Framework.
    """
    optimized_design: DesignVariables
    pareto_front: ParetoFront
    tradeoff_analysis: TradeoffAnalysis
    sensitivity_analysis: SensitivityAnalysis
    optimization_history: OptimizationHistory
    objective_values: ObjectiveValues
    constraint_summary: ConstraintSummary
    optimization_analysis: OptimizationAnalysis

    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
