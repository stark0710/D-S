"""
VTOL Phase 9 System Integration & Verification Pipeline.

Purpose:
    Master pipeline orchestrator that ingests locked Phase 1-7 engineering results
    and Phase 8 commercial hardware selection (BOM), executes multi-domain physical,
    electrical, I/O, CG, mission-state, and failure verification, and returns the
    authoritative IntegrationPipelineResult.

Standards:
    - Downstream integration layer only: zero modification of upstream physics or Fixed-Wing backend.
    - 100% deterministic and fully serializable to JSON.
"""

from __future__ import annotations
import datetime
from typing import Any, Dict, List, Optional

from backend.design.vtol.commercial import (
    HardwareMatcher,
    CATALOG,
    CommercialBillOfMaterials,
)
from .integration_models import (
    IntegrationConfiguration,
    IntegrationPipelineResult,
    IntegrationStatus,
)
from .hardware_assignment import HardwareAssignmentEngine
from .electrical_integration import ElectricalIntegrationEngine
from .io_allocation import IOAllocationEngine
from .physical_integration import PhysicalInstallationEngine
from .cg_integration import CGIntegrationEngine
from .mission_integration import MissionIntegrationEngine
from .failure_analysis import FailureAnalysisEngine
from .integration_verifier import IntegrationVerifier


class VTOLSystemIntegrationPipeline:
    """
    Executes the complete Phase 9 System Integration and Multi-Domain Verification suite.
    """

    def __init__(self, config: Optional[IntegrationConfiguration] = None) -> None:
        self.config = config or IntegrationConfiguration()

    def execute(
        self,
        bom: Optional[CommercialBillOfMaterials] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> IntegrationPipelineResult:
        """
        Executes end-to-end integration and verification.
        If BOM is not provided, compiles it deterministically via Phase 8 HardwareMatcher.
        """
        overrides = overrides or {}

        # 1. Obtain Phase 8 Authoritative Commercial BOM
        if bom is None:
            matcher = HardwareMatcher(CATALOG)
            match_res = matcher.match_hardware(overrides=overrides)
            bom = match_res.selected_bom

        # 2. Hardware Assignment (Phase 8 BOM -> Aircraft Roles)
        assignments = HardwareAssignmentEngine.assign_hardware(bom)

        # 3. Electrical Architecture & Power Paths
        buses, power_paths, loads = ElectricalIntegrationEngine.build_electrical_architecture(
            assignments=assignments,
            bom=bom,
        )

        # 4. Deterministic Pixhawk I/O Port Allocation
        io_allocations = IOAllocationEngine.allocate_io()

        # 5. Physical Installation 3D Spatial Layout
        installed_components = PhysicalInstallationEngine.build_installation_model(
            bom=bom,
            airframe_mass_overrides=overrides.get("airframe_mass_overrides"),
        )

        # 6. Integrated Center of Gravity Evaluation
        integrated_cg = CGIntegrationEngine.calculate_integrated_cg(
            installed_components=installed_components,
            x_lemac_m=overrides.get("x_lemac_m"),
            mac_m=overrides.get("mac_m"),
            neutral_point_x_m=overrides.get("neutral_point_x_m"),
            forward_limit_m=overrides.get("forward_limit_m"),
            aft_limit_m=overrides.get("aft_limit_m"),
        )

        # 7. Mass Reconciliation (Phase 5 vs Phase 8 vs Phase 9)
        mass_reconciliation = CGIntegrationEngine.reconcile_mass(
            bom=bom,
            installed_components=installed_components,
            phase5_mtow_kg=overrides.get("phase5_mtow_kg"),
            phase5_hw_mass_kg=overrides.get("phase5_hw_mass_kg"),
        )

        # 8. Operational Mission-State Matrix (10 Phases)
        mission_states = MissionIntegrationEngine.evaluate_mission_states()

        # 9. Dual-Direction Transition Hardware Readiness
        transition_res = MissionIntegrationEngine.verify_transition_integration()

        # 10. System-Level Failure Modes & Controllability (13 Scenarios)
        failure_modes = FailureAnalysisEngine.evaluate_failure_modes()

        # 11. Connectors & Wiring Inventory
        connectors = IntegrationVerifier.compile_connector_inventory()

        # 12. Thermal Dissipation Checks
        thermal_checks = IntegrationVerifier.compile_thermal_checks()

        # 13. End-to-End Requirement Traceability
        traceability_table = IntegrationVerifier.compile_requirement_traceability()

        # 14. Consolidated Multi-Domain Integration Verification
        verification, final_status, deferred_items, insufficient_inputs = IntegrationVerifier.verify_all(
            assignments=assignments,
            buses=buses,
            paths=power_paths,
            io_allocations=io_allocations,
            installed_components=installed_components,
            integrated_cg=integrated_cg,
            mass_reconciliation=mass_reconciliation,
            mission_states=mission_states,
            transition=transition_res,
            failure_modes=failure_modes,
            config=self.config,
        )

        return IntegrationPipelineResult(
            final_status=final_status,
            assignments=assignments,
            electrical_buses=buses,
            power_paths=power_paths,
            io_allocations=io_allocations,
            installed_components=installed_components,
            integrated_cg=integrated_cg,
            mass_reconciliation=mass_reconciliation,
            mission_states=mission_states,
            transition_integration=transition_res,
            failure_modes=failure_modes,
            connectors=connectors,
            thermal_checks=thermal_checks,
            traceability_table=traceability_table,
            verification=verification,
            configuration=self.config,
            deferred_items=deferred_items,
            insufficient_input_items=insufficient_inputs,
            metadata={
                "generated_at": datetime.datetime.now().isoformat(),
                "phase": 9,
                "subsystem": "VTOL_SYSTEM_INTEGRATION_VERIFICATION",
                "aircraft_type": "LIFT_AND_CRUISE_QUADPLANE",
            },
        )
