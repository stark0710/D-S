"""
VTOL Fixed-Wing Engineering Adapter / Interface Boundary

Purpose:
    Provides a clean, authoritative boundary connecting the VTOL backend to the
    locked Fixed-Wing engineering engines (wing, tail, fuselage, cruise propulsion,
    cruise aerodynamics/performance) WITHOUT duplicating any Fixed-Wing code.

Architecture:
    VTOL Requirements / Configuration
             │
             ▼
    FixedWingEngineeringAdapter
             │
             ▼
    Locked Fixed-Wing Engines / FixedWingDesignPipeline
             │
             ▼
    FixedWingSubsystemResult
             │
             ▼
    VTOL Aircraft Synthesis Stage
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import logging

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.design_mode import DesignMode

from backend.design.vtol.requirements.vtol_requirement_model import VTOLRequirementModel

logger = logging.getLogger(__name__)


@dataclass
class FixedWingSubsystemResult:
    """
    Typed container holding the cruise / fixed-wing subsystem results
    evaluated by the locked Fixed-Wing engineering backend.
    """
    fixed_wing_result: Optional[Any] = None
    wing: Optional[Any] = None
    tail: Optional[Any] = None
    fuselage: Optional[Any] = None
    cruise_propulsion: Optional[Any] = None
    cruise_performance: Optional[Any] = None
    airfoil: Optional[Any] = None
    status: str = "SUCCESS"  # SUCCESS, PARTIAL, FAILED
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_cruise_electrical_power_w(self) -> Optional[float]:
        """Extracts authoritative forward cruise electrical power in Watts."""
        if self.cruise_propulsion is not None:
            # Check direct attribute on PropulsionSpecification
            p_w = getattr(self.cruise_propulsion, "cruise_power_w", None)
            if p_w is not None and p_w > 0.0:
                return float(p_w)
            # Check nested power_analysis
            pa = getattr(self.cruise_propulsion, "power_analysis", None)
            if pa is not None:
                p_w = getattr(pa, "required_cruise_power_w", None)
                if p_w is not None and p_w > 0.0:
                    return float(p_w)
        if self.cruise_performance is not None:
            # Check FlightPerformanceSpecification
            p_w = getattr(self.cruise_performance, "power_required_w", None)
            if p_w is not None and p_w > 0.0:
                return float(p_w)
        return None

    def get_cruise_voltage_v(self) -> Optional[float]:
        """Extracts authoritative cruise operating voltage in Volts."""
        if self.cruise_propulsion is not None:
            v = getattr(self.cruise_propulsion, "operating_voltage_v", None)
            if v is not None and v > 0.0:
                return float(v)
            v = getattr(self.cruise_propulsion, "operating_voltage", None)
            if v is not None and v > 0.0:
                return float(v)
        return None

    def get_cruise_current_a(self) -> Optional[float]:
        """Extracts authoritative cruise operating current in Amperes."""
        if self.cruise_propulsion is not None:
            i_a = getattr(self.cruise_propulsion, "cruise_current_a", None)
            if i_a is not None and i_a > 0.0:
                return float(i_a)
            # Derive from power and voltage if both exist
            p = self.get_cruise_electrical_power_w()
            v = self.get_cruise_voltage_v()
            if p is not None and v is not None and v > 0.0:
                return float(p / v)
        return None

    def get_loiter_electrical_power_w(self) -> Optional[float]:
        """
        Extracts authoritative loiter electrical power if available from Fixed-Wing.
        Returns None if not explicitly modeled by the fixed-wing performance engine.
        """
        if self.cruise_performance is not None:
            loiter_p = getattr(self.cruise_performance, "loiter_power_w", None)
            if loiter_p is not None and loiter_p > 0.0:
                return float(loiter_p)
        return None

    def get_wing_mass_kg(self) -> Optional[float]:
        """Extracts authoritative wing structural mass in kg from Fixed-Wing."""
        if self.wing is not None:
            for attr in ("estimated_wing_weight_kg", "mass_kg", "estimated_weight_kg", "weight_kg"):
                val = getattr(self.wing, attr, None)
                if val is not None and float(val) > 0.0:
                    return float(val)
                # Check nested wing_structure if present
                ws = getattr(self.wing, "wing_structure", None)
                if ws is not None:
                    val = getattr(ws, attr, None)
                    if val is not None and float(val) > 0.0:
                        return float(val)
        return None

    def get_fuselage_mass_kg(self) -> Optional[float]:
        """Extracts authoritative fuselage structural mass in kg from Fixed-Wing."""
        if self.fuselage is not None:
            for attr in ("estimated_fuselage_weight_kg", "mass_kg", "estimated_weight_kg", "weight_kg"):
                val = getattr(self.fuselage, attr, None)
                if val is not None and float(val) > 0.0:
                    return float(val)
                fs = getattr(self.fuselage, "fuselage_structure", None)
                if fs is not None:
                    val = getattr(fs, attr, None)
                    if val is not None and float(val) > 0.0:
                        return float(val)
        return None

    def get_tail_mass_kg(self) -> Optional[float]:
        """Extracts authoritative tail structural mass in kg from Fixed-Wing."""
        if self.tail is not None:
            for attr in ("estimated_tail_weight_kg", "mass_kg", "estimated_weight_kg", "weight_kg"):
                val = getattr(self.tail, attr, None)
                if val is not None and float(val) > 0.0:
                    return float(val)
                ts = getattr(self.tail, "tail_structure", None)
                if ts is not None:
                    val = getattr(ts, attr, None)
                    if val is not None and float(val) > 0.0:
                        return float(val)
        return None

    def get_cruise_motor_mass_kg(self) -> Optional[float]:
        """Extracts authoritative forward cruise motor mass in kg from Fixed-Wing."""
        if self.cruise_propulsion is not None:
            for attr in ("motor_mass_kg", "mass_kg", "weight_kg"):
                val = getattr(self.cruise_propulsion, attr, None)
                if val is not None and float(val) > 0.0:
                    return float(val)
                ms = getattr(self.cruise_propulsion, "motor", None) or getattr(self.cruise_propulsion, "motor_selection", None)
                if ms is not None:
                    if isinstance(ms, dict):
                        m_val = ms.get("mass_kg") or ms.get("weight_kg")
                        if m_val is not None and float(m_val) > 0.0:
                            return float(m_val)
                    else:
                        val = getattr(ms, attr, None)
                        if val is not None and float(val) > 0.0:
                            return float(val)
        return None

    def get_wing_aerodynamic_center_x_m(self) -> Optional[float]:
        """Extracts authoritative wing aerodynamic center location from Fixed-Wing."""
        if self.wing is not None:
            # Check wing_geometry
            wg = getattr(self.wing, "wing_geometry", None) or self.wing
            ac = getattr(wg, "aerodynamic_center_x_m", None) or getattr(wg, "quarter_chord_x_m", None)
            if ac is not None and float(ac) > 0.0:
                return float(ac)
        return None

    def get_wing_mac_m(self) -> Optional[float]:
        """Extracts authoritative mean aerodynamic chord in meters from Fixed-Wing."""
        if self.wing is not None:
            wg = getattr(self.wing, "wing_geometry", None) or self.wing
            mac = getattr(wg, "mean_aerodynamic_chord_m", None) or getattr(wg, "mac_m", None) or getattr(wg, "mean_aerodynamic_chord", None)
            if mac is not None and float(mac) > 0.0:
                return float(mac)
        return None

    def get_wing_span_m(self) -> Optional[float]:
        """Extracts authoritative wingspan in meters from Fixed-Wing."""
        if self.wing is not None:
            wg = getattr(self.wing, "wing_geometry", None) or self.wing
            span = getattr(wg, "span_m", None) or getattr(wg, "wingspan_m", None) or getattr(wg, "span", None)
            if span is not None and float(span) > 0.0:
                return float(span)
        return None

    def get_wing_area_m2(self) -> Optional[float]:
        """Extracts authoritative wing planform area in m² from Fixed-Wing."""
        if self.wing is not None:
            wg = getattr(self.wing, "wing_geometry", None) or self.wing
            area = getattr(wg, "area_m2", None) or getattr(wg, "wing_area_m2", None) or getattr(wg, "area", None)
            if area is not None and float(area) > 0.0:
                return float(area)
        return None

    def get_wing_aspect_ratio(self) -> Optional[float]:
        """Extracts authoritative wing aspect ratio from Fixed-Wing."""
        if self.wing is not None:
            wg = getattr(self.wing, "wing_geometry", None) or self.wing
            ar = getattr(wg, "aspect_ratio", None)
            if ar is not None and float(ar) > 0.0:
                return float(ar)
        return None

    def get_airfoil_lift_curve_slope(self) -> Optional[float]:
        """Extracts authoritative 2D airfoil lift-curve slope (per radian) from Fixed-Wing."""
        if self.airfoil is not None:
            for attr in ("lift_curve_slope", "cl_alpha", "cla"):
                val = getattr(self.airfoil, attr, None)
                if val is not None and float(val) > 0.0:
                    return float(val)
                # Check nested polar or aerodynamic_properties
                ap = getattr(self.airfoil, "aerodynamic_properties", None) or getattr(self.airfoil, "polar", None)
                if ap is not None:
                    val = getattr(ap, attr, None)
                    if val is not None and float(val) > 0.0:
                        return float(val)
        return None

    def get_airfoil_cm0(self) -> Optional[float]:
        """Extracts authoritative zero-lift pitching moment coefficient C_m0 from Fixed-Wing."""
        if self.airfoil is not None:
            for attr in ("c_m0", "cm0", "zero_lift_pitching_moment"):
                val = getattr(self.airfoil, attr, None)
                if val is not None:
                    return float(val)
                ap = getattr(self.airfoil, "aerodynamic_properties", None) or getattr(self.airfoil, "polar", None)
                if ap is not None:
                    val = getattr(ap, attr, None)
                    if val is not None:
                        return float(val)
        return None

    def get_cruise_speed_m_s(self) -> Optional[float]:
        """Extracts authoritative forward cruise airspeed in m/s from Fixed-Wing."""
        if self.cruise_performance is not None:
            spd = getattr(self.cruise_performance, "cruise_speed_m_s", None)
            if spd is not None and float(spd) > 0.0:
                return float(spd)
            kmh = getattr(self.cruise_performance, "cruise_speed_kmh", None)
            if kmh is not None and float(kmh) > 0.0:
                return float(kmh) / 3.6
        return None

    def get_cruise_dynamic_pressure_pa(self, air_density_kg_m3: float = 1.225) -> Optional[float]:
        """Computes dynamic pressure q_inf = 0.5 * rho * V^2 at cruise speed."""
        v = self.get_cruise_speed_m_s()
        if v is not None and v > 0.0:
            return 0.5 * air_density_kg_m3 * (v ** 2)
        return None

    def get_tail_volume_coefficients(self) -> Tuple[Optional[float], Optional[float]]:
        """Extracts (V_H, V_V) tail volume coefficients from Fixed-Wing tail analysis."""
        vh, vv = None, None
        if self.tail is not None:
            ta = getattr(self.tail, "tail_analysis", None) or getattr(self.tail, "analysis", None)
            if ta is not None:
                vh = getattr(ta, "horizontal_volume_coefficient", None) or getattr(ta, "vh", None)
                vv = getattr(ta, "vertical_volume_coefficient", None) or getattr(ta, "vv", None)
        return (vh, vv)


class FixedWingEngineeringAdapter:
    """
    Authoritative adapter delegating cruise aerodynamics, wing, tail, fuselage,
    and forward propulsion sizing directly to the locked Fixed-Wing backend.
    """

    def __init__(self, raise_on_failure: bool = False) -> None:
        self.raise_on_failure = raise_on_failure

    def translate_to_fixed_wing_requirements(
        self,
        vtol_reqs: VTOLRequirementModel | RequirementModel,
    ) -> RequirementModel:
        """
        Translates VTOL requirements into canonical Fixed-Wing requirements
        expected by the locked Fixed-Wing pipeline.

        Args:
            vtol_reqs: VTOL requirement model or common requirement model.

        Returns:
            RequirementModel configured for Fixed-Wing cruise airframe synthesis.
        """
        pld = getattr(vtol_reqs, "payload_weight_kg", None)
        if pld is None:
            pld = getattr(vtol_reqs, "payload_mass", 2.0)

        rng = getattr(vtol_reqs, "target_range_km", None)
        if rng is None:
            rng = getattr(vtol_reqs, "target_range", 40.0)

        flight_t = getattr(vtol_reqs, "target_flight_time_min", None)
        if flight_t is None:
            flight_t = getattr(vtol_reqs, "target_flight_time", 30.0)

        cruise_spd = getattr(vtol_reqs, "cruise_speed_kmh", None)
        if cruise_spd is None:
            cruise_spd = getattr(vtol_reqs, "cruise_speed", 90.0)

        mtow = getattr(vtol_reqs, "maximum_takeoff_weight_kg", None)
        if mtow is None:
            mtow = getattr(vtol_reqs, "mtow_limit", None)

        env = getattr(vtol_reqs, "environment", None)
        if env is None:
            env = getattr(vtol_reqs, "operating_environment", OperatingEnvironment.RURAL)

        return RequirementModel(
            mission_type=getattr(vtol_reqs, "mission_type", MissionType.SURVEY),
            payload_weight_kg=float(pld),
            target_flight_time_min=float(flight_t),
            target_range_km=float(rng),
            cruise_speed_kmh=float(cruise_spd),
            aircraft_type=AircraftType.FIXED_WING,
            maximum_takeoff_weight_kg=float(mtow) if mtow is not None else None,
            budget=getattr(vtol_reqs, "budget", None),
            takeoff_type=TakeoffType.RUNWAY,
            landing_type=LandingType.RUNWAY,
            environment=env,
            optimization_priority=getattr(vtol_reqs, "optimization_priority", OptimizationPriority.BALANCED),
            design_mode=getattr(vtol_reqs, "design_mode", DesignMode.MANUAL),
            metadata=dict(getattr(vtol_reqs, "metadata", {}) or {}),
        )

    def size_cruise_subsystems(
        self,
        vtol_reqs: VTOLRequirementModel | RequirementModel,
    ) -> FixedWingSubsystemResult:
        """
        Executes Fixed-Wing sizing on the cruise portion of the VTOL aircraft
        using the locked FixedWingDesignPipeline.

        Args:
            vtol_reqs: VTOL requirement model.

        Returns:
            FixedWingSubsystemResult containing sized wing, tail, fuselage,
            propulsion, performance, and specification data.
        """
        notes: List[str] = []
        warnings: List[str] = []

        try:
            fw_reqs = self.translate_to_fixed_wing_requirements(vtol_reqs)
            notes.append(
                f"Translated VTOL requirements to Fixed-Wing cruise requirements "
                f"(Payload: {fw_reqs.payload_weight_kg:.2f} kg, Range: {fw_reqs.target_range_km:.1f} km, "
                f"Cruise Speed: {fw_reqs.cruise_speed_kmh:.1f} km/h)"
            )

            # Invoke locked FixedWingDesignPipeline lazily to avoid circular imports
            from backend.design.fixed_wing.pipeline.fixed_wing_design_pipeline import (
                FixedWingDesignPipeline,
            )

            pipeline = FixedWingDesignPipeline(raise_on_failure=self.raise_on_failure)
            result = pipeline.execute(fw_reqs)

            spec = getattr(result, "specification", None)
            wing = getattr(spec, "wing", None) if spec else None
            tail = getattr(spec, "tail", None) if spec else None
            fuselage = getattr(spec, "fuselage", None) if spec else None
            propulsion = getattr(spec, "propulsion", None) if spec else None
            perf = getattr(spec, "flight_performance", None) if spec else None
            airfoil = getattr(spec, "airfoil", None) if spec else None

            status_str = "SUCCESS" if getattr(result, "is_success", False) else "PARTIAL"
            if not getattr(result, "is_success", False):
                warnings.extend(getattr(result, "warnings", []))
                warnings.append("Fixed-Wing pipeline returned partial or non-converged result.")

            return FixedWingSubsystemResult(
                fixed_wing_result=result,
                wing=wing,
                tail=tail,
                fuselage=fuselage,
                cruise_propulsion=propulsion,
                cruise_performance=perf,
                airfoil=airfoil,
                status=status_str,
                notes=notes,
                warnings=warnings,
                metadata={
                    "fw_iterations": getattr(result, "iterations", 0),
                    "fw_converged": getattr(result, "converged", False),
                },
            )

        except Exception as e:
            logger.error(f"FixedWingEngineeringAdapter failed: {e}", exc_info=True)
            if self.raise_on_failure:
                raise
            return FixedWingSubsystemResult(
                status="FAILED",
                notes=notes,
                warnings=[f"FixedWingEngineeringAdapter execution failed: {str(e)}"],
            )
