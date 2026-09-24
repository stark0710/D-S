"""
VTOL Authoritative Hover Performance and Lift Sizing Physics Engine.

Purpose:
    Provides the single authoritative, configuration-driven, manufacturer-independent
    engineering model for VTOL hover performance and vertical lift system requirements.

Key Relationships:
    - Weight: W = m * g (g = 9.80665 m/s^2)
    - Required Total Hover Thrust: T_req = W * (T/W)_req
    - Lift Motor Count: N sourced from authoritative VTOLConfiguration (QuadPlane default = 4)
    - Per-Motor Thrust: T_per_motor = T_req / N
    - Thrust Margin: T_margin = T_req - W
    - Total Rotor Disk Area: A_total = N * pi * (D / 2)^2 (when diameter D is available)
    - Hover Power (Momentum Theory):
        v_i = sqrt(T_req / (2 * rho * A_total))
        P_ideal = T_req * v_i
        P_induced = kappa * P_ideal (kappa = 1.15)
        P_profile = f_profile * P_induced (f_profile = 0.25)
        P_aero = P_induced + P_profile
        P_electrical = P_aero / eta_elec (eta_elec = 0.85)
        P_per_motor = P_electrical / N
    - Hover Current: I = P_electrical / V (when voltage V is available)
        I_per_motor = I / N

Architecture Standards:
    - Typed dataclass outputs
    - Manufacturer-independent technical requirements
    - Traceable physics without arbitrary hidden magic multipliers
    - Explicit distinction between sizing mass and converged MTOW (Phase 5)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import math


GRAVITATIONAL_ACCELERATION_M_S2: float = 9.80665
STANDARD_AIR_DENSITY_KG_M3: float = 1.225
DEFAULT_HOVER_THRUST_TO_WEIGHT: float = 1.20
DEFAULT_INDUCED_POWER_CORRECTION_FACTOR: float = 1.15  # kappa (tip losses + non-uniform inflow)
DEFAULT_PROFILE_DRAG_POWER_FRACTION: float = 0.25      # f_profile (blade profile drag fraction)
DEFAULT_ELECTRICAL_EFFICIENCY: float = 0.85            # Combined motor and ESC efficiency


class HoverPhysicsValidationError(ValueError):
    """Raised when hover physical inputs violate engineering invariants."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


