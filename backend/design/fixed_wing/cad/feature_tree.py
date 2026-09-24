"""
Fixed-Wing CAD Feature Tree Subsystem

Purpose:
    Defines the `FeatureTree` class representing parametric feature history logs.

Role in Architecture:
    `FeatureTree` records chronological lists of modeling operations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass(slots=True)
class FeatureTree:
    """
    Parametric history tree tracking modeling features.

    Attributes:
        features (List[Dict[str, Any]]): Chronological modeling steps (extrusions, lofts, fillets).
    """

    features: List[Dict[str, Any]] = field(default_factory=list)

    def add_feature(self, feature_type: str, target: str, parameters: Dict[str, Any]) -> None:
        """Appends a modeling operation to the history tree."""
        self.features.append({
            "step_id": len(self.features) + 1,
            "feature_type": feature_type,
            "target_component": target,
            "parameters": parameters,
        })
