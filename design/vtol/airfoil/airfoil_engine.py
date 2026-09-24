"""
VTOL Airfoil Sizing Engine Subsystem

Purpose:
    Defines the `AirfoilEngine` facade class orchestrating airfoil selection,
    polar corrections for propeller slipstream, downwash stall checks,
    and structural spar validation.
"""

from typing import List, Dict, Any
import math
from datetime import datetime

from backend.design.vtol.mission.mission_requirements import VTOLType
from backend.design.vtol.airfoil.airfoil_requirements import AirfoilRequirements
from backend.design.vtol.airfoil.airfoil_result import AirfoilResult
from backend.design.vtol.airfoil.polar_analysis import PolarAnalysis
from backend.design.vtol.airfoil.transition_analysis import TransitionAnalysis
from backend.design.vtol.airfoil.stall_analysis import StallAnalysis
from backend.design.vtol.airfoil.manufacturing_analysis import ManufacturingAnalysis
from backend.design.vtol.airfoil.airfoil_validator import AirfoilValidator
from backend.design.vtol.airfoil.airfoil_registry import VTOLAirfoilStrategyRegistry
from backend.design.vtol.airfoil.airfoil_selector import AirfoilSelector
from backend.design.vtol.airfoil.airfoil_database import AirfoilDatabase


