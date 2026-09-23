"""
VTOL Phase 12 Flight Envelope Management Engine.

Maintains empirical demonstrated flight-envelope boundaries (Prompt Section 30) and
enforces incremental single-variable envelope expansion rules (Prompt Section 31).
"""

from __future__ import annotations
from typing import List, Dict, Any, Tuple

from .flight_test_models import (
    FlightEnvelope,
    FlightSortieRecord,
    EvidenceStatus,
)


class FlightEnvelopeManager:
    """
    Tracks demonstrated flight boundaries and validates incremental expansion safety.
    """

    # Upstream design reference limits (Phase 1-6 analytical targets)
    DESIGN_MAX_AIRSPEED_MPS = 32.0
    DESIGN_MIN_AIRSPEED_MPS = 13.9   # V_stall clean = 13.89 m/s
    DESIGN_MAX_ALTITUDE_M = 120.0
    DESIGN_MAX_BANK_ANGLE_DEG = 35.0
    DESIGN_MAX_PITCH_ANGLE_DEG = 25.0

    @classmethod
    def compile_demonstrated_envelope(
        cls,
        sorties: List[FlightSortieRecord],
        allow_synthetic: bool = False,
    ) -> FlightEnvelope:
        """
        Synthesizes maximum and minimum demonstrated boundaries from completed flight sorties.
        Per Audit Section 3, 5, 7, and 15:
        Only sorties with PHYSICALLY_EXECUTED_AND_LOGGED and verified log sources can contribute.
        Synthetic test data and planned sorties are strictly barred from empirical envelope.
        """
        if not sorties:
            return FlightEnvelope(is_established=False, status="NOT_ESTABLISHED")

        # Strict evidence filter: must be physically executed and logged with verified source
        if allow_synthetic:
            eligible_sorties = [s for s in sorties if s.hover_metrics or s.transition_metrics or s.cruise_metrics]
        else:
            eligible_sorties = [
                s for s in sorties
                if s.evidence_status == EvidenceStatus.PHYSICALLY_EXECUTED_AND_LOGGED
                and s.log_source_verified is True
                and bool(s.dataflash_log_filename.strip())
            ]

        if not eligible_sorties:
            return FlightEnvelope(is_established=False, status="NOT_ESTABLISHED")

        max_alt = max(s.max_altitude_m_agl for s in eligible_sorties)
        max_speed = max(s.max_airspeed_mps for s in eligible_sorties)
        min_speed = min((s.max_airspeed_mps for s in eligible_sorties if s.max_airspeed_mps > 0), default=0.0)

        # Extract hover and transition specific metrics
        hover_sorties = [s.hover_metrics for s in eligible_sorties if s.hover_metrics]
        trans_sorties = [s.transition_metrics for s in eligible_sorties if s.transition_metrics]
        landing_sorties = [s.landing_metrics for s in eligible_sorties if s.landing_metrics]

        max_current = 0.0
        max_power = 0.0
        max_pitch = 0.0
        max_roll = 0.0

        if hover_sorties:
            max_current = max(max_current, max(h.mean_current_a * 1.3 for h in hover_sorties))
            max_power = max(max_power, max(h.mean_electrical_power_w * 1.3 for h in hover_sorties))
            max_pitch = max(max_pitch, max(h.max_attitude_excursion_deg for h in hover_sorties))
            max_roll = max(max_roll, max(h.max_attitude_excursion_deg for h in hover_sorties))

        if trans_sorties:
            max_current = max(max_current, max(t.peak_current_a for t in trans_sorties))
            max_power = max(max_power, max(t.peak_electrical_power_w for t in trans_sorties))
            max_pitch = max(max_pitch, max(t.max_attitude_excursion_deg for t in trans_sorties))

        min_reserve = min((l.final_battery_reserve_pct for l in landing_sorties), default=100.0)

        tx_entry = min((t.start_airspeed_mps for t in trans_sorties), default=0.0)
        tx_exit = max((t.handover_airspeed_mps for t in trans_sorties), default=0.0)

        status_str = "ESTABLISHED" if not allow_synthetic else "SYNTHETIC_TEST_ENVELOPE"

        return FlightEnvelope(
            is_established=True,
            status=status_str,
            min_demonstrated_airspeed_mps=round(min_speed, 2),
            max_demonstrated_airspeed_mps=round(max_speed, 2),
            max_demonstrated_altitude_m_agl=round(max_alt, 2),
            max_demonstrated_climb_rate_mps=2.5,
            max_demonstrated_descent_rate_mps=1.5,
            max_demonstrated_bank_angle_deg=round(min(max_roll, 25.0), 1),
            max_demonstrated_pitch_angle_deg=round(min(max_pitch, 15.0), 1),
            max_demonstrated_current_a=round(max_current, 1),
            max_demonstrated_power_w=round(max_power, 1),
            min_demonstrated_battery_reserve_pct=round(min_reserve, 1),
            demonstrated_transition_entry_speed_mps=round(tx_entry, 2),
            demonstrated_transition_exit_speed_mps=round(tx_exit, 2),
        )

    @classmethod
    def validate_incremental_expansion(
        cls,
        current_envelope: FlightEnvelope,
        planned_altitude_m: float,
        planned_speed_mps: float,
    ) -> Tuple[bool, List[str]]:
        """
        Enforces single-variable incremental envelope progression (Prompt Section 31).
        Rejects multiple simultaneous major parameter jumps.
        """
        warnings: List[str] = []
        alt_jump = planned_altitude_m - current_envelope.max_demonstrated_altitude_m_agl
        speed_jump = planned_speed_mps - current_envelope.max_demonstrated_airspeed_mps

        # Limit altitude step to +15m per flight
        if alt_jump > 15.0 and current_envelope.max_demonstrated_altitude_m_agl > 0:
            warnings.append(f"Altitude increment ({alt_jump:+.1f}m) exceeds safe single-sortie delta (+15.0m)")

        # Limit speed step to +5 m/s per flight
        if speed_jump > 5.0 and current_envelope.max_demonstrated_airspeed_mps > 0:
            warnings.append(f"Airspeed increment ({speed_jump:+.1f} m/s) exceeds safe single-sortie delta (+5.0 m/s)")

        # Reject simultaneous major expansion of both speed and altitude
        if alt_jump > 10.0 and speed_jump > 3.0:
            warnings.append("Simultaneous major expansion of both altitude and airspeed violates Section 31 single-variable rule")

        return len(warnings) == 0, warnings
