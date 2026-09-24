"""
VTOL Phase 12 Engineering Model Reconciliation Engine.

Conducts evidence-based comparisons between empirical flight telemetry and
upstream engineering models (Phases 2-11) per Prompt Section 36.
"""

from __future__ import annotations
from typing import List, Optional

from .flight_test_models import (
    EngineeringReconciliation,
    ModelReconciliationAction,
    EvidenceStatus,
    DataOrigin,
    HoverMetrics,
    TransitionMetrics,
    CruiseMetrics,
    LandingMetrics,
)
from .hover_analysis import HoverAnalysisEngine
from .transition_analysis import TransitionAnalysisEngine
from .cruise_analysis import CruiseAnalysisEngine


class FlightDataReconciliationEngine:
    """
    Synthesizes multi-phase reconciliations without mutating upstream read-only calculations.
    Strictly distinguishes PHYSICAL_BENCH_MEASUREMENT / PHYSICAL_GROUND_MEASUREMENT from
    flight measurements and SYNTHETIC_TEST_DATA per Audit Section 6 & 12.
    """

    @classmethod
    def compile_all_reconciliations(
        cls,
        hover_metrics: Optional[List[HoverMetrics]] = None,
        transition_metrics: Optional[List[TransitionMetrics]] = None,
        cruise_metrics: Optional[List[CruiseMetrics]] = None,
        landing_metrics: Optional[List[LandingMetrics]] = None,
        allow_synthetic: bool = False,
    ) -> List[EngineeringReconciliation]:
        """
        Builds the master list of upstream model reconciliations.
        Accurately classifies data origin and evidence status.
        """
        reconciliations: List[EngineeringReconciliation] = []

        # 1. Phase 2: Hover Power Reconciliation
        if hover_metrics and allow_synthetic:
            valid_powers = [m.mean_electrical_power_w for m in hover_metrics if m.mean_electrical_power_w > 0]
            if valid_powers:
                avg_hover_pwr = sum(valid_powers) / len(valid_powers)
                rec = HoverAnalysisEngine.reconcile_hover_power(avg_hover_pwr)
                rec.evidence_origin = DataOrigin.SYNTHETIC_TEST_DATA
                rec.evidence_status = EvidenceStatus.SYNTHETIC_TEST_DATA
                rec.notes = "SYNTHETIC_TEST_DATA: Evaluated from software simulation fixture. NOT physical flight evidence."
                reconciliations.append(rec)
        else:
            reconciliations.append(EngineeringReconciliation(
                parameter_name="Hover Electrical Power",
                upstream_phase="Phase 2 Multirotor Performance",
                predicted_value="1782.40 W (Phase 2 Analytical Model)",
                measured_value="NOT_TESTED_IN_FLIGHT",
                delta="N/A",
                significance="AWAITING_PHYSICAL_FLIGHT",
                confidence="HIGH (Phase 2 Analytical Target)",
                action=ModelReconciliationAction.MONITOR,
                evidence_origin=DataOrigin.DESIGNED,
                evidence_status=EvidenceStatus.PLANNED_NOT_EXECUTED,
                notes="Zero physical flight sorties conducted. Awaiting Gate-2 hover stability flight test.",
            ))

        # 2. Phase 3: Transition Handover & Aerodynamics Reconciliation
        if transition_metrics and allow_synthetic:
            forward_tx = [t for t in transition_metrics if t.transition_type == "FORWARD_ACCEL"]
            if forward_tx:
                rec = TransitionAnalysisEngine.reconcile_transition_model(forward_tx[0])
                rec.evidence_origin = DataOrigin.SYNTHETIC_TEST_DATA
                rec.evidence_status = EvidenceStatus.SYNTHETIC_TEST_DATA
                rec.notes = "SYNTHETIC_TEST_DATA: Evaluated from software simulation fixture. NOT physical flight evidence."
                reconciliations.append(rec)
        else:
            reconciliations.append(EngineeringReconciliation(
                parameter_name="Transition Handover Airspeed",
                upstream_phase="Phase 3 Transition Aerodynamics",
                predicted_value="18.06 m/s (Phase 3 Handover Target)",
                measured_value="NOT_TESTED_IN_FLIGHT",
                delta="N/A",
                significance="AWAITING_PHYSICAL_FLIGHT",
                confidence="HIGH (Phase 3 Analytical Target)",
                action=ModelReconciliationAction.MONITOR,
                evidence_origin=DataOrigin.DESIGNED,
                evidence_status=EvidenceStatus.PLANNED_NOT_EXECUTED,
                notes="Zero physical flight sorties conducted. Awaiting Gate-5 forward transition flight test.",
            ))

        # 3. Phase 4: Cruise Electrical Power Reconciliation
        if cruise_metrics and allow_synthetic:
            valid_cruise = [c for c in cruise_metrics if c.mean_cruise_power_w > 0]
            if valid_cruise:
                rec = CruiseAnalysisEngine.reconcile_cruise_power(valid_cruise[0])
                rec.evidence_origin = DataOrigin.SYNTHETIC_TEST_DATA
                rec.evidence_status = EvidenceStatus.SYNTHETIC_TEST_DATA
                rec.notes = "SYNTHETIC_TEST_DATA: Evaluated from software simulation fixture. NOT physical flight evidence."
                reconciliations.append(rec)
        else:
            reconciliations.append(EngineeringReconciliation(
                parameter_name="Cruise Aerodynamic Electrical Power",
                upstream_phase="Phase 4 Fixed-Wing Flight Performance",
                predicted_value="248.50 W (Phase 4 Power Curve at 22 m/s)",
                measured_value="NOT_TESTED_IN_FLIGHT",
                delta="N/A",
                significance="AWAITING_PHYSICAL_FLIGHT",
                confidence="HIGH (Phase 4 Analytical Target)",
                action=ModelReconciliationAction.MONITOR,
                evidence_origin=DataOrigin.DESIGNED,
                evidence_status=EvidenceStatus.PLANNED_NOT_EXECUTED,
                notes="Zero physical flight sorties conducted. Awaiting Gate-6 fixed-wing cruise flight test.",
            ))

        # 4. Phase 5: Installed Mass / MTOW Reconciliation (Phase 11 Ground Measurement)
        reconciliations.append(EngineeringReconciliation(
            parameter_name="Installed Takeoff Mass (MTOW)",
            upstream_phase="Phase 5 Mass Properties Model",
            predicted_value="7.869 kg (Converged Phase 5 MTOW)",
            measured_value="7.915 kg (Phase 11 Calibrated Ground Scale)",
            delta="+0.046 kg (+0.58%)",
            significance="WITHIN_DESIGN_TOLERANCE",
            confidence="VERY_HIGH (Calibrated 3-Point Load Cells)",
            action=ModelReconciliationAction.NO_CHANGE,
            evidence_origin=DataOrigin.PHYSICAL_GROUND_MEASUREMENT,
            evidence_status=EvidenceStatus.PHYSICALLY_EXECUTED_AND_LOGGED,
            notes="PHYSICAL_GROUND_MEASUREMENT: Weighed on calibrated ground scale during Phase 11; NOT flight-measured.",
        ))

        # 5. Phase 6: Longitudinal CG Position (Phase 11 Ground Measurement)
        reconciliations.append(EngineeringReconciliation(
            parameter_name="Longitudinal Center of Gravity (CG)",
            upstream_phase="Phase 6 Stability & Control Sizing",
            predicted_value="0.5165 m (Nominal Phase 6 CG)",
            measured_value="0.5180 m (Phase 11 Ground Balance Rig)",
            delta="+0.0015 m (+1.5 mm shift)",
            significance="NOMINAL_CORRELATION",
            confidence="VERY_HIGH (Mechanical Knife-Edge Balance Rig)",
            action=ModelReconciliationAction.NO_CHANGE,
            evidence_origin=DataOrigin.PHYSICAL_GROUND_MEASUREMENT,
            evidence_status=EvidenceStatus.PHYSICALLY_EXECUTED_AND_LOGGED,
            notes="PHYSICAL_GROUND_MEASUREMENT: Measured on physical ground balance rig in Phase 11; NOT flight-measured.",
        ))

        # 6. Phase 8: Lift Motor Static Thrust (Phase 11 Bench Measurement)
        reconciliations.append(EngineeringReconciliation(
            parameter_name="Lift Motor Static Thrust",
            upstream_phase="Phase 8 Commercial Hardware Specification",
            predicted_value="23.50 N (Phase 8 Specification per motor)",
            measured_value="23.20 N (Phase 11 Static Thrust Stand)",
            delta="-0.30 N (-1.28%)",
            significance="WITHIN_BENCH_TOLERANCE",
            confidence="VERY_HIGH (Bench Load Cell with Calibrated Tare)",
            action=ModelReconciliationAction.NO_CHANGE,
            evidence_origin=DataOrigin.PHYSICAL_BENCH_MEASUREMENT,
            evidence_status=EvidenceStatus.PHYSICALLY_EXECUTED_AND_LOGGED,
            notes="PHYSICAL_BENCH_MEASUREMENT: Measured on physical thrust stand in Phase 11 commissioning; NOT flight-measured.",
        ))

        # 7. Phase 10: ArduPilot Q_TRANS_FAIL Timing Configuration
        reconciliations.append(EngineeringReconciliation(
            parameter_name="ArduPilot Q_TRANS_FAIL Failsafe Timing",
            upstream_phase="Phase 10 Flight Control Configuration",
            predicted_value="Q_TRANS_FAIL = 30 s; Q_TRANSITION_MS = 5000 ms",
            measured_value="NOT_TESTED_IN_FLIGHT (Phase 11 bench logic verified)",
            delta="N/A",
            significance="BENCH_VERIFIED_ONLY",
            confidence="HIGH (Phase 11 Ground Verification Script)",
            action=ModelReconciliationAction.MONITOR,
            evidence_origin=DataOrigin.PHYSICAL_BENCH_MEASUREMENT,
            evidence_status=EvidenceStatus.PHYSICALLY_EXECUTED_AND_LOGGED,
            notes="Bench failsafe logic verified during Phase 11 commissioning. In-flight abort timing not tested in flight.",
        ))

        return reconciliations
