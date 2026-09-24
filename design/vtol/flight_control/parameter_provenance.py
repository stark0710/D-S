"""
VTOL Phase 10 Parameter Provenance Tracking Engine.

Purpose:
    Maintains a strict, traceable parameter provenance registry.
    Ensures that every ArduPilot QuadPlane parameter is linked to an upstream
    authoritative source, official ArduPilot documentation, manufacturer datasheet,
    or explicit configurable assumption.
    Flags any parameter lacking evidence or requiring flight validation.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from .flight_control_models import (
    ArduPilotParameter,
    FlightControlStatus,
    ParameterConfidence,
    ParameterSourceType,
)


class ParameterProvenanceRegistry:
    """
    Authoritative registry and auditor for ArduPilot QuadPlane parameter provenance.
    """

    def __init__(self) -> None:
        self._parameters: Dict[str, ArduPilotParameter] = {}

    def register(self, param: ArduPilotParameter) -> None:
        """Registers an ArduPilot parameter with its provenance."""
        if param.parameter_name in self._parameters:
            raise ValueError(f"Duplicate parameter registration: {param.parameter_name}")
        self._parameters[param.parameter_name] = param

    def get(self, name: str) -> Optional[ArduPilotParameter]:
        """Retrieves a registered parameter by name."""
        return self._parameters.get(name)

    def all_parameters(self) -> List[ArduPilotParameter]:
        """Returns all registered parameters in alphabetical order."""
        return sorted(self._parameters.values(), key=lambda p: p.parameter_name)

    def filter_by_source(self, source_type: ParameterSourceType) -> List[ArduPilotParameter]:
        """Filters parameters by source type."""
        return [p for p in self._parameters.values() if p.source_type == source_type]

    def audit_provenance_completeness(self) -> Dict[str, Any]:
        """
        Audits parameter set to verify that no parameter has UNKNOWN provenance,
        and aggregates confidence levels.
        """
        total = len(self._parameters)
        unknown_params = [p.parameter_name for p in self._parameters.values() if p.source_type == ParameterSourceType.UNKNOWN]
        deferred_params = [p.parameter_name for p in self._parameters.values() if p.status == FlightControlStatus.DEFERRED]
        assumed_params = [p.parameter_name for p in self._parameters.values() if p.source_type == ParameterSourceType.CONFIGURABLE_ASSUMPTION]

        return {
            "total_parameters": total,
            "has_unknown": len(unknown_params) > 0,
            "unknown_parameters": unknown_params,
            "deferred_parameters_count": len(deferred_params),
            "deferred_parameters": deferred_params,
            "assumed_parameters_count": len(assumed_params),
            "assumed_parameters": assumed_params,
            "high_confidence_count": sum(1 for p in self._parameters.values() if p.confidence == ParameterConfidence.HIGH),
            "medium_confidence_count": sum(1 for p in self._parameters.values() if p.confidence == ParameterConfidence.MEDIUM),
            "low_confidence_count": sum(1 for p in self._parameters.values() if p.confidence == ParameterConfidence.LOW),
        }
