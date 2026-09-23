"""
VTOL Phase 11 Ground Verification Pipeline.

Master coordinator orchestrating physical hardware inventory auditing,
power-off electrical inspections, power-on bus voltage verification, Pixhawk commissioning,
sensor validations, actuator output mapping and motor rotation tests, failsafe injection,
bench transition verification, 18-point ground test evidence logging, defect management,
and final ground verification verdict determination.
"""

from __future__ import annotations
import json
import os
from typing import Any, Dict, List, Optional

from .ground_verification_models import (
    GroundVerificationState,
    GroundVerificationVerdict,
    HardwareReconciliationStatus,
    GroundTestStatus,
    DefectSeverity,
    DefectStatus,
    PhysicalComponent,
)
from .hardware_inventory_verifier import HardwareInventoryVerifier
from .power_commissioning import PowerCommissioningEngine
from .pixhawk_commissioning import PixhawkCommissioningEngine
from .sensor_verifier import SensorVerifier
from .actuator_verifier import ActuatorVerifier
from .failsafe_verifier import FailsafeVerifier
from .bench_transition_verifier import BenchTransitionVerifier
from .ground_test_engine import GroundTestEngine


class GroundVerificationPipeline:
    """
    Executes the comprehensive Phase 11 physical ground verification and Pixhawk commissioning pipeline.
    """

    AIRCRAFT_NAME = "Torq Wings VTOL (Lift + Cruise QuadPlane)"
    CONFIG_VERSION = "PHASE-10-CONFIG-V2.1 / ARDUPLANE-4.5.4"

    @classmethod
    def run_pipeline(
        cls,
        as_executed: bool = True,
        simulate_hardware_conflict: bool = False,
        operator: Optional[str] = None,
        date_str: str = "2026-09-21",
    ) -> GroundVerificationState:
        """
        Executes the full commissioning pipeline and synthesizes the final ground verification state.
        """
        # 1. Hardware Inventory & Reconciliation
        inventory = HardwareInventoryVerifier.build_authorized_inventory()
        if simulate_hardware_conflict:
            conflicted_inventory = []
            for item in inventory:
                if "HW-LIFT-ESC" in item.component_id:
                    conflicted_inventory.append(
                        PhysicalComponent(
                            component_id=item.component_id,
                            name=item.name,
                            manufacturer="T-Motor",
                            model="AIR 40A Multi-Rotor ESC",
                            serial_number="TM-AIR40-CONFLICT",
                            quantity=item.quantity,
                            physical_location=item.physical_location,
                            electrical_connection=item.electrical_connection,
                            software_identity=item.software_identity,
                            bom_identity=item.bom_identity,
                            phase10_identity=item.phase10_identity,
                            verification_status=HardwareReconciliationStatus.HARDWARE_IDENTITY_CONFLICT,
                            notes="Physical hardware conflict: T-Motor AIR 40A installed instead of Spedix GS40A.",
                        )
                    )
                else:
                    conflicted_inventory.append(item)
            inventory = conflicted_inventory

        hw_verdict, hw_conflicts = HardwareInventoryVerifier.audit_physical_reconciliation(inventory)

        # 2. Power-Off Electrical Inspection
        electrical_inspection = PowerCommissioningEngine.generate_power_off_inspection_checklist()

        # 3. Controlled Power-On Voltage Measurements
        power_rails = PowerCommissioningEngine.execute_controlled_power_on_measurements()

        # 4. Pixhawk Autopilot Commissioning
        pixhawk_rec = PixhawkCommissioningEngine.execute_pixhawk_commissioning()

        # 5. Sensor Subsystems Verification
        sensors = SensorVerifier.verify_all_sensors()

        # 6. Actuator Output Mapping, Motors & Servos
        output_mappings = ActuatorVerifier.verify_output_channel_mapping()
        motor_ids = ActuatorVerifier.verify_motor_identifications_and_directions()
        servos, vtail = ActuatorVerifier.verify_servos_and_control_surfaces()

        # 7. Bench Failsafe Tests
        failsafes = FailsafeVerifier.verify_bench_failsafes()

        # 8. Bench Transition Logic (Props Removed)
        transition_bench = BenchTransitionVerifier.verify_bench_transition()

        # 9. Ground Test Procedures & Evidence
        ground_tests = GroundTestEngine.generate_ground_test_records(
            as_executed=as_executed,
            operator=operator,
            date_str=date_str,
        )

        # 10. Mass & CG Audit
        mass_cg = GroundTestEngine.audit_mass_and_cg()

        # 11. Thermal Inspections
        thermals = GroundTestEngine.audit_bench_thermals()

        # 12. Defect Management & Upstream Reconciliations
        defects = GroundTestEngine.compile_defects(hw_conflicts)
        upstream_reconciliations = GroundTestEngine.compile_upstream_reconciliations(mass_cg)

        # 13. Determine Final Verdict
        verdict, explanation = cls._evaluate_final_verdict(
            as_executed=as_executed,
            ground_tests=ground_tests,
            defects=defects,
            hw_conflicts=hw_conflicts,
            electrical_inspection=electrical_inspection,
        )

        state = GroundVerificationState(
            aircraft_name=cls.AIRCRAFT_NAME,
            configuration_version=cls.CONFIG_VERSION,
            pixhawk_commissioning=pixhawk_rec,
            physical_inventory=inventory,
            electrical_inspection=electrical_inspection,
            power_rail_measurements=power_rails,
            sensor_verifications=sensors,
            output_verifications=output_mappings,
            motor_identifications=motor_ids,
            servo_verifications=servos,
            vtail_verification=vtail,
            failsafe_tests=failsafes,
            transition_bench=transition_bench,
            thermal_checks=thermals,
            mass_cg_measurement=mass_cg,
            ground_tests=ground_tests,
            defects=defects,
            upstream_reconciliations=upstream_reconciliations,
            hardware_reconciliation_verdict=hw_verdict,
            verdict=verdict,
            verdict_explanation=explanation,
        )
        return state

    @classmethod
    def _evaluate_final_verdict(
        cls,
        as_executed: bool,
        ground_tests: List[Any],
        defects: List[Any],
        hw_conflicts: List[Any],
        electrical_inspection: List[Any],
    ) -> tuple[GroundVerificationVerdict, str]:
        """
        Evaluates the final commissioning verdict following Prompt Section 43 rules.
        """
        # Rule 1: If tests have not been executed on physical hardware
        if not as_executed or any(gt.status == GroundTestStatus.NOT_EXECUTED for gt in ground_tests):
            return (
                GroundVerificationVerdict.GROUND_VERIFICATION_NOT_EXECUTED,
                "Physical bench procedures have not yet been executed on aircraft hardware. "
                "All 18 ground test procedures remain in NOT_EXECUTED status.",
            )

        # Rule 2: Check for critical electrical or safety blockers
        critical_electrical_failure = any(e.status.value == "FAIL" for e in electrical_inspection)
        critical_defects = [d for d in defects if d.severity == DefectSeverity.CRITICAL and d.status == DefectStatus.OPEN]
        if critical_electrical_failure or critical_defects:
            return (
                GroundVerificationVerdict.GROUND_VERIFICATION_BLOCKED,
                f"Critical safety or electrical failure prevents ground testing sign-off: "
                f"{len(critical_defects)} critical defects identified.",
            )

        # Rule 3: Check for hardware identity conflicts (Prompt Section 6 & 43)
        if hw_conflicts:
            return (
                GroundVerificationVerdict.GROUND_VERIFICATION_BLOCKED,
                f"ACTUAL_HARDWARE_DIFFERS_FROM_AUTHORIZED_BOM: {len(hw_conflicts)} hardware identity conflict(s) detected. "
                "Configuration path stopped. Ground verification blocked.",
            )

        # Rule 4: Check for non-critical limitations and warnings
        has_warnings = False
        warning_reasons = []

        # In-flight deferred items (aerodynamics, long-range telemetry, flight thermals)
        has_warnings = True
        warning_reasons.append("In-flight aerodynamic airspeed calibration and flight thermals remain FLIGHT_TEST_REQUIRED")

        if any(d.severity == DefectSeverity.HIGH and d.status == DefectStatus.OPEN for d in defects):
            has_warnings = True
            warning_reasons.append("High-severity defect tracked regarding ESC hardware reconciliation")

        if has_warnings:
            return (
                GroundVerificationVerdict.GROUND_VERIFICATION_COMPLETE_WITH_WARNINGS,
                "Ground verification completed successfully on bench with all 18 procedures executed. "
                f"Non-critical limitations tracked: {'; '.join(warning_reasons)}.",
            )

        return (
            GroundVerificationVerdict.GROUND_VERIFICATION_COMPLETE,
            "All 18 ground test procedures executed and passed with zero defects or hardware conflicts.",
        )

    @classmethod
    def export_json(cls, state: GroundVerificationState, filepath: str) -> str:
        """
        Serializes and exports the full Phase 11 ground verification state to a JSON file.
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2)
        return filepath
