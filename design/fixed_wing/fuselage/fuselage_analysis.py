"""
Fixed-Wing Fuselage Analysis Subsystem

Purpose:
    Defines the `FuselageAnalysis` class and the `FuselageAnalysisService` class
    to conduct packing checks, fineness ratio aerodynamic estimates, and accessibility audits.

Role in Architecture:
    Combines the results of fuselage geometry sizing and component placements into high-level, human-readable
    performance evaluations (volume utilization, accessibility, cooling paths).
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class FuselageAnalysis:
    """
    aerodynamic, structural, and packaging analysis metrics for the fuselage body.

    Attributes:
        packaging_efficiency_score (float): Internal systems packaging index (0.0 to 100.0).
        payload_accommodation_score (float): Sized rating for payload bay margin (0.0 to 100.0).
        aerodynamic_efficiency_score (float): Estimated fuselage aerodynamic drag score (0.0 to 100.0).
        manufacturability_score (float): Ease of fabrication score (0.0 to 100.0).
        component_accessibility_score (float): Maintenance access rating based on packing density (0.0 to 100.0).
        cooling_adequacy_score (float): Cooling airflow path evaluation score (0.0 to 100.0).
        volume_utilization_ratio (float): Ratio of utilized bay volumes to total fuselage volume.
        analysis_summary (str): textual summary of the fuselage analysis.
    """

    packaging_efficiency_score: float
    payload_accommodation_score: float
    aerodynamic_efficiency_score: float
    manufacturability_score: float
    component_accessibility_score: float
    cooling_adequacy_score: float
    volume_utilization_ratio: float
    analysis_summary: str


class FuselageAnalysisService:
    """
    Fuselage packaging evaluator analyzing volumetric densities and drag.
    """

    def analyze_fuselage(
        self,
        length: float,
        width: float,
        height: float,
        payload_vol: float,
        battery_vol: float,
        total_vol: float,
        tail_style: str,
        fuselage_type: str,
    ) -> FuselageAnalysis:
        # 1. Volume utilization ratio
        utilized_vol = payload_vol + battery_vol + 0.0003  # assume 300cm3 for avionics
        vol_ratio = utilized_vol / max(0.0001, total_vol)

        # 2. Packaging efficiency
        # Ideal packaging utilizes between 25% and 50% of the volume.
        # Too low = oversized empty fuselage (high drag). Too high = too cramped (heat issues, no accessibility).
        if 0.20 <= vol_ratio <= 0.45:
            packaging_score = 90.0
        elif vol_ratio < 0.20:
            packaging_score = 60.0  # too bulky
        else:
            packaging_score = 70.0  # cramped

        # 3. Aerodynamic efficiency (Fineness ratio L / D_eq where D_eq is average diameter)
        equiv_diam = (width + height) / 2.0
        fineness_ratio = length / max(0.01, equiv_diam)
        
        # Best aerodynamic fineness ratio for sub-sonic fuselages is 5.0 to 7.5.
        if 5.0 <= fineness_ratio <= 7.5:
            aero_score = 95.0
        elif fineness_ratio < 4.0:
            aero_score = 60.0  # too stubby (high drag)
        else:
            aero_score = 80.0  # slender, but has high surface friction drag

        # 4. Manufacturability
        if fuselage_type == "Conventional":
            mfg_score = 95.0
        elif fuselage_type == "Pod-and-Boom":
            mfg_score = 85.0
        elif fuselage_type in ("Twin Boom", "Blended Body"):
            mfg_score = 60.0
        else:
            mfg_score = 75.0

        # 5. Component accessibility
        # Cramped fuselage reduces accessibility
        accessibility_score = 100.0 - (vol_ratio * 120.0)
        accessibility_score = max(30.0, min(95.0, accessibility_score))

        # 6. Cooling adequacy
        # Lower density fuselages have better airflow
        cooling_score = 100.0 - (vol_ratio * 100.0)
        cooling_score = max(40.0, min(95.0, cooling_score))

        # 7. Summary
        summary = (
            f"Fuselage analysis: Fineness ratio = {fineness_ratio:.2f} ({'Optimal' if 5.0<=fineness_ratio<=7.5 else 'Suboptimal'}). "
            f"Volume utilization: {vol_ratio*100:.1f}%. Packaging score: {packaging_score:.1f}/100."
        )

        return FuselageAnalysis(
            packaging_efficiency_score=round(packaging_score, 1),
            payload_accommodation_score=85.0,
            aerodynamic_efficiency_score=round(aero_score, 1),
            manufacturability_score=mfg_score,
            component_accessibility_score=round(accessibility_score, 1),
            cooling_adequacy_score=round(cooling_score, 1),
            volume_utilization_ratio=round(vol_ratio, 3),
            analysis_summary=summary,
        )