class AirfoilEngine:
    """
    Facade orchestrator driving airfoil sizing, polars, and interaction analysis.
    """

    def __init__(
        self,
        validator: AirfoilValidator | None = None,
        selector: AirfoilSelector | None = None,
    ) -> None:
        self._validator = validator or AirfoilValidator()
        self._selector = selector or AirfoilSelector()

    def design_airfoil(self, requirements: AirfoilRequirements) -> AirfoilResult:
        """
        Orchestrates selection and analysis of the wing airfoil profile.

        Args:
            requirements (AirfoilRequirements): overrides and preceding results.

        Returns:
            AirfoilResult: Complete airfoil characterization.
        """
        mission_res = requirements.mission_result
        config_res = requirements.configuration_result
        wing_res = requirements.wing_result

        # 1. Strategy selection
        strategy = VTOLAirfoilStrategyRegistry.get(mission_res.mission_profile.mission_category)

        # 2. Airfoil Selection
        selected_name = self._selector.select_best_airfoil(requirements, strategy)
        db_entry = AirfoilDatabase.get_airfoil(selected_name)
        if db_entry is None:
            # Fallback
            selected_name = "Clark Y"
            db_entry = AirfoilDatabase.get_airfoil(selected_name)

        # Extract airfoil parameters
        thick_ratio = db_entry["thickness_ratio"]
        camber = db_entry["camber"]
        cm0 = db_entry["cm0"]
        cd0 = db_entry["cd0"]
        cl_max_db = db_entry["cl_max"]

        # 3. Solve Reynolds Number
        root_chord = wing_res.wing_geometry.root_chord_m
        taper = wing_res.wing_geometry.taper_ratio
        mac = root_chord * (2.0 / 3.0) * ((1.0 + taper + taper**2) / (1.0 + taper))

        v_cruise = mission_res.cruise_requirements.cruise_speed_kmh / 3.6
        viscosity = 1.48e-5  # Kinematic viscosity of standard air
        reynolds = (v_cruise * mac) / viscosity

        # 4. Polar analysis with propeller slipstream correction
        # Propeller slipstream increases dynamic pressure behind the rotor
        # We size slipstream factor based on propulsion configuration
        has_slipstream = config_res.selected_configuration in (
            VTOLType.QUADPLANE,
            VTOLType.LIFT_CRUISE,
            VTOLType.TILT_ROTOR,
            VTOLType.TILT_WING,
        )
        slipstream_factor = 1.15 if has_slipstream else 1.0

        cl_cruise_freestream = wing_res.wing_analysis.cruise_lift_coefficient
        # Sized lift coefficient corrected for higher slipstream velocity
        cl_corrected = cl_cruise_freestream / slipstream_factor

        # Parabolic drag polar estimation: Cd = Cd0 + k * (Cl - Cl_opt)^2
        # Lift optimum camber Cl_opt is roughly camber * 10
        cl_opt = camber * 1.0
        k = 0.015  # profile drag polar curvature constant
        cd_corrected = cd0 + k * (cl_corrected - cl_opt) ** 2
        ld_ratio = cl_corrected / max(0.001, cd_corrected)

        polar_anal = PolarAnalysis(
            cl_cruise=round(cl_corrected, 3),
            cd_cruise=round(cd_corrected, 5),
            lift_to_drag_ratio_sectional=round(ld_ratio, 2),
            pitching_moment_cruise=round(cm0, 3),
            slipstream_correction_factor=slipstream_factor,
            metadata={"reynolds_number": round(reynolds, 0)},
        )

        # 5. Transition aerodynamics: angles of attack and flow separation
        flow_detachment = 15.0 + (camber * 100.0)
        suit = "Excellent" if flow_detachment > 18.0 else "Good"
        if selected_name == "Selig S1223":
            suit = "Marginal"  # Selig has very high drag at high AoA

        trans_anal = TransitionAnalysis(
            transition_aoa_range_deg=(0.0, 18.0),
            flow_detachment_angle_deg=round(flow_detachment, 1),
            separated_flow_drag_coefficient=1.12,
            pitch_stability_margin_transition=round(0.15 + abs(cm0), 3),
            suitability_rating=suit,
        )

        # 6. Stall performance under rotor downwash
        mtow = mission_res.mission_analysis.estimated_mtow_kg
        # Approximate rotor induced downwash: v = sqrt(T / (2 * rho * A))
        downwash = 4.5 * math.sqrt(mtow / 10.0)
        downwash_angle = math.degrees(math.atan2(downwash, max(1.0, v_cruise)))

        stall_behavior = "Gentle"
        if selected_name == "Selig S1223":
            stall_behavior = "Sharp"
        elif thick_ratio < 0.09:
            stall_behavior = "Progressive"

        stall_anal = StallAnalysis(
            cl_max=cl_max_db,
            stall_angle_deg=round(14.0 + camber * 100.0, 1),
            downwash_velocity_m_s=round(downwash, 2),
            downwash_angle_deg=round(downwash_angle, 2),
            stall_behavior=stall_behavior,
        )

        # 7. Manufacturing and packaging structural analysis
        wing_thickness_mm = root_chord * thick_ratio * 1000.0
        # Maximum carbon spar diameter that can fit within 75% of thickness envelope
        max_spar_mm = wing_thickness_mm * 0.75

        foam_score = 90.0
        if selected_name == "Selig S1223":
            foam_score = 70.0  # Deep under-camber is very difficult to wire-cut

        mfg_anal = ManufacturingAnalysis(
            foam_cut_feasibility_score=foam_score,
            mold_release_feasibility_score=85.0,
            min_trailing_edge_thickness_mm=1.8,
            carbon_spar_diameter_max_mm=round(max_spar_mm, 1),
            suitability_rating="Excellent" if foam_score >= 80.0 else "Good",
        )

        # 8. Sizing geometry values for output
        geom = {
            "thickness_ratio": thick_ratio,
            "camber": camber,
            "le_radius": db_entry["le_radius"],
            "max_thickness_loc": db_entry["max_thickness_loc"],
            "max_camber_loc": db_entry["max_camber_loc"],
            "cm0": cm0,
        }

        # 9. Recommendations, Warnings, Notes
        notes = [
            f"Airfoil Selector matched: {selected_name}.",
            f"Sized wing root physical thickness: {wing_thickness_mm:.1f} mm.",
            f"Estimated max allowable carbon tube spar diameter: {max_spar_mm:.1f} mm.",
        ]

        recs = strategy.get_recommendations(selected_name)
        warnings: List[str] = []

        if has_slipstream:
            notes.append("Propeller slipstream velocity correction applied to dynamic pressure.")
        if cm0 < -0.10:
            warnings.append("High pitching moment airfoil selected. Sizing must account for extra tail trim drag.")

        # 10. Assemble complete result
        result = AirfoilResult(
            selected_airfoil=selected_name,
            airfoil_geometry=geom,
            polar_analysis=polar_anal,
            transition_analysis=trans_anal,
            stall_analysis=stall_anal,
            manufacturing_analysis=mfg_anal,
            engineering_notes=notes,
            recommendations=recs,
            warnings=warnings,
        )

        # 11. Run validations (raises AirfoilValidationError if invalid)
        self._validator.validate(requirements, result)

        # Metadata info
        meta = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.__class__.__name__,
        }
        result.metadata = meta

        return result
