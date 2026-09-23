"""
VTOL Authoritative Transition Engineering and Flight Corridor Physics Engine.

Purpose:
    Provides the authoritative, configuration-driven, manufacturer-independent
    engineering model for the VTOL <-> Fixed-Wing transition corridor (QuadPlane / Lift + Cruise).

Physics Formulations:
    - Aircraft Weight: W = m * g (g = 9.80665 m/s^2)
    - Dynamic Pressure: q = 0.5 * rho * V^2
    - Wing Lift: L = 0.5 * rho * V^2 * S * CL
    - Stall Speed: V_stall = sqrt(2 * W / (rho * S * CL_max))
    - Safe Transition Speed: V_trans >= 1.20 * V_stall
    - Wing Lift Fraction: f_wing = min(1.0, max(0.0, L / W))
    - Required Vertical Thrust: T_vert = max(0.0, W - L)
    - Vertical Thrust Fraction: f_vert = T_vert / W = 1.0 - f_wing
    - Per-Motor Vertical Thrust: T_vert_per_motor = T_vert / N
    - Aerodynamic Drag: D = q * S * CD
    - Forward Acceleration Thrust: T_accel = m * (V_trans / t_trans)
    - Forward Propulsion Thrust: T_fwd = D + T_accel
    - Transition Directions:
        - TRANSITION_TO_CRUISE: Accelerates from hover (V=0) to fixed-wing cruise (V=V_trans)
        - TRANSITION_TO_VTOL: Decelerates from fixed-wing cruise to hover (V=0)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import math

GRAVITATIONAL_ACCELERATION_M_S2: float = 9.80665
STANDARD_AIR_DENSITY_KG_M3: float = 1.225
DEFAULT_TRANSITION_CL_FRACTION: float = 0.70  # Effective transition CL as fraction of CL_max
DEFAULT_CL_MAX: float = 1.40
DEFAULT_CD0: float = 0.035
DEFAULT_OSWALD_EFFICIENCY: float = 0.80
DEFAULT_INDUCED_POWER_CORRECTION: float = 1.15
DEFAULT_PROFILE_DRAG_FRACTION: float = 0.25
DEFAULT_LIFT_ELECTRICAL_EFFICIENCY: float = 0.85
DEFAULT_CRUISE_PROPULSION_EFFICIENCY: float = 0.78


class TransitionPhysicsValidationError(ValueError):
    """Raised when transition engineering inputs violate physical boundaries."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


@dataclass(slots=True)
class TransitionOperatingPoint:
    """
    Physical metrics at a discrete operating airspeed point along the transition corridor.
    """
    stage_name: str
    airspeed_kmh: float
    airspeed_m_s: float
    dynamic_pressure_pa: float
    wing_lift_n: float
    wing_lift_fraction: float
    required_vertical_thrust_n: float
    vertical_thrust_fraction: float
    vertical_thrust_per_motor_n: float
    aerodynamic_drag_n: float
    forward_thrust_n: float
    vertical_electrical_power_w: float
    forward_electrical_power_w: float
    total_electrical_power_w: float
    is_wing_supported: bool
    is_aerodynamically_feasible: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_name": self.stage_name,
            "airspeed_kmh": round(self.airspeed_kmh, 2),
            "airspeed_m_s": round(self.airspeed_m_s, 2),
            "dynamic_pressure_pa": round(self.dynamic_pressure_pa, 2),
            "wing_lift_n": round(self.wing_lift_n, 2),
            "wing_lift_fraction": round(self.wing_lift_fraction, 4),
            "required_vertical_thrust_n": round(self.required_vertical_thrust_n, 2),
            "vertical_thrust_fraction": round(self.vertical_thrust_fraction, 4),
            "vertical_thrust_per_motor_n": round(self.vertical_thrust_per_motor_n, 2),
            "aerodynamic_drag_n": round(self.aerodynamic_drag_n, 2),
            "forward_thrust_n": round(self.forward_thrust_n, 2),
            "vertical_electrical_power_w": round(self.vertical_electrical_power_w, 2),
            "forward_electrical_power_w": round(self.forward_electrical_power_w, 2),
            "total_electrical_power_w": round(self.total_electrical_power_w, 2),
            "is_wing_supported": self.is_wing_supported,
            "is_aerodynamically_feasible": self.is_aerodynamically_feasible,
        }