@dataclass(slots=True)
class AuthoritativeHoverResult:
    """
    Authoritative engineering sizing result for VTOL hover performance.
    """
    # Mass & Weight
    sizing_mass_kg: float
    aircraft_weight_n: float

    # Thrust sizing
    hover_thrust_to_weight_target: float
    required_total_hover_thrust_n: float
    lift_motor_count: int
    required_thrust_per_motor_n: float
    thrust_margin_n: float
    thrust_margin_ratio: float

    # Aerodynamics & Geometry (Available when rotor diameter is specified)
    rotor_diameter_m: Optional[float] = None
    total_disk_area_m2: Optional[float] = None
    disk_loading_n_m2: Optional[float] = None
    induced_velocity_m_s: Optional[float] = None

    # Power requirements [W]
    ideal_induced_power_w: Optional[float] = None
    actual_induced_power_w: Optional[float] = None
    profile_drag_power_w: Optional[float] = None
    total_aerodynamic_power_w: Optional[float] = None
    hover_electrical_power_w: Optional[float] = None
    hover_power_per_motor_w: Optional[float] = None

    # Electrical requirements (Available when voltage is specified)
    system_voltage_v: Optional[float] = None
    hover_current_a: Optional[float] = None
    hover_current_per_motor_a: Optional[float] = None

    # Physical environment and sizing factors
    air_density_kg_m3: float = STANDARD_AIR_DENSITY_KG_M3
    induced_power_correction_factor: float = DEFAULT_INDUCED_POWER_CORRECTION_FACTOR
    profile_drag_power_fraction: float = DEFAULT_PROFILE_DRAG_POWER_FRACTION
    electrical_efficiency: float = DEFAULT_ELECTRICAL_EFFICIENCY

    # MTOW & Convergence Interface (Phase 5 boundary)
    is_converged_mtow: bool = False
    mtow_status: str = "PRE_CONVERGENCE_SIZING"

    # Stage Status Semantics
    status: str = "IMPLEMENTED"
    engineering_assumptions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a serializable dictionary."""
        return {
            "sizing_mass_kg": round(self.sizing_mass_kg, 4),
            "aircraft_weight_n": round(self.aircraft_weight_n, 4),
            "hover_thrust_to_weight_target": round(self.hover_thrust_to_weight_target, 3),
            "required_total_hover_thrust_n": round(self.required_total_hover_thrust_n, 3),
            "lift_motor_count": self.lift_motor_count,
            "required_thrust_per_motor_n": round(self.required_thrust_per_motor_n, 3),
            "thrust_margin_n": round(self.thrust_margin_n, 3),
            "thrust_margin_ratio": round(self.thrust_margin_ratio, 3),
            "rotor_diameter_m": round(self.rotor_diameter_m, 4) if self.rotor_diameter_m is not None else None,
            "total_disk_area_m2": round(self.total_disk_area_m2, 4) if self.total_disk_area_m2 is not None else None,
            "disk_loading_n_m2": round(self.disk_loading_n_m2, 3) if self.disk_loading_n_m2 is not None else None,
            "induced_velocity_m_s": round(self.induced_velocity_m_s, 3) if self.induced_velocity_m_s is not None else None,
            "ideal_induced_power_w": round(self.ideal_induced_power_w, 2) if self.ideal_induced_power_w is not None else None,
            "actual_induced_power_w": round(self.actual_induced_power_w, 2) if self.actual_induced_power_w is not None else None,
            "profile_drag_power_w": round(self.profile_drag_power_w, 2) if self.profile_drag_power_w is not None else None,
            "total_aerodynamic_power_w": round(self.total_aerodynamic_power_w, 2) if self.total_aerodynamic_power_w is not None else None,
            "hover_electrical_power_w": round(self.hover_electrical_power_w, 2) if self.hover_electrical_power_w is not None else None,
            "hover_power_per_motor_w": round(self.hover_power_per_motor_w, 2) if self.hover_power_per_motor_w is not None else None,
            "system_voltage_v": round(self.system_voltage_v, 2) if self.system_voltage_v is not None else None,
            "hover_current_a": round(self.hover_current_a, 2) if self.hover_current_a is not None else None,
            "hover_current_per_motor_a": round(self.hover_current_per_motor_a, 2) if self.hover_current_per_motor_a is not None else None,
            "air_density_kg_m3": round(self.air_density_kg_m3, 4),
            "induced_power_correction_factor": self.induced_power_correction_factor,
            "profile_drag_power_fraction": self.profile_drag_power_fraction,
            "electrical_efficiency": self.electrical_efficiency,
            "is_converged_mtow": self.is_converged_mtow,
            "mtow_status": self.mtow_status,
            "status": self.status,
            "engineering_assumptions": list(self.engineering_assumptions),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "metadata": dict(self.metadata),
        }


class AuthoritativeHoverModel:
    """
    Authoritative hover performance engineering calculation engine.
    """

    @classmethod
    def calculate_hover_state(
        cls,
        sizing_mass_kg: float,
        lift_motor_count: int,
        rotor_diameter_m: Optional[float] = None,
        system_voltage_v: Optional[float] = None,
        hover_thrust_to_weight_target: float = DEFAULT_HOVER_THRUST_TO_WEIGHT,
        air_density_kg_m3: float = STANDARD_AIR_DENSITY_KG_M3,
        induced_power_correction_factor: float = DEFAULT_INDUCED_POWER_CORRECTION_FACTOR,
        profile_drag_power_fraction: float = DEFAULT_PROFILE_DRAG_POWER_FRACTION,
        electrical_efficiency: float = DEFAULT_ELECTRICAL_EFFICIENCY,
        is_converged_mtow: bool = False,
    ) -> AuthoritativeHoverResult:
        """
        Executes authoritative hover performance calculations based on Momentum Theory.

        Raises:
            HoverPhysicsValidationError: If fundamental physical parameters are non-physical.
        """
        errors: List[str] = []
        warnings: List[str] = []
        assumptions: List[str] = []

        # 1. Invariant Validation
        if sizing_mass_kg <= 0.0:
            errors.append(f"Invalid sizing mass: {sizing_mass_kg} kg <= 0. Aircraft mass must be strictly positive.")
        if lift_motor_count <= 0:
            errors.append(f"Invalid lift motor count: {lift_motor_count} <= 0. Motor count must be strictly positive.")
        if hover_thrust_to_weight_target < 1.0:
            errors.append(
                f"Invalid hover thrust-to-weight target: {hover_thrust_to_weight_target:.2f} < 1.00. "
                "Hover flight requires at least T/W >= 1.0 to overcome gravity."
            )
        if rotor_diameter_m is not None and rotor_diameter_m <= 0.0:
            errors.append(f"Invalid rotor diameter: {rotor_diameter_m} m <= 0. Diameter must be strictly positive.")
        if system_voltage_v is not None and system_voltage_v <= 0.0:
            errors.append(f"Invalid system voltage: {system_voltage_v} V <= 0. Voltage must be strictly positive.")
        if air_density_kg_m3 <= 0.0:
            errors.append(f"Invalid air density: {air_density_kg_m3} kg/m³ <= 0. Air density must be positive.")

        if errors:
            raise HoverPhysicsValidationError(errors)

        # 2. Fundamental Weight and Thrust Requirements
        # W = m * g
        weight_n = sizing_mass_kg * GRAVITATIONAL_ACCELERATION_M_S2
        assumptions.append(f"Aircraft weight derived via W = mass * g (g = {GRAVITATIONAL_ACCELERATION_M_S2} m/s²).")

        # T_req = W * (T/W)_target
        req_total_thrust_n = weight_n * hover_thrust_to_weight_target
        assumptions.append(
            f"Required total hover thrust derived via T_req = W * (T/W)_target ((T/W)_target = {hover_thrust_to_weight_target:.2f})."
        )

        # T_per_motor = T_req / N
        req_thrust_per_motor_n = req_total_thrust_n / lift_motor_count
        assumptions.append(
            f"Per-motor thrust derived via T_per_motor = T_req / N (N = {lift_motor_count} from authoritative configuration)."
        )

        thrust_margin_n = req_total_thrust_n - weight_n
        thrust_margin_ratio = req_total_thrust_n / weight_n

        # 3. Disk Area & Aerodynamic Hover Power (Requires Rotor Diameter)
        total_disk_area: Optional[float] = None
        disk_loading: Optional[float] = None
        induced_vel: Optional[float] = None
        p_ideal: Optional[float] = None
        p_induced: Optional[float] = None
        p_profile: Optional[float] = None
        p_aero: Optional[float] = None
        p_electrical: Optional[float] = None
        p_per_motor: Optional[float] = None

        if rotor_diameter_m is not None:
            # A_single = pi * (D/2)^2
            # A_total = N * A_single
            total_disk_area = lift_motor_count * math.pi * ((rotor_diameter_m / 2.0) ** 2)
            disk_loading = weight_n / total_disk_area
            assumptions.append(
                f"Total disk area A = N * pi * (D/2)² = {total_disk_area:.4f} m² (D = {rotor_diameter_m:.3f} m, N = {lift_motor_count})."
            )

            # Induced velocity from Momentum Theory: v_i = sqrt(T / (2 * rho * A))
            induced_vel = math.sqrt(req_total_thrust_n / (2.0 * air_density_kg_m3 * total_disk_area))
            p_ideal = req_total_thrust_n * induced_vel

            # Actual induced power with inflow/tip-loss correction factor kappa
            p_induced = p_ideal * induced_power_correction_factor

            # Profile drag power fraction
            p_profile = p_induced * profile_drag_power_fraction

            # Total aerodynamic power
            p_aero = p_induced + p_profile

            # Total electrical power accounting for combined motor and ESC efficiency
            p_electrical = p_aero / electrical_efficiency
            p_per_motor = p_electrical / lift_motor_count

            assumptions.append(
                f"Hover power modeled via Momentum Theory: kappa={induced_power_correction_factor:.2f}, "
                f"f_profile={profile_drag_power_fraction:.2f}, eta_elec={electrical_efficiency:.2f}."
            )
        else:
            warnings.append(
                "Rotor diameter not provided in requirements/configuration. Total disk area, hover power, "
                "and current are deferred to when rotor geometry is established."
            )

        # 4. Hover Current (Requires Electrical Voltage)
        hover_current_total: Optional[float] = None
        hover_current_per_motor: Optional[float] = None

        if p_electrical is not None:
            if system_voltage_v is not None:
                hover_current_total = p_electrical / system_voltage_v
                hover_current_per_motor = hover_current_total / lift_motor_count
                assumptions.append(
                    f"Hover current derived via I = P_elec / V (V = {system_voltage_v:.1f} V, I = {hover_current_total:.2f} A)."
                )
            else:
                warnings.append(
                    "System voltage not provided. Hover current calculation is deferred."
                )

        # 5. Status Semantics
        if rotor_diameter_m is not None and system_voltage_v is not None:
            stage_status = "IMPLEMENTED"
        else:
            stage_status = "PARTIAL"

        mtow_status_desc = "CONVERGED_MTOW" if is_converged_mtow else "PRE_CONVERGENCE_SIZING"

        return AuthoritativeHoverResult(
            sizing_mass_kg=sizing_mass_kg,
            aircraft_weight_n=weight_n,
            hover_thrust_to_weight_target=hover_thrust_to_weight_target,
            required_total_hover_thrust_n=req_total_thrust_n,
            lift_motor_count=lift_motor_count,
            required_thrust_per_motor_n=req_thrust_per_motor_n,
            thrust_margin_n=thrust_margin_n,
            thrust_margin_ratio=thrust_margin_ratio,
            rotor_diameter_m=rotor_diameter_m,
            total_disk_area_m2=total_disk_area,
            disk_loading_n_m2=disk_loading,
            induced_velocity_m_s=induced_vel,
            ideal_induced_power_w=p_ideal,
            actual_induced_power_w=p_induced,
            profile_drag_power_w=p_profile,
            total_aerodynamic_power_w=p_aero,
            hover_electrical_power_w=p_electrical,
            hover_power_per_motor_w=p_per_motor,
            system_voltage_v=system_voltage_v,
            hover_current_a=hover_current_total,
            hover_current_per_motor_a=hover_current_per_motor,
            air_density_kg_m3=air_density_kg_m3,
            induced_power_correction_factor=induced_power_correction_factor,
            profile_drag_power_fraction=profile_drag_power_fraction,
            electrical_efficiency=electrical_efficiency,
            is_converged_mtow=is_converged_mtow,
            mtow_status=mtow_status_desc,
            status=stage_status,
            engineering_assumptions=assumptions,
            warnings=warnings,
            errors=errors,
            metadata={
                "architecture_reference": "QuadPlane / Lift + Cruise",
                "gravitational_acceleration_m_s2": GRAVITATIONAL_ACCELERATION_M_S2,
            },
        )
