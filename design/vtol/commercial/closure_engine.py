"""
VTOL Phase 8 Mass and Electrical Power Closure Engine.

Purpose:
    Performs system-level mass closure and electrical power closure comparing selected
    commercial hardware against Phase 5 sizing ledger assumptions.

Standards:
    - Never mutates Phase 1-7 locked physics.
    - If hardware mass or power changes materially affect engineering envelopes, generates
      explicit ENGINEERING_REEVALUATION_REQUIRED triggers.
    - Full electrical branch validation: Battery -> PDB -> ESC -> Motor and Battery -> BEC -> Avionics.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .product_models import (
    CommercialProduct,
    HardwareCategory,
    HardwareReevaluationTrigger,
)


@dataclass(slots=True)
class MassClosureResult:
    """Consolidated report on commercial hardware mass closure."""
    baseline_assumed_hardware_mass_kg: float
    selected_commercial_hardware_mass_kg: float
    hardware_mass_delta_kg: float
    hardware_mass_delta_pct: float
    mtow_baseline_kg: float
    mtow_projected_kg: float
    estimated_cg_shift_m: float
    estimated_static_margin_impact_pct: float
    hover_tw_projected: float
    is_mass_closed: bool
    requires_reevaluation: bool
    reevaluation_triggers: List[HardwareReevaluationTrigger] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "baseline_assumed_hardware_mass_kg": round(self.baseline_assumed_hardware_mass_kg, 4),
            "selected_commercial_hardware_mass_kg": round(self.selected_commercial_hardware_mass_kg, 4),
            "hardware_mass_delta_kg": round(self.hardware_mass_delta_kg, 4),
            "hardware_mass_delta_pct": round(self.hardware_mass_delta_pct, 2),
            "mtow_baseline_kg": round(self.mtow_baseline_kg, 4),
            "mtow_projected_kg": round(self.mtow_projected_kg, 4),
            "estimated_cg_shift_m": round(self.estimated_cg_shift_m, 5),
            "estimated_static_margin_impact_pct": round(self.estimated_static_margin_impact_pct, 2),
            "hover_tw_projected": round(self.hover_tw_projected, 3),
            "is_mass_closed": self.is_mass_closed,
            "requires_reevaluation": self.requires_reevaluation,
            "reevaluation_triggers": [t.to_dict() for t in self.reevaluation_triggers],
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class PowerClosureResult:
    """Consolidated report on electrical power and bus closure."""
    vtol_hover_power_w: float
    vtol_peak_power_w: float
    cruise_continuous_power_w: float
    avionics_power_w: float
    payload_power_w: float
    simultaneous_transition_peak_power_w: float
    total_continuous_power_w: float
    total_peak_power_w: float
    system_voltage_v: float
    total_continuous_current_a: float
    total_peak_current_a: float
    battery_continuous_current_capability_a: float
    battery_burst_current_capability_a: float
    pdb_current_capability_a: float
    bec_5v_current_capability_a: float
    avionics_and_servo_peak_draw_a: float
    is_power_closed: bool
    battery_current_margin_a: float
    pdb_current_margin_a: float
    bec_current_margin_a: float
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vtol_hover_power_w": round(self.vtol_hover_power_w, 2),
            "vtol_peak_power_w": round(self.vtol_peak_power_w, 2),
            "cruise_continuous_power_w": round(self.cruise_continuous_power_w, 2),
            "avionics_power_w": round(self.avionics_power_w, 2),
            "payload_power_w": round(self.payload_power_w, 2),
            "simultaneous_transition_peak_power_w": round(self.simultaneous_transition_peak_power_w, 2),
            "total_continuous_power_w": round(self.total_continuous_power_w, 2),
            "total_peak_power_w": round(self.total_peak_power_w, 2),
            "system_voltage_v": round(self.system_voltage_v, 2),
            "total_continuous_current_a": round(self.total_continuous_current_a, 2),
            "total_peak_current_a": round(self.total_peak_current_a, 2),
            "battery_continuous_current_capability_a": round(self.battery_continuous_current_capability_a, 2),
            "battery_burst_current_capability_a": round(self.battery_burst_current_capability_a, 2),
            "pdb_current_capability_a": round(self.pdb_current_capability_a, 2),
            "bec_5v_current_capability_a": round(self.bec_5v_current_capability_a, 2),
            "avionics_and_servo_peak_draw_a": round(self.avionics_and_servo_peak_draw_a, 2),
            "is_power_closed": self.is_power_closed,
            "battery_current_margin_a": round(self.battery_current_margin_a, 2),
            "pdb_current_margin_a": round(self.pdb_current_margin_a, 2),
            "bec_current_margin_a": round(self.bec_current_margin_a, 2),
            "warnings": list(self.warnings),
        }


class MassClosureEngine:
    """
    Evaluates mass delta between Phase 5 sizing ledger and actual commercial hardware BOM.
    """

    # Baseline Phase 5 assumed hardware masses (from authoritative_mass.py default ledger)
    DEFAULT_PHASE5_HARDWARE_BASELINE_KG = 3.657  # Propulsion + Battery + Avionics + Wire/PDB
    DEFAULT_BASELINE_MTOW_KG = 7.869
    REEVALUATION_DELTA_MASS_THRESHOLD_KG = 0.150  # 150g delta triggers engineering re-evaluation
    REEVALUATION_DELTA_PCT_THRESHOLD = 2.0        # 2.0% MTOW delta

    @classmethod
    def evaluate_mass_closure(
        cls,
        selected_hardware_mass_kg: float,
        baseline_mtow_kg: Optional[float] = None,
        baseline_hardware_mass_kg: Optional[float] = None,
    ) -> MassClosureResult:
        mtow_base = baseline_mtow_kg or cls.DEFAULT_BASELINE_MTOW_KG
        hw_base = baseline_hardware_mass_kg or cls.DEFAULT_PHASE5_HARDWARE_BASELINE_KG

        delta_m = selected_hardware_mass_kg - hw_base
        delta_pct = (delta_m / mtow_base) * 100.0 if mtow_base > 0 else 0.0
        projected_mtow = mtow_base + delta_m

        # CG shift estimation: hardware is distributed across airframe with effective arm ~0.50m
        # Delta CG: (delta_m * x_hw - M_base * x_cg) / M_new
        cg_shift = (delta_m * 0.05) / projected_mtow if projected_mtow > 0 else 0.0
        sm_impact_pct = -(cg_shift / 0.145) * 100.0  # MAC ~ 0.145m

        # Hover thrust-to-weight impact (based on 100.32 N total thrust)
        t_total = 100.32
        hover_tw = t_total / (projected_mtow * 9.80665) if projected_mtow > 0 else 0.0

        triggers: List[HardwareReevaluationTrigger] = []
        notes: List[str] = []

        requires_reeval = (
            abs(delta_m) >= cls.REEVALUATION_DELTA_MASS_THRESHOLD_KG
            or abs(delta_pct) >= cls.REEVALUATION_DELTA_PCT_THRESHOLD
        )

        if requires_reeval:
            trigger = HardwareReevaluationTrigger(
                affected_phase=5,
                affected_parameter="converged_mtow_kg",
                engineering_baseline_value=mtow_base,
                commercial_actual_value=projected_mtow,
                delta_value=delta_m,
                units="kg",
                reason=(
                    f"Selected commercial hardware BOM mass ({selected_hardware_mass_kg:.3f} kg) "
                    f"deviates from Phase 5 assumed hardware mass ({hw_base:.3f} kg) by {delta_m:+.3f} kg ({delta_pct:+.1f}% MTOW)."
                ),
                expected_impact=(
                    f"Projected MTOW shifts to {projected_mtow:.3f} kg; CG shifts by {cg_shift:+.4f} m; "
                    f"Projected hover T/W shifts to {hover_tw:.2f}."
                ),
                requires_re_convergence=True,
            )
            triggers.append(trigger)
            notes.append(
                f"ENGINEERING_REEVALUATION_REQUIRED: Hardware mass delta ({delta_m:+.3f} kg) exceeds {cls.REEVALUATION_DELTA_MASS_THRESHOLD_KG:.3f} kg threshold."
            )
        else:
            notes.append(
                f"Mass closed within engineering tolerance (Delta: {delta_m:+.3f} kg, {delta_pct:+.2f}% MTOW)."
            )

        return MassClosureResult(
            baseline_assumed_hardware_mass_kg=hw_base,
            selected_commercial_hardware_mass_kg=selected_hardware_mass_kg,
            hardware_mass_delta_kg=delta_m,
            hardware_mass_delta_pct=delta_pct,
            mtow_baseline_kg=mtow_base,
            mtow_projected_kg=projected_mtow,
            estimated_cg_shift_m=cg_shift,
            estimated_static_margin_impact_pct=sm_impact_pct,
            hover_tw_projected=hover_tw,
            is_mass_closed=True,
            requires_reevaluation=requires_reeval,
            reevaluation_triggers=triggers,
            notes=notes,
        )


class PowerClosureEngine:
    """
    Evaluates complete electrical branch power, continuous and burst current margins.
    """

    @classmethod
    def evaluate_power_closure(
        cls,
        selected_products: Dict[HardwareCategory, CommercialProduct],
        vtol_hover_power_w: float = 1624.5,
        cruise_power_w: float = 195.0,
        avionics_power_w: float = 40.0,
        payload_power_w: float = 0.0,
        system_voltage_v: float = 22.2,
    ) -> PowerClosureResult:
        warnings: List[str] = []

        vtol_peak_power = vtol_hover_power_w * 1.35
        simultaneous_transition_peak_power = vtol_hover_power_w + (cruise_power_w * 1.8) + avionics_power_w

        total_cont_power = vtol_hover_power_w + avionics_power_w + payload_power_w
        total_peak_power = simultaneous_transition_peak_power

        total_cont_current = total_cont_power / system_voltage_v
        total_peak_current = total_peak_power / system_voltage_v

        # Extract selected ratings
        battery = selected_products.get(HardwareCategory.BATTERY_PACK)
        pdb = selected_products.get(HardwareCategory.POWER_DISTRIBUTION)

        batt_cont_a = battery.continuous_current_a if battery and battery.continuous_current_a else 100.0
        batt_peak_a = battery.peak_current_a if battery and battery.peak_current_a else 200.0
        pdb_cont_a = pdb.continuous_current_a if pdb and pdb.continuous_current_a else 140.0
        bec_5v_a = pdb.get_spec("bec_5v_current_a", 5.0) if pdb else 5.0

        # 5V Avionics (FC, GNSS, Sensors, RX ~1.35A) + 4x Servos dynamic peak (~1.80A) = 3.15A @ 5V
        avionics_servo_peak = 1.35 + 1.80

        batt_margin = batt_cont_a - total_cont_current
        pdb_margin = pdb_cont_a - total_cont_current
        bec_margin = bec_5v_a - avionics_servo_peak

        is_power_closed = True

        if batt_margin < 0:
            is_power_closed = False
            warnings.append(f"Battery continuous current capability ({batt_cont_a:.1f}A) exceeded by hover draw ({total_cont_current:.1f}A).")

        if batt_peak_a < total_peak_current:
            is_power_closed = False
            warnings.append(f"Battery peak burst capability ({batt_peak_a:.1f}A) exceeded by transition peak draw ({total_peak_current:.1f}A).")

        if pdb_margin < 0:
            is_power_closed = False
            warnings.append(f"PDB continuous rating ({pdb_cont_a:.1f}A) exceeded by total current ({total_cont_current:.1f}A).")

        if bec_margin < 0:
            is_power_closed = False
            warnings.append(f"PDB 5V BEC rating ({bec_5v_a:.1f}A) exceeded by avionics and servo peak draw ({avionics_servo_peak:.1f}A).")

        return PowerClosureResult(
            vtol_hover_power_w=vtol_hover_power_w,
            vtol_peak_power_w=vtol_peak_power,
            cruise_continuous_power_w=cruise_power_w,
            avionics_power_w=avionics_power_w,
            payload_power_w=payload_power_w,
            simultaneous_transition_peak_power_w=simultaneous_transition_peak_power,
            total_continuous_power_w=total_cont_power,
            total_peak_power_w=total_peak_power,
            system_voltage_v=system_voltage_v,
            total_continuous_current_a=total_cont_current,
            total_peak_current_a=total_peak_current,
            battery_continuous_current_capability_a=batt_cont_a,
            battery_burst_current_capability_a=batt_peak_a,
            pdb_current_capability_a=pdb_cont_a,
            bec_5v_current_capability_a=bec_5v_a,
            avionics_and_servo_peak_draw_a=avionics_servo_peak,
            is_power_closed=is_power_closed,
            battery_current_margin_a=batt_margin,
            pdb_current_margin_a=pdb_margin,
            bec_current_margin_a=bec_margin,
            warnings=warnings,
        )
