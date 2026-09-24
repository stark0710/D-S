from dataclasses import dataclass, asdict
from typing import Any, Dict
from backend.design.multirotor.mission.mission_targets import MissionTargets
from backend.design.multirotor.mission.strategy_models import PriorityWeights, DesignStrategy
from backend.design.multirotor.mission.mission_constraints import MissionConstraints

@dataclass(slots=True)
class MissionStrategySpecification:
    """
    Unified engineering design strategy specification output by the Mission Strategy Engine.
    """
    mission_summary: Dict[str, Any]
    engineering_targets: MissionTargets
    priority_weights: PriorityWeights
    constraint_summary: MissionConstraints
    recommended_configuration_class: str
    design_strategy: DesignStrategy
    optimization_priorities: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the strategy specification to a nested dictionary structure."""
        return {
            "mission_summary": self.mission_summary,
            "engineering_targets": asdict(self.engineering_targets),
            "priority_weights": asdict(self.priority_weights),
            "constraint_summary": asdict(self.constraint_summary),
            "recommended_configuration_class": self.recommended_configuration_class,
            "design_strategy": asdict(self.design_strategy),
            "optimization_priorities": self.optimization_priorities,
        }