@dataclass(slots=True)
class AuthoritativeTransitionResult:
    """
    Consolidated authoritative sizing outputs for the VTOL transition flight corridor.
    """
    direction: str
    sizing_mass_kg: float
    aircraft_weight_n: float
    wing_area_m2: float
    lift_motor_count: int
    air_density_kg_m3: float
    cl_transition: float
    cl_max: float
    stall_speed_kmh: float
    transition_speed_kmh: float
    transition_duration_s: float
    corridor_points: List[TransitionOperatingPoint]
    earliest_wing_supported_airspeed_kmh: float
    fixed_wing_entry_airspeed_kmh: float
    peak_forward_thrust_n: float
    peak_electrical_power_w: float
    total_energy_kwh: float

    # Phase 5 MTOW interface boundary
    is_converged_mtow: bool = False
    mtow_status: str = "PRE_CONVERGENCE_SIZING"

    # Status semantics
    status: str = "IMPLEMENTED"
    engineering_assumptions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "direction": self.direction,
            "sizing_mass_kg": round(self.sizing_mass_kg, 4),
            "aircraft_weight_n": round(self.aircraft_weight_n, 3),
            "wing_area_m2": round(self.wing_area_m2, 4),
            "lift_motor_count": self.lift_motor_count,
            "air_density_kg_m3": round(self.air_density_kg_m3, 4),
            "cl_transition": round(self.cl_transition, 3),
            "cl_max": round(self.cl_max, 3),
            "stall_speed_kmh": round(self.stall_speed_kmh, 2),
            "transition_speed_kmh": round(self.transition_speed_kmh, 2),
            "transition_duration_s": round(self.transition_duration_s, 2),
            "earliest_wing_supported_airspeed_kmh": round(self.earliest_wing_supported_airspeed_kmh, 2),
            "fixed_wing_entry_airspeed_kmh": round(self.fixed_wing_entry_airspeed_kmh, 2),
            "peak_forward_thrust_n": round(self.peak_forward_thrust_n, 2),
            "peak_electrical_power_w": round(self.peak_electrical_power_w, 2),
            "total_energy_kwh": round(self.total_energy_kwh, 5),
            "is_converged_mtow": self.is_converged_mtow,
            "mtow_status": self.mtow_status,
            "status": self.status,
            "corridor_points": [p.to_dict() for p in self.corridor_points],
            "engineering_assumptions": list(self.engineering_assumptions),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "metadata": dict(self.metadata),
        }


