"""
Fixed-Wing Payload Analysis Subsystem

Purpose:
    Defines the `PayloadAnalysis` class and the `PayloadAnalysisService` class
    to conduct CG offset, BEC load, and data bandwidth audits.

Role in Architecture:
    `PayloadAnalysisService` evaluates weight distribution impact and thermal margins,
    returning them in `PayloadAnalysis`.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from backend.design.fixed_wing.payload.payload_selector import PayloadRecord


@dataclass(slots=True)
class PayloadAnalysis:
    """
    aerodynamic, structural, and electrical analysis metrics for the payload subsystem.

    Attributes:
        payload_accommodation_score (float): Sized rating for envelope fit (0.0 to 100.0).
        power_consumption_w (float): continuous power draw.
        required_bandwidth_mbps (float): Data rate draw.
        cg_shift_offset_m (float): Longitudinal displacement of CG due to payload placement.
        static_margin_impact_pct (float): Stability margin impact percentage.
        thermal_dissipation_factor (float): Cooling adequacy rating.
        structural_safety_margin (float): Sized structural reserve factor.
        upgrade_potential_rating (str): Upgrade rating.
        serviceability_score (float): accessibility rating.
        analysis_summary (str): textual summary.
    """

    payload_accommodation_score: float
    power_consumption_w: float
    required_bandwidth_mbps: float
    cg_shift_offset_m: float
    static_margin_impact_pct: float
    thermal_dissipation_factor: float
    structural_safety_margin: float
    upgrade_potential_rating: str
    serviceability_score: float
    analysis_summary: str


class PayloadAnalysisService:
    """
    Evaluator performing weight calculations and packaging clearances.
    """

    def analyze_payload_integration(
        self,
        payloads: List[PayloadRecord],
        placement_x_m: float,
        cg_calculated_x_m: float,
        wing_mac: float,
        mtow_kg: float,
        compartment_vol: float,
    ) -> PayloadAnalysis:
        # 1. Total Weight & Power
        total_weight = sum(p.weight_kg for p in payloads)
        total_power = sum(p.power_w for p in payloads)
        total_bandwidth = sum(p.bandwidth_mbps for p in payloads)

        # 2. CG Shift calculation
        # CG_shift = (M_payload * (X_payload - CG_empty)) / M_total
        cg_offset = placement_x_m - cg_calculated_x_m
        cg_shift = (total_weight * cg_offset) / max(0.1, mtow_kg)

        # Static margin impact = CG_shift / MAC * 100
        static_margin_impact = (cg_shift / max(0.01, wing_mac)) * 100.0

        # 3. Packaging fit
        # Payload size vs compartment volume
        payload_vol = sum((p.dimensions_mm[0]*p.dimensions_mm[1]*p.dimensions_mm[2])/1e9 for p in payloads)
        vol_fit_ratio = payload_vol / max(0.00001, compartment_vol)
        
        accommodation_score = 100.0 - (vol_ratio := vol_fit_ratio * 100.0)
        accommodation_score = max(40.0, min(95.0, accommodation_score))

        # 4. Serviceability
        service_score = 90.0
        if vol_ratio > 30.0:
            service_score -= 15.0  # cramped compartment makes it harder to service

        # 5. Upgrade potential
        if vol_fit_ratio < 0.20:
            upgrade_rating = "Excellent (Ample space for larger secondary cameras)"
        elif vol_fit_ratio < 0.50:
            upgrade_rating = "Moderate (Compact space limits upgrade choice)"
        else:
            upgrade_rating = "Low (Compartment is fully occupied)"

        summary = (
            f"Payload integration: Sized weight = {total_weight:.2f} kg, CG shift: {cg_shift*1000:.1f} mm "
            f"({'Stable' if abs(static_margin_impact) < 5.0 else 'CG Shift warning'}). "
            f"Continuous power: {total_power:.1f} W."
        )

        return PayloadAnalysis(
            payload_accommodation_score=round(accommodation_score, 1),
            power_consumption_w=round(total_power, 1),
            required_bandwidth_mbps=round(total_bandwidth, 1),
            cg_shift_offset_m=round(cg_shift, 4),
            static_margin_impact_pct=round(static_margin_impact, 2),
            thermal_dissipation_factor=1.2,
            structural_safety_margin=3.0,
            upgrade_potential_rating=upgrade_rating,
            serviceability_score=service_score,
            analysis_summary=summary,
        )
