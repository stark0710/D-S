"""
Fixed-Wing Airfoil Reynolds Analysis Subsystem

Purpose:
    Defines the `ReynoldsAnalysis` class and the `ReynoldsAnalysisService` class
    to compute expected flight Reynolds numbers across the wing chord layout.

Role in Architecture:
    Provides calculated Reynolds numbers at root, tip, and MAC chords for cruise and stall speeds,
    enabling polar checking at realistic flow boundaries.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class ReynoldsAnalysis:
    """
    Data model holding Reynolds number results across the wing envelope.

    Attributes:
        re_root_cruise (float): Reynolds number at wing root chord under cruise speed.
        re_tip_cruise (float): Reynolds number at wing tip chord under cruise speed.
        re_mean_cruise (float): Reynolds number at mean aerodynamic chord under cruise speed.
        re_root_stall (float): Reynolds number at wing root chord under stall speed.
        re_tip_stall (float): Reynolds number at wing tip chord under stall speed.
        recommended_re_range (str): Textual description of recommended polar lookup bounds.
        metadata (Dict[str, Any]): Viscosity and operational speed inputs.
    """

    re_root_cruise: float
    re_tip_cruise: float
    re_mean_cruise: float
    re_root_stall: float
    re_tip_stall: float
    recommended_re_range: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReynoldsAnalysisService:
    """
    Service calculating flight Reynolds numbers based on dynamic viscosity and wing geometry.
    """

    def analyze_reynolds_envelope(
        self,
        air_density: float,
        cruise_speed_m_s: float,
        stall_speed_m_s: float,
        root_chord_m: float,
        tip_chord_m: float,
        mac_m: float,
        ambient_temp_c: float = 15.0,
    ) -> ReynoldsAnalysis:
        """
        Computes spanwise Reynolds numbers.
        """
        # Dynamic viscosity estimation of air (Sutherland's Law):
        # mu = mu_0 * (T_0 + S) / (T + S) * (T / T_0)^(3/2)
        # where T is absolute temperature in Kelvin.
        t_kelvin = ambient_temp_c + 273.15
        mu_0 = 1.7894e-5  # reference viscosity in Pa-s at T_0 = 273.11 K
        t_0 = 273.11
        s_sutherland = 110.56  # Sutherland constant for air
        
        mu = mu_0 * ((t_0 + s_sutherland) / (t_kelvin + s_sutherland)) * ((t_kelvin / t_0) ** 1.5)

        # Calculate Re = (rho * V * chord) / mu
        # Cruise
        re_root_cruise = (air_density * cruise_speed_m_s * root_chord_m) / mu
        re_tip_cruise = (air_density * cruise_speed_m_s * tip_chord_m) / mu if tip_chord_m > 0 else 0.0
        re_mean_cruise = (air_density * cruise_speed_m_s * mac_m) / mu

        # Stall
        re_root_stall = (air_density * stall_speed_m_s * root_chord_m) / mu
        re_tip_stall = (air_density * stall_speed_m_s * tip_chord_m) / mu if tip_chord_m > 0 else 0.0

        min_re = min(
            re_root_stall, 
            re_tip_stall if re_tip_stall > 0 else re_root_stall, 
            re_tip_cruise if re_tip_cruise > 0 else re_root_cruise
        )
        max_re = max(re_root_cruise, re_mean_cruise)

        re_range_desc = f"Reynolds range: {min_re:,.0f} to {max_re:,.0f}"

        return ReynoldsAnalysis(
            re_root_cruise=round(re_root_cruise, 1),
            re_tip_cruise=round(re_tip_cruise, 1),
            re_mean_cruise=round(re_mean_cruise, 1),
            re_root_stall=round(re_root_stall, 1),
            re_tip_stall=round(re_tip_stall, 1),
            recommended_re_range=re_range_desc,
            metadata={
                "air_viscosity_pa_s": round(mu, 8),
                "air_density_kg_m3": round(air_density, 4),
            }
        )