class AuthoritativeTransitionModel:
    """
    Physics calculation engine for VTOL conversion / transition flight corridors.
    """

    @classmethod
    def calculate_transition_corridor(
        cls,
        sizing_mass_kg: float,
        wing_area_m2: float,
        lift_motor_count: int = 4,
        direction: str = "TRANSITION_TO_CRUISE",
        preferred_transition_speed_kmh: Optional[float] = None,
        preferred_transition_duration_s: Optional[float] = None,
        air_density_kg_m3: float = STANDARD_AIR_DENSITY_KG_M3,
        cl_max: float = DEFAULT_CL_MAX,
        cl_transition: Optional[float] = None,
        aspect_ratio: float = 8.5,
        rotor_diameter_m: Optional[float] = None,
        is_converged_mtow: bool = False,
    ) -> AuthoritativeTransitionResult:
        """
        Calculates the aerodynamic and propulsive transition corridor.

        Raises:
            TransitionPhysicsValidationError: If inputs are unphysical.
        """
        errors: List[str] = []
        warnings: List[str] = []
        assumptions: List[str] = []

        # 1. Physical Invariant Validation
        if sizing_mass_kg <= 0.0:
            errors.append(f"Invalid sizing mass: {sizing_mass_kg} kg <= 0. Mass must be positive.")
        if wing_area_m2 <= 0.0:
            errors.append(f"Invalid wing area: {wing_area_m2} m² <= 0. Wing area must be positive.")
        if lift_motor_count <= 0:
            errors.append(f"Invalid lift motor count: {lift_motor_count} <= 0. Motor count must be positive.")
        if air_density_kg_m3 <= 0.0:
            errors.append(f"Invalid air density: {air_density_kg_m3} kg/m³ <= 0. Density must be positive.")
        if cl_max <= 0.0:
            errors.append(f"Invalid CL_max: {cl_max} <= 0. Maximum lift coefficient must be positive.")
        if preferred_transition_speed_kmh is not None and preferred_transition_speed_kmh <= 0.0:
            errors.append(f"Invalid preferred transition speed: {preferred_transition_speed_kmh} km/h <= 0.")
        if preferred_transition_duration_s is not None and preferred_transition_duration_s <= 0.0:
            errors.append(f"Invalid preferred transition duration: {preferred_transition_duration_s} s <= 0.")

        norm_direction = direction.strip().upper()
        if norm_direction not in ("TRANSITION_TO_CRUISE", "TRANSITION_TO_VTOL"):
            errors.append(
                f"Invalid transition direction: '{direction}'. "
                "Must be 'TRANSITION_TO_CRUISE' (forward) or 'TRANSITION_TO_VTOL' (reverse)."
            )

        if errors:
            raise TransitionPhysicsValidationError(errors)

        # 2. Fundamental Aircraft Weight
        # W = m * g
        weight_n = sizing_mass_kg * GRAVITATIONAL_ACCELERATION_M_S2
        assumptions.append(f"Aircraft weight derived via W = mass * g (g = {GRAVITATIONAL_ACCELERATION_M_S2} m/s²).")

        # 3. Aerodynamic Sizing (Stall Speed & Conversion Speed)
        # V_stall = sqrt(2 * W / (rho * S * CL_max))
        v_stall_m_s = math.sqrt((2.0 * weight_n) / (air_density_kg_m3 * wing_area_m2 * cl_max))
        v_stall_kmh = v_stall_m_s * 3.6
        assumptions.append(
            f"Stall speed derived via V_stall = sqrt(2*W / (rho*S*CL_max)) = {v_stall_kmh:.2f} km/h (CL_max={cl_max:.2f})."
        )

        min_safe_trans_speed_kmh = 1.20 * v_stall_kmh

        if preferred_transition_speed_kmh is not None:
            if preferred_transition_speed_kmh < v_stall_kmh:
                warnings.append(
                    f"Preferred transition speed ({preferred_transition_speed_kmh:.1f} km/h) is below stall speed "
                    f"({v_stall_kmh:.1f} km/h). Clamped to minimum safe conversion speed ({min_safe_trans_speed_kmh:.1f} km/h)."
                )
                v_trans_kmh = min_safe_trans_speed_kmh
            elif preferred_transition_speed_kmh < min_safe_trans_speed_kmh:
                warnings.append(
                    f"Preferred transition speed ({preferred_transition_speed_kmh:.1f} km/h) has low stall margin (< 1.2*V_stall). "
                    f"Recommended conversion speed is at least {min_safe_trans_speed_kmh:.1f} km/h."
                )
                v_trans_kmh = preferred_transition_speed_kmh
            else:
                v_trans_kmh = preferred_transition_speed_kmh
        else:
            # Sizing default: 1.25 * V_stall or 55.0 km/h minimum for conventional trainer scale
            v_trans_kmh = max(55.0, 1.25 * v_stall_kmh)

        v_trans_m_s = v_trans_kmh / 3.6

        # Effective transition CL
        if cl_transition is not None and cl_transition > 0.0:
            effective_cl = min(cl_max, cl_transition)
        else:
            effective_cl = cl_max * DEFAULT_TRANSITION_CL_FRACTION

        # Transition duration
        duration_s = preferred_transition_duration_s if preferred_transition_duration_s is not None else 18.0

        # Rotor swept disk area for vertical power calculations
        prop_diam = rotor_diameter_m if (rotor_diameter_m is not None and rotor_diameter_m > 0.0) else 0.40
        total_disk_area_m2 = lift_motor_count * math.pi * ((prop_diam / 2.0) ** 2)

        # 4. Discrete Corridor Operating Points
        # Standard corridor checkpoints:
        # Hover (0%), Early (25%), Intermediate (50%), Blended (75%), Cruise Entry (100%)
        fractions = [0.0, 0.25, 0.50, 0.75, 1.0]
        stage_names = [
            "Hover Departure" if norm_direction == "TRANSITION_TO_CRUISE" else "Hover Entry",
            "Early Conversion" if norm_direction == "TRANSITION_TO_CRUISE" else "Late Deceleration",
            "Blended Mid-Transition",
            "Wing-Supported Handover" if norm_direction == "TRANSITION_TO_CRUISE" else "Vertical Rotor Engagement",
            "Fixed-Wing Cruise Entry" if norm_direction == "TRANSITION_TO_CRUISE" else "Fixed-Wing Deceleration Entry",
        ]

        if norm_direction == "TRANSITION_TO_VTOL":
            # Reverse sequence from cruise entry down to hover
            fractions = list(reversed(fractions))
            stage_names = list(reversed(stage_names))

        # Forward acceleration thrust requirement: T_accel = m * (V_trans / duration)
        a_trans = v_trans_m_s / duration_s
        t_accel_n = sizing_mass_kg * a_trans

        corridor_points: List[TransitionOperatingPoint] = []
        earliest_wing_supported_speed: Optional[float] = None
        peak_fwd_thrust: float = 0.0
        peak_power: float = 0.0

        for frac, name in zip(fractions, stage_names):
            v_kmh = frac * v_trans_kmh
            v_m_s = v_kmh / 3.6

            # Dynamic pressure q = 0.5 * rho * V^2
            q = 0.5 * air_density_kg_m3 * (v_m_s ** 2)

            # Wing lift: L = q * S * CL (capped at total weight W to prevent unphysical excess vertical acceleration)
            l_wing_raw = q * wing_area_m2 * effective_cl
            l_wing = min(weight_n, l_wing_raw)
            f_wing = min(1.0, max(0.0, l_wing / weight_n))

            # Remaining vertical thrust requirement: T_vert = max(0, W - L)
            t_vert = max(0.0, weight_n - l_wing)
            f_vert = t_vert / weight_n
            t_vert_per_motor = t_vert / lift_motor_count

            # Aerodynamic Drag: CD = CD0 + CL^2 / (pi * AR * e) + delta_CD_rotors
            induced_cd = (effective_cl ** 2) / (math.pi * aspect_ratio * DEFAULT_OSWALD_EFFICIENCY)
            rotor_parasitic_cd = 0.020 * f_vert  # Drag of exposed stationary/spinning lift rotors
            cd_total = DEFAULT_CD0 + induced_cd + rotor_parasitic_cd
            drag_n = q * wing_area_m2 * cd_total

            # Forward propulsion thrust
            if norm_direction == "TRANSITION_TO_CRUISE":
                # Must overcome aerodynamic drag plus acceleration thrust
                # When V=0, forward thrust provides initial forward acceleration
                t_fwd = drag_n + (t_accel_n if frac < 1.0 else 0.0)
            else:
                # Deceleration: forward thrust throttles back; aerodynamic drag decelerates the aircraft
                # Residual forward thrust keeps airflow steady
                t_fwd = max(0.0, drag_n - t_accel_n * 0.5)

            peak_fwd_thrust = max(peak_fwd_thrust, t_fwd)

            # Vertical electrical power from Momentum Theory
            if t_vert > 0.001:
                v_i = math.sqrt(t_vert / (2.0 * air_density_kg_m3 * total_disk_area_m2))
                p_vert_ind = DEFAULT_INDUCED_POWER_CORRECTION * t_vert * v_i
                p_vert_prof = p_vert_ind * DEFAULT_PROFILE_DRAG_FRACTION
                p_vert_aero = p_vert_ind + p_vert_prof
                p_vert_elec = p_vert_aero / DEFAULT_LIFT_ELECTRICAL_EFFICIENCY
            else:
                p_vert_elec = 0.0

            # Forward electrical power
            if v_m_s > 0.001:
                p_fwd_mech = t_fwd * v_m_s
                p_fwd_elec = p_fwd_mech / DEFAULT_CRUISE_PROPULSION_EFFICIENCY
            else:
                # Static forward thrust consumption
                p_fwd_elec = (t_fwd * 2.5) / DEFAULT_CRUISE_PROPULSION_EFFICIENCY if t_fwd > 0 else 0.0

            p_total_elec = p_vert_elec + p_fwd_elec
            peak_power = max(peak_power, p_total_elec)

            is_wing_borne = f_wing >= 0.70
            if is_wing_borne and earliest_wing_supported_speed is None:
                earliest_wing_supported_speed = v_kmh

            feasible = True
            if frac >= 0.99 and f_wing < 0.90:
                feasible = False  # Failed to generate full wing lift at conversion speed

            corridor_points.append(
                TransitionOperatingPoint(
                    stage_name=name,
                    airspeed_kmh=v_kmh,
                    airspeed_m_s=v_m_s,
                    dynamic_pressure_pa=q,
                    wing_lift_n=l_wing,
                    wing_lift_fraction=f_wing,
                    required_vertical_thrust_n=t_vert,
                    vertical_thrust_fraction=f_vert,
                    vertical_thrust_per_motor_n=t_vert_per_motor,
                    aerodynamic_drag_n=drag_n,
                    forward_thrust_n=t_fwd,
                    vertical_electrical_power_w=p_vert_elec,
                    forward_electrical_power_w=p_fwd_elec,
                    total_electrical_power_w=p_total_elec,
                    is_wing_supported=is_wing_borne,
                    is_aerodynamically_feasible=feasible,
                )
            )

        if earliest_wing_supported_speed is None:
            earliest_wing_supported_speed = v_stall_kmh

        # Integrated energy over transition duration (trapezoidal integration)
        dt = duration_s / (len(corridor_points) - 1)
        total_energy_ws = 0.0
        for i in range(len(corridor_points) - 1):
            p1 = corridor_points[i].total_electrical_power_w
            p2 = corridor_points[i + 1].total_electrical_power_w
            total_energy_ws += 0.5 * (p1 + p2) * dt

        energy_kwh = total_energy_ws / (3600.0 * 1000.0)

        mtow_status_desc = "CONVERGED_MTOW" if is_converged_mtow else "PRE_CONVERGENCE_SIZING"

        return AuthoritativeTransitionResult(
            direction=norm_direction,
            sizing_mass_kg=sizing_mass_kg,
            aircraft_weight_n=weight_n,
            wing_area_m2=wing_area_m2,
            lift_motor_count=lift_motor_count,
            air_density_kg_m3=air_density_kg_m3,
            cl_transition=effective_cl,
            cl_max=cl_max,
            stall_speed_kmh=v_stall_kmh,
            transition_speed_kmh=v_trans_kmh,
            transition_duration_s=duration_s,
            corridor_points=corridor_points,
            earliest_wing_supported_airspeed_kmh=earliest_wing_supported_speed,
            fixed_wing_entry_airspeed_kmh=v_trans_kmh,
            peak_forward_thrust_n=peak_fwd_thrust,
            peak_electrical_power_w=peak_power,
            total_energy_kwh=energy_kwh,
            is_converged_mtow=is_converged_mtow,
            mtow_status=mtow_status_desc,
            status="IMPLEMENTED",
            engineering_assumptions=assumptions,
            warnings=warnings,
            errors=errors,
            metadata={
                "architecture_reference": "QuadPlane / Lift + Cruise",
                "gravitational_acceleration_m_s2": GRAVITATIONAL_ACCELERATION_M_S2,
                "corridor_checkpoints": len(corridor_points),
            },
        )
