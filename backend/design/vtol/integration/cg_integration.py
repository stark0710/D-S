"""
VTOL Phase 9 Integrated CG & Mass Reconciliation Engine.

Purpose:
    Computes installed 3D Center of Gravity (x_cg, y_cg, z_cg) from the discrete
    physical installation model, evaluates longitudinal stability margins against
    the Phase 6 CG envelope, and reconciles mass deltas between Phase 5 sizing,
    Phase 8 commercial BOM, and Phase 9 integrated installation.

Standards:
    - Does not alter Phase 5 or Phase 6 upstream physics equations.
    - Explicit envelope checking against forward (0.490m) and aft (0.542m) limits.
    - Evaluates UPSTREAM_REEVALUATION_REQUIRED only if the hardware delta exceeds 150g or 2.0% MTOW.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from backend.design.vtol.commercial.bom import CommercialBillOfMaterials
from backend.design.vtol.commercial.closure_engine import MassClosureEngine

from .integration_models import (
    ComponentLocation,
    IntegratedCGResult,
    MassReconciliationResult,
    ProvenanceCategory,
    VerificationCheckStatus,
)


class CGIntegrationEngine:
    """
    Evaluates discrete mass-moment equilibrium and longitudinal stability compliance.
    """

    # Authoritative Phase 6 Wing Aerodynamic Reference and CG Envelope
    DEFAULT_X_LEMAC_M = 0.4500
    DEFAULT_MAC_M = 0.2000
    DEFAULT_NEUTRAL_POINT_X_M = 0.5316
    DEFAULT_FORWARD_CG_LIMIT_M = 0.4900
    DEFAULT_AFT_CG_LIMIT_M = 0.5420

    # Phase 5 baseline references
    DEFAULT_PHASE5_MTOW_KG = 7.8690
    DEFAULT_PHASE5_HARDWARE_BASELINE_KG = 3.6570

    @classmethod
    def calculate_integrated_cg(
        cls,
        installed_components: List[ComponentLocation],
        x_lemac_m: Optional[float] = None,
        mac_m: Optional[float] = None,
        neutral_point_x_m: Optional[float] = None,
        forward_limit_m: Optional[float] = None,
        aft_limit_m: Optional[float] = None,
    ) -> IntegratedCGResult:
        """
        Calculates installed 3D CG and compares with stability envelope.
        """
        lemac = x_lemac_m or cls.DEFAULT_X_LEMAC_M
        mac = mac_m or cls.DEFAULT_MAC_M
        np_x = neutral_point_x_m or cls.DEFAULT_NEUTRAL_POINT_X_M
        fwd_lim = forward_limit_m or cls.DEFAULT_FORWARD_CG_LIMIT_M
        aft_lim = aft_limit_m or cls.DEFAULT_AFT_CG_LIMIT_M

        total_mass = sum(c.mass_kg for c in installed_components)
        if total_mass <= 0.0:
            return IntegratedCGResult(
                total_integrated_mass_kg=0.0,
                x_cg_m=0.0,
                y_cg_m=0.0,
                z_cg_m=0.0,
                x_lemac_m=lemac,
                mac_m=mac,
                cg_pct_mac=0.0,
                forward_limit_m=fwd_lim,
                aft_limit_m=aft_lim,
                forward_margin_m=0.0,
                aft_margin_m=0.0,
                static_margin_pct_mac=0.0,
                neutral_point_m=np_x,
                is_within_envelope=False,
                status=VerificationCheckStatus.FAIL,
                provenance=ProvenanceCategory.DERIVED,
                notes=["Total mass is zero or negative; cannot compute CG."],
            )

        sum_mx = sum(c.moment_x_kg_m for c in installed_components)
        sum_my = sum(c.moment_y_kg_m for c in installed_components)
        sum_mz = sum(c.moment_z_kg_m for c in installed_components)

        x_cg = sum_mx / total_mass
        y_cg = sum_my / total_mass
        z_cg = sum_mz / total_mass

        cg_pct_mac = ((x_cg - lemac) / mac) * 100.0 if mac > 0 else 0.0
        fwd_margin = x_cg - fwd_lim
        aft_margin = aft_lim - x_cg
        static_margin_pct = ((np_x - x_cg) / mac) * 100.0 if mac > 0 else 0.0

        notes: List[str] = []
        is_within_envelope = (fwd_margin >= 0.0) and (aft_margin >= 0.0)

        if not is_within_envelope:
            if fwd_margin < 0:
                notes.append(f"Installed x_cg ({x_cg:.4f}m) exceeds forward limit ({fwd_lim:.4f}m) by {abs(fwd_margin):.4f}m.")
            if aft_margin < 0:
                notes.append(f"Installed x_cg ({x_cg:.4f}m) exceeds aft limit ({aft_lim:.4f}m) by {abs(aft_margin):.4f}m.")
            status = VerificationCheckStatus.FAIL
        else:
            notes.append(
                f"Installed x_cg ({x_cg:.4f}m / {cg_pct_mac:.1f}% MAC) is well within Phase 6 stability envelope "
                f"[{fwd_lim:.4f}m, {aft_lim:.4f}m]. Forward margin: {fwd_margin:+.4f}m, Aft margin: {aft_margin:+.4f}m. "
                f"Static Margin: +{static_margin_pct:.2f}% MAC (Neutral Point: {np_x:.4f}m)."
            )
            status = VerificationCheckStatus.PASS

        return IntegratedCGResult(
            total_integrated_mass_kg=total_mass,
            x_cg_m=x_cg,
            y_cg_m=y_cg,
            z_cg_m=z_cg,
            x_lemac_m=lemac,
            mac_m=mac,
            cg_pct_mac=cg_pct_mac,
            forward_limit_m=fwd_lim,
            aft_limit_m=aft_lim,
            forward_margin_m=fwd_margin,
            aft_margin_m=aft_margin,
            static_margin_pct_mac=static_margin_pct,
            neutral_point_m=np_x,
            is_within_envelope=is_within_envelope,
            status=status,
            provenance=ProvenanceCategory.DERIVED,
            notes=notes,
        )

    @classmethod
    def reconcile_mass(
        cls,
        bom: CommercialBillOfMaterials,
        installed_components: List[ComponentLocation],
        phase5_mtow_kg: Optional[float] = None,
        phase5_hw_mass_kg: Optional[float] = None,
    ) -> MassReconciliationResult:
        """
        Reconciles Phase 5 baseline sizing mass against Phase 8 BOM and Phase 9 installed mass.
        """
        p5_mtow = phase5_mtow_kg or cls.DEFAULT_PHASE5_MTOW_KG
        p5_hw = phase5_hw_mass_kg or cls.DEFAULT_PHASE5_HARDWARE_BASELINE_KG
        p8_bom_mass = bom.total_commercial_mass_kg
        installed_total_mass = sum(c.mass_kg for c in installed_components)

        hw_delta = p8_bom_mass - p5_hw
        hw_delta_pct = (hw_delta / p5_mtow) * 100.0 if p5_mtow > 0 else 0.0

        thresh_mass = MassClosureEngine.REEVALUATION_DELTA_MASS_THRESHOLD_KG  # 0.150 kg
        thresh_pct = MassClosureEngine.REEVALUATION_DELTA_PCT_THRESHOLD      # 2.0%

        requires_reeval = (abs(hw_delta) >= thresh_mass) or (abs(hw_delta_pct) >= thresh_pct)

        # Categorized mass sums from installed components
        mounting_mass = sum(c.mass_kg for c in installed_components if "Wiring Harness" in c.component_name)
        struct_mass = sum(c.mass_kg for c in installed_components if c.role is None and "Wiring" not in c.component_name)
        payload_mass = sum(c.mass_kg for c in installed_components if c.role == "MISSION_PAYLOAD_CAMERA" or (c.role and c.role.value == "MISSION_PAYLOAD_CAMERA"))
        battery_mass = sum(c.mass_kg for c in installed_components if c.role == "BATTERY_MAIN" or (c.role and c.role.value == "BATTERY_MAIN"))
        avionics_mass = sum(c.mass_kg for c in installed_components if c.role in (
            "AUTOPILOT_PIXHAWK", "NAVIGATION_GNSS_RTK", "DIGITAL_AIRSPEED", "TELEMETRY_TRANSCEIVER", "RC_RECEIVER", "COMPANION_SBC"
        ) or (c.role and c.role.value in (
            "AUTOPILOT_PIXHAWK", "NAVIGATION_GNSS_RTK", "DIGITAL_AIRSPEED", "TELEMETRY_TRANSCEIVER", "RC_RECEIVER", "COMPANION_SBC"
        )))

        notes: List[str] = [
            f"Phase 5 Assumed Hardware Mass: {p5_hw:.3f} kg vs Phase 8 Commercial BOM: {p8_bom_mass:.3f} kg.",
            f"Hardware Mass Delta: {hw_delta:+.3f} kg ({hw_delta_pct:+.2f}% MTOW).",
            f"Re-evaluation Thresholds: +/-{thresh_mass:.3f} kg (+/-{thresh_pct:.1f}% MTOW).",
        ]

        if requires_reeval:
            notes.append("UPSTREAM_REEVALUATION_REQUIRED: Commercial hardware delta exceeds acceptable closure envelope.")
            status = VerificationCheckStatus.WARNING
        else:
            notes.append("Mass closed within acceptable tolerance; no upstream re-convergence required.")
            status = VerificationCheckStatus.PASS

        return MassReconciliationResult(
            phase5_mtow_kg=p5_mtow,
            phase5_hardware_mass_kg=p5_hw,
            phase8_bom_mass_kg=p8_bom_mass,
            phase9_installed_mass_kg=installed_total_mass,
            hardware_delta_kg=hw_delta,
            hardware_delta_pct_mtow=hw_delta_pct,
            mounting_hardware_mass_kg=mounting_mass,
            wiring_and_connectors_mass_kg=mounting_mass,
            structural_mass_kg=struct_mass,
            payload_mass_kg=payload_mass,
            battery_mass_kg=battery_mass,
            avionics_mass_kg=avionics_mass,
            upstream_reevaluation_required=requires_reeval,
            reevaluation_threshold_kg=thresh_mass,
            reevaluation_threshold_pct=thresh_pct,
            status=status,
            notes=notes,
        )
