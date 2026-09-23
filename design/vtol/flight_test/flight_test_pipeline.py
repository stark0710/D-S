"""
VTOL Phase 12 Flight Test Pipeline Engine.

Master orchestration pipeline coordinating flight readiness evaluation, sortie execution,
envelope expansion tracking, analytical regime metrics, multi-phase reconciliations,
incident management, and generation of the 40-section master engineering report.
"""

from __future__ import annotations
import json
import os
from typing import Any, Dict, List, Optional

from .flight_test_models import (
    FlightCampaignState,
    FlightCampaignVerdict,
    FlightGate,
    FlightSortieRecord,
    FlightIncident,
    WeatherConditions,
    OperatingLimits,
    FlightEnvelope,
)
from .flight_conditions import FlightConditionsEngine
from .flight_readiness import FlightReadinessEngine
from .test_campaign import FlightTestCampaignEngine
from .envelope_manager import FlightEnvelopeManager
from .flight_data_reconciliation import FlightDataReconciliationEngine
from .flight_test_verifier import FlightTestVerifier


class FlightTestPipeline:
    """
    Executes the end-to-end Phase 12 Controlled Flight Testing & Flight-Envelope Expansion pipeline.
    """

    AIRCRAFT_NAME = "Torq Wings VTOL (Lift + Cruise QuadPlane)"
    CAMPAIGN_NAME = "Torq Wings Phase 12 Controlled Flight Test Campaign"

    @classmethod
    def run_pipeline(
        cls,
        as_executed: bool = True,
        simulate_synthetic: bool = False,
        simulate_critical_stop: bool = False,
        simulate_weather_block: bool = False,
    ) -> FlightCampaignState:
        """
        Executes flight test campaign synthesis.
        Per Audit Section 7: In the absence of real physical flight logs,
        sorties are PLANNED_NOT_EXECUTED, envelope is NOT_ESTABLISHED,
        and final verdict is FLIGHT_TEST_FRAMEWORK_COMPLETE_NOT_EXECUTED.
        """
        limits = FlightConditionsEngine.get_default_operating_limits()

        # 1. Weather conditions
        if simulate_weather_block:
            weather = WeatherConditions(
                temperature_c=24.0,
                wind_speed_mps=11.5,  # Exceeds 7.0 m/s limit
                wind_direction_deg=220.0,
                wind_gust_mps=14.0,   # Exceeds 9.0 m/s limit
                humidity_pct=60.0,
                visibility_km=3.0,    # Below 5.0 km limit
                field_condition="Wet runway with high gusting crosswinds",
                within_limits=False,
            )
        else:
            weather = WeatherConditions(
                temperature_c=22.5,
                wind_speed_mps=3.1,
                wind_direction_deg=220.0,
                wind_gust_mps=4.2,
                humidity_pct=50.0,
                visibility_km=10.0,
                field_condition="Dry flat short-grass turf, zero ground obstacles",
                within_limits=True,
            )

        # 2. Pre-Flight Readiness Gate
        readiness = FlightReadinessEngine.evaluate_readiness(
            weather=weather,
            limits=limits,
            target_gate=FlightGate.GATE_1_INITIAL_VTOL,
            ground_verification_passed=True,
            pilot_briefing_completed=True,
            emergency_procedure_reviewed=True,
            hardware_conflicts_present=False,
            structural_damage_detected=simulate_critical_stop,
        )

        # 3. Flight Sorties & Incidents
        if simulate_synthetic and not simulate_weather_block:
            sorties = FlightTestCampaignEngine.build_synthetic_test_sorties()
            incidents = FlightTestCampaignEngine.build_standard_campaign_incidents(as_synthetic=True)
            completed_gates = [
                FlightGate.GATE_0_GROUND_VERIFIED,
                FlightGate.GATE_1_INITIAL_VTOL,
                FlightGate.GATE_2_STABLE_HOVER,
                FlightGate.GATE_3_VERTICAL_MANEUVERING,
                FlightGate.GATE_4_FORWARD_FLIGHT,
                FlightGate.GATE_5_FIRST_TRANSITION,
                FlightGate.GATE_6_STABLE_CRUISE,
                FlightGate.GATE_7_RETURN_TRANSITION,
                FlightGate.GATE_8_VTOL_RECOVERY,
                FlightGate.GATE_9_LANDING,
            ]
            active_gate = FlightGate.GATE_10_EXPANDED_ENVELOPE
        elif as_executed and not simulate_weather_block:
            # Audit Section 7: No physical flight logs exist in repository
            sorties = FlightTestCampaignEngine.build_planned_campaign_sorties()
            incidents = []
            completed_gates = [FlightGate.GATE_0_GROUND_VERIFIED]
            active_gate = FlightGate.GATE_1_INITIAL_VTOL
        else:
            sorties = []
            incidents = []
            completed_gates = [FlightGate.GATE_0_GROUND_VERIFIED]
            active_gate = FlightGate.GATE_1_INITIAL_VTOL

        # 4. Flight Envelope Compilation (Strict physical evidence filter)
        envelope = FlightEnvelopeManager.compile_demonstrated_envelope(
            sorties, allow_synthetic=simulate_synthetic
        )

        # 5. Multi-Phase Engineering Reconciliations
        hover_metrics = [s.hover_metrics for s in sorties if s.hover_metrics]
        transition_metrics = [s.transition_metrics for s in sorties if s.transition_metrics]
        cruise_metrics = [s.cruise_metrics for s in sorties if s.cruise_metrics]
        landing_metrics = [s.landing_metrics for s in sorties if s.landing_metrics]

        reconciliations = FlightDataReconciliationEngine.compile_all_reconciliations(
            hover_metrics=hover_metrics,
            transition_metrics=transition_metrics,
            cruise_metrics=cruise_metrics,
            landing_metrics=landing_metrics,
            allow_synthetic=simulate_synthetic,
        )

        # 6. Campaign Verdict Determination
        verdict, explanation = FlightTestVerifier.evaluate_campaign_verdict(
            sorties=sorties,
            incidents=incidents,
            completed_gates=completed_gates,
            allow_synthetic=simulate_synthetic,
        )

        state = FlightCampaignState(
            aircraft_name=cls.AIRCRAFT_NAME,
            campaign_name=cls.CAMPAIGN_NAME,
            active_gate=active_gate,
            completed_gates=completed_gates,
            sorties=sorties,
            demonstrated_envelope=envelope,
            incidents=incidents,
            reconciliations=reconciliations,
            current_readiness=readiness,
            site_limits=limits,
            campaign_verdict=verdict,
            verdict_explanation=explanation,
        )
        return state

    @classmethod
    def export_json(cls, state: FlightCampaignState, filepath: str) -> str:
        """
        Serializes and exports the full Phase 12 flight test campaign state to a JSON file.
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2)
        return filepath
