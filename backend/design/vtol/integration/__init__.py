"""
Torq Wings Studio v2 - VTOL Phase 9 System Integration and Verification Subsystem.

Purpose:
    Exports authoritative integration domain models, hardware assignment, electrical
    architecture, I/O pinout allocation, 3D installation models, integrated CG,
    mission-state operational matrices, preliminary failure modes (FMEA),
    and master pipeline orchestrator.
"""

from .integration_models import (
    IntegrationStatus,
    ProvenanceCategory,
    VerificationCheckStatus,
    AircraftRole,
    BusType,
    IOPortType,
    SignalProtocol,
    MountingRegion,
    MissionState,
    ControllabilityStatus,
    HardwareAssignment,
    ElectricalLoad,
    ElectricalBus,
    PowerPath,
    IOAssignment,
    ComponentLocation,
    IntegratedCGResult,
    MassReconciliationResult,
    StateDeviceStatus,
    MissionStateIntegrationResult,
    TransitionIntegrationResult,
    FailureModeResult,
    ConnectorInterfaceItem,
    ThermalCheckItem,
    IntegrationRequirementTrace,
    IntegrationVerificationResult,
    IntegrationConfiguration,
    IntegrationPipelineResult,
)
from .hardware_assignment import HardwareAssignmentEngine
from .electrical_integration import ElectricalIntegrationEngine
from .io_allocation import IOAllocationEngine
from .physical_integration import PhysicalInstallationEngine
from .cg_integration import CGIntegrationEngine
from .mission_integration import MissionIntegrationEngine
from .failure_analysis import FailureAnalysisEngine
from .integration_verifier import IntegrationVerifier
from .integration_pipeline import VTOLSystemIntegrationPipeline

__all__ = [
    "IntegrationStatus",
    "ProvenanceCategory",
    "VerificationCheckStatus",
    "AircraftRole",
    "BusType",
    "IOPortType",
    "SignalProtocol",
    "MountingRegion",
    "MissionState",
    "ControllabilityStatus",
    "HardwareAssignment",
    "ElectricalLoad",
    "ElectricalBus",
    "PowerPath",
    "IOAssignment",
    "ComponentLocation",
    "IntegratedCGResult",
    "MassReconciliationResult",
    "StateDeviceStatus",
    "MissionStateIntegrationResult",
    "TransitionIntegrationResult",
    "FailureModeResult",
    "ConnectorInterfaceItem",
    "ThermalCheckItem",
    "IntegrationRequirementTrace",
    "IntegrationVerificationResult",
    "IntegrationConfiguration",
    "IntegrationPipelineResult",
    "HardwareAssignmentEngine",
    "ElectricalIntegrationEngine",
    "IOAllocationEngine",
    "PhysicalInstallationEngine",
    "CGIntegrationEngine",
    "MissionIntegrationEngine",
    "FailureAnalysisEngine",
    "IntegrationVerifier",
    "VTOLSystemIntegrationPipeline",
]
