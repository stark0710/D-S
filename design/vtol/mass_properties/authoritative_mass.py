"""
VTOL Phase 5 — Authoritative Multidisciplinary Mass, CG & MTOW Convergence Subsystem

Purpose:
    Provides the single authoritative VTOL mass properties calculation,
    longitudinal center-of-gravity (CG) evaluation, component mass ledger,
    and true iterative MTOW convergence engine for the Torq Wings VTOL backend.

Architecture:
    Assumed Mass (M_k)
          │
          ├──► Phase 2 Hover Physics (P_hover)
          ├──► Phase 3 Transition Physics (E_trans)
          ├──► Fixed-Wing Adapter Cruise Propulsion (P_cruise)
          ├──► Phase 4 Electrical Engine (E_nominal, m_battery)
          ├──► Upstream Structure (Wing, Fuselage, Tail)
          ├──► Upstream Avionics & Payload
          │
          ▼
    AuthoritativeMassModel.synthesize_mass(...)
          │
          ├── 1. 6-Category Mass Ledger (Structure, Propulsion, Electrical, Avionics, Payload, Other)
          ├── 2. Complete Provenance Tagging (DERIVED, PROJECT_REQ, CONFIG_ASSUMPTION, UNRESOLVED, DEFERRED)
          ├── 3. Battery Mass Direct Coupling (m_battery = E_nominal / SE)
          ├── 4. Propulsion Segregation (N_lift * m_lift + 1 * m_cruise)
          ├── 5. Independent Total Mass Synthesis (M_calculated = sum(m_i))
          ├── 6. Longitudinal CG & Moment Calculation (Datum: FUSELAGE_NOSE)
          ├── 7. True Convergence Residual (|M_calculated - M_k| <= tol)
          └── 8. Under-Relaxation (M_{k+1} = alpha * M_calculated + (1-alpha) * M_k)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import math
import logging

logger = logging.getLogger(__name__)


class MassCategory(str, Enum):
    """Authoritative mass ledger categories."""
    STRUCTURE = "STRUCTURE"
    PROPULSION = "PROPULSION"
    ELECTRICAL = "ELECTRICAL"
    AVIONICS = "AVIONICS"
    PAYLOAD = "PAYLOAD"
    OTHER = "OTHER"


class MassClassification(str, Enum):
    """Provenance classification taxonomy."""
    DERIVED = "DERIVED"
    PROJECT_REQUIREMENT = "PROJECT_REQUIREMENT"
    CONFIGURABLE_ASSUMPTION = "CONFIGURABLE_ASSUMPTION"
    CATALOG_REQUIRED = "CATALOG_REQUIRED"
    UNRESOLVED = "UNRESOLVED"
    DEFERRED = "DEFERRED"


class MassStatus(str, Enum):
    """Component sizing status."""
    SIZED = "SIZED"
    ESTIMATED = "ESTIMATED"
    CATALOG_MATCHED = "CATALOG_MATCHED"
    UNRESOLVED = "UNRESOLVED"


class ConvergenceStatus(str, Enum):
    """Multidisciplinary sizing loop convergence state."""
    PRE_CONVERGENCE = "PRE_CONVERGENCE"
    ITERATING = "ITERATING"
    CONVERGED = "CONVERGED"
    NOT_CONVERGED = "NOT_CONVERGED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    INVALID_CONVERGENCE_ARCHITECTURE = "INVALID_CONVERGENCE_ARCHITECTURE"


@dataclass(slots=True)
class AuthoritativeComponentMass:
    """
    Detailed atomic record for a single airframe component in the mass ledger.
    """
    name: str
    category: MassCategory
    value_kg: float
    source: str
    classification: MassClassification
    position_x_m: float  # Distance from Fuselage Nose datum (positive aft)
    position_y_m: float = 0.0  # Lateral offset from centerline (positive right)
    position_z_m: float = 0.0  # Vertical offset from centerline (positive up)
    status: MassStatus = MassStatus.SIZED
    notes: str = ""

    @property
    def moment_kg_m(self) -> float:
        """Longitudinal mass moment about the reference datum in kg*m."""
        return self.value_kg * self.position_x_m

    @property
    def mass_kg(self) -> float:
        """Alias for value_kg in kilograms."""
        return self.value_kg

    @property
    def x_arm_m(self) -> float:
        """Alias for position_x_m in meters."""
        return self.position_x_m

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category.value,
            "value_kg": round(self.value_kg, 4),
            "source": self.source,
            "classification": self.classification.value,
            "position_x_m": round(self.position_x_m, 4),
            "position_y_m": round(self.position_y_m, 4),
            "position_z_m": round(self.position_z_m, 4),
            "moment_kg_m": round(self.moment_kg_m, 4),
            "status": self.status.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class MassCategoryBreakdown:
    """
    Aggregated category rollups and airframe mass fractions.
    """
    structure_mass_kg: float
    propulsion_mass_kg: float
    electrical_mass_kg: float
    avionics_mass_kg: float
    payload_mass_kg: float
    other_mass_kg: float
    battery_mass_kg: float
    empty_mass_kg: float
    total_mass_kg: float

    # Mass fractions
    structure_fraction: float = 0.0
    propulsion_fraction: float = 0.0
    electrical_fraction: float = 0.0
    avionics_fraction: float = 0.0
    payload_fraction: float = 0.0
    battery_fraction: float = 0.0
    empty_mass_fraction: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "structure_mass_kg": round(self.structure_mass_kg, 4),
            "propulsion_mass_kg": round(self.propulsion_mass_kg, 4),
            "electrical_mass_kg": round(self.electrical_mass_kg, 4),
            "avionics_mass_kg": round(self.avionics_mass_kg, 4),
            "payload_mass_kg": round(self.payload_mass_kg, 4),
            "other_mass_kg": round(self.other_mass_kg, 4),
            "battery_mass_kg": round(self.battery_mass_kg, 4),
            "empty_mass_kg": round(self.empty_mass_kg, 4),
            "total_mass_kg": round(self.total_mass_kg, 4),
            "fractions": {
                "structure": round(self.structure_fraction, 4),
                "propulsion": round(self.propulsion_fraction, 4),
                "electrical": round(self.electrical_fraction, 4),
                "avionics": round(self.avionics_fraction, 4),
                "payload": round(self.payload_fraction, 4),
                "battery": round(self.battery_fraction, 4),
                "empty": round(self.empty_mass_fraction, 4),
            }
        }


@dataclass(slots=True)
class MassLedger:
    """
    Complete consolidated mass ledger enforcing conservation and integrity.
    """
    components: List[AuthoritativeComponentMass] = field(default_factory=list)
    category_breakdown: MassCategoryBreakdown = field(
        default_factory=lambda: MassCategoryBreakdown(0, 0, 0, 0, 0, 0, 0, 0, 0)
    )
    total_mass_kg: float = 0.0
    mass_conservation_residual: float = 0.0
    is_conserved: bool = True
    has_duplicates: bool = False
    has_negative_mass: bool = False
    unresolved_components: List[str] = field(default_factory=list)

    @property
    def conservation_residual_kg(self) -> float:
        """Alias for mass_conservation_residual."""
        return self.mass_conservation_residual

    @property
    def has_duplicate_components(self) -> bool:
        """Alias for has_duplicates."""
        return self.has_duplicates

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_mass_kg": round(self.total_mass_kg, 4),
            "mass_conservation_residual": round(self.mass_conservation_residual, 6),
            "is_conserved": self.is_conserved,
            "has_duplicates": self.has_duplicates,
            "has_negative_mass": self.has_negative_mass,
            "unresolved_components": list(self.unresolved_components),
            "category_breakdown": self.category_breakdown.to_dict(),
            "component_count": len(self.components),
            "components": [c.to_dict() for c in self.components],
        }


@dataclass(slots=True)
class CenterOfGravityResult:
    """
    Longitudinal and spatial center-of-gravity evaluation with datum consistency.
    """
    reference_datum: str = "FUSELAGE_NOSE"
    total_mass_kg: float = 0.0
    total_moment_kg_m: float = 0.0
    x_cg_m: float = 0.0
    y_cg_m: float = 0.0
    z_cg_m: float = 0.0
    mean_aerodynamic_chord_m: Optional[float] = None
    x_lemac_m: Optional[float] = None
    x_cg_pct_mac: Optional[float] = None
    forward_cg_limit_m: Optional[float] = None
    aft_cg_limit_m: Optional[float] = None
    forward_margin_m: Optional[float] = None
    aft_margin_m: Optional[float] = None
    cg_status: str = "DEFERRED_TO_PHASE_6"

    @property
    def datum_reference(self) -> str:
        """Alias for reference_datum."""
        return self.reference_datum

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reference_datum": self.reference_datum,
            "total_mass_kg": round(self.total_mass_kg, 4),
            "total_moment_kg_m": round(self.total_moment_kg_m, 4),
            "x_cg_m": round(self.x_cg_m, 4),
            "y_cg_m": round(self.y_cg_m, 4),
            "z_cg_m": round(self.z_cg_m, 4),
            "mean_aerodynamic_chord_m": round(self.mean_aerodynamic_chord_m, 4) if self.mean_aerodynamic_chord_m else None,
            "x_lemac_m": round(self.x_lemac_m, 4) if self.x_lemac_m else None,
            "x_cg_pct_mac": round(self.x_cg_pct_mac, 2) if self.x_cg_pct_mac is not None else None,
            "forward_cg_limit_m": round(self.forward_cg_limit_m, 4) if self.forward_cg_limit_m else None,
            "aft_cg_limit_m": round(self.aft_cg_limit_m, 4) if self.aft_cg_limit_m else None,
            "forward_margin_m": round(self.forward_margin_m, 4) if self.forward_margin_m is not None else None,
            "aft_margin_m": round(self.aft_margin_m, 4) if self.aft_margin_m is not None else None,
            "cg_status": self.cg_status,
        }


@dataclass(slots=True)
class ConvergenceStepRecord:
    """
    Diagnostic history entry for a single iteration step of the mass loop.
    """
    iteration: int
    assumed_mass_kg: float
    calculated_mass_kg: float
    residual_kg: float
    relaxation_alpha: float
    next_mass_kg: float
    battery_mass_kg: float
    structural_mass_kg: float
    propulsion_mass_kg: float
    converged: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "iteration": self.iteration,
            "assumed_mass_kg": round(self.assumed_mass_kg, 4),
            "calculated_mass_kg": round(self.calculated_mass_kg, 4),
            "residual_kg": round(self.residual_kg, 4),
            "relaxation_alpha": round(self.relaxation_alpha, 3),
            "next_mass_kg": round(self.next_mass_kg, 4),
            "battery_mass_kg": round(self.battery_mass_kg, 4),
            "structural_mass_kg": round(self.structural_mass_kg, 4),
            "propulsion_mass_kg": round(self.propulsion_mass_kg, 4),
            "converged": self.converged,
        }


@dataclass(slots=True)
class AuthoritativeMassResult:
    """
    Consolidated outcome of Phase 5 authoritative mass and MTOW convergence.
    """
    sizing_mass_kg: float
    converged_mtow_kg: float
    empty_weight_kg: float
    payload_weight_kg: float
    battery_weight_kg: float
    mass_ledger: MassLedger
    center_of_gravity: CenterOfGravityResult
    convergence_status: ConvergenceStatus
    is_converged_mtow: bool
    convergence_iterations: int
    convergence_residual_kg: float
    convergence_tolerance_kg: float
    convergence_history: List[ConvergenceStepRecord] = field(default_factory=list)
    relaxation_alpha: float = 0.70
    status: str = "IMPLEMENTED"
    engineering_assumptions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sizing_mass_kg": round(self.sizing_mass_kg, 4),
            "converged_mtow_kg": round(self.converged_mtow_kg, 4),
            "empty_weight_kg": round(self.empty_weight_kg, 4),
            "payload_weight_kg": round(self.payload_weight_kg, 4),
            "battery_weight_kg": round(self.battery_weight_kg, 4),
            "convergence_status": self.convergence_status.value,
            "is_converged_mtow": self.is_converged_mtow,
            "convergence_iterations": self.convergence_iterations,
            "convergence_residual_kg": round(self.convergence_residual_kg, 4),
            "convergence_tolerance_kg": round(self.convergence_tolerance_kg, 4),
            "relaxation_alpha": round(self.relaxation_alpha, 3),
            "status": self.status,
            "mass_ledger": self.mass_ledger.to_dict(),
            "center_of_gravity": self.center_of_gravity.to_dict(),
            "convergence_history": [s.to_dict() for s in self.convergence_history],
            "engineering_assumptions": list(self.engineering_assumptions),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "metadata": dict(self.metadata),
        }


class AuthoritativeMassModel:
    """
    Calculation engine for VTOL Phase 5 mass synthesis, CG, and convergence.
    """

    # Engineering constants and geometric reference defaults (Datum: FUSELAGE_NOSE)
    DEFAULT_REFERENCE_DATUM = "FUSELAGE_NOSE"
    DEFAULT_MASS_TOLERANCE_KG = 0.015  # 15 grams convergence threshold
    DEFAULT_RELAXATION_ALPHA = 0.70    # Under-relaxation factor
    DEFAULT_MAX_ITERATIONS = 20

    # Typical component longitudinal centroids (fractions of fuselage length or absolute meters)
    DEFAULT_AVIONICS_X_M = 0.25
    DEFAULT_PAYLOAD_X_M = 0.30
    DEFAULT_BATTERY_X_M = 0.45
    DEFAULT_WING_X_M = 0.50
    DEFAULT_FUSELAGE_CG_X_M = 0.45
    DEFAULT_LIFT_FRONT_MOTOR_X_M = 0.25
    DEFAULT_LIFT_REAR_MOTOR_X_M = 0.75
    DEFAULT_CRUISE_MOTOR_X_M = 0.90  # Pusher default
    DEFAULT_TAIL_X_M = 1.20
    DEFAULT_LANDING_GEAR_X_M = 0.45

    @classmethod
    def synthesize_component_masses(
        cls,
        sizing_mass_kg: float,
        lift_motor_count: int = 4,
        wing_result: Optional[Any] = None,
        fuselage_result: Optional[Any] = None,
        tail_result: Optional[Any] = None,
        lift_system_result: Optional[Any] = None,
        forward_propulsion_result: Optional[Any] = None,
        electrical_result: Optional[Any] = None,
        avionics_result: Optional[Any] = None,
        payload_result: Optional[Any] = None,
        mission_result: Optional[Any] = None,
        fixed_wing_subsystems: Optional[Any] = None,
        overrides: Optional[Dict[str, float]] = None,
    ) -> MassLedger:
        """
        Compiles the complete 6-category mass ledger from authoritative upstream results.
        Every component is explicitly attributed with mass, CG, source, and provenance.
        """
        overrides = overrides or {}
        components: List[AuthoritativeComponentMass] = []
        unresolved: List[str] = []

        # -------------------------------------------------------------
        # 1. STRUCTURE MASSES
        # -------------------------------------------------------------
        # A. Wing Structure
        wing_mass = None
        wing_source = "UNRESOLVED"
        wing_class = MassClassification.UNRESOLVED

        if "wing_structure_mass_kg" in overrides:
            wing_mass = overrides["wing_structure_mass_kg"]
            wing_source = "USER_OVERRIDE"
            wing_class = MassClassification.CONFIGURABLE_ASSUMPTION
        elif wing_result is not None and hasattr(wing_result, "wing_structure"):
            wing_mass = getattr(wing_result.wing_structure, "estimated_wing_weight_kg", None)
            if wing_mass is not None and wing_mass > 0:
                wing_source = "WING_SUBSYSTEM_ANALYSIS"
                wing_class = MassClassification.DERIVED
        elif fixed_wing_subsystems is not None and hasattr(fixed_wing_subsystems, "wing"):
            fw_wing = fixed_wing_subsystems.wing
            wing_mass = getattr(fw_wing, "mass_kg", None) or getattr(fw_wing, "estimated_weight_kg", None)
            if wing_mass is not None and wing_mass > 0:
                wing_source = "FIXED_WING_ADAPTER"
                wing_class = MassClassification.DERIVED

        if wing_mass is None or wing_mass <= 0:
            # Fallback assumption (typical 12-15% of sizing mass for composite UAV wing)
            wing_mass = max(0.40, sizing_mass_kg * 0.13)
            wing_source = "ESTIMATED_WING_FRACTION_ASSUMPTION"
            wing_class = MassClassification.CONFIGURABLE_ASSUMPTION

        # Longitudinal location of wing from fuselage or geometry
        wing_x = cls.DEFAULT_WING_X_M
        if wing_result is not None and hasattr(wing_result, "wing_geometry"):
            root_c = getattr(wing_result.wing_geometry, "root_chord_m", 0.30)
            wing_x = cls.DEFAULT_WING_X_M + 0.25 * root_c

        components.append(AuthoritativeComponentMass(
            name="Wing Structure",
            category=MassCategory.STRUCTURE,
            value_kg=wing_mass,
            source=wing_source,
            classification=wing_class,
            position_x_m=wing_x,
            position_y_m=0.0,
            position_z_m=0.10,
            status=MassStatus.SIZED if wing_class == MassClassification.DERIVED else MassStatus.ESTIMATED,
            notes="Main wing panels, spar, ribs, and skins."
        ))

        # B. Fuselage Structure
        fuse_mass = None
        fuse_source = "UNRESOLVED"
        fuse_class = MassClassification.UNRESOLVED

        if "fuselage_structure_mass_kg" in overrides:
            fuse_mass = overrides["fuselage_structure_mass_kg"]
            fuse_source = "USER_OVERRIDE"
            fuse_class = MassClassification.CONFIGURABLE_ASSUMPTION
        elif fuselage_result is not None and hasattr(fuselage_result, "fuselage_structure"):
            fuse_mass = getattr(fuselage_result.fuselage_structure, "estimated_fuselage_weight_kg", None)
            if fuse_mass is not None and fuse_mass > 0:
                fuse_source = "FUSELAGE_SUBSYSTEM_ANALYSIS"
                fuse_class = MassClassification.DERIVED
        elif fixed_wing_subsystems is not None and hasattr(fixed_wing_subsystems, "fuselage"):
            fw_fuse = fixed_wing_subsystems.fuselage
            fuse_mass = getattr(fw_fuse, "mass_kg", None)
            if fuse_mass is not None and fuse_mass > 0:
                fuse_source = "FIXED_WING_ADAPTER"
                fuse_class = MassClassification.DERIVED

        if fuse_mass is None or fuse_mass <= 0:
            fuse_mass = max(0.45, sizing_mass_kg * 0.12)
            fuse_source = "ESTIMATED_FUSELAGE_FRACTION_ASSUMPTION"
            fuse_class = MassClassification.CONFIGURABLE_ASSUMPTION

        fuse_x = cls.DEFAULT_FUSELAGE_CG_X_M
        if fuselage_result is not None and hasattr(fuselage_result, "internal_layout"):
            fuse_x = getattr(fuselage_result.internal_layout, "center_of_gravity_x_m", cls.DEFAULT_FUSELAGE_CG_X_M)

        components.append(AuthoritativeComponentMass(
            name="Fuselage Structure",
            category=MassCategory.STRUCTURE,
            value_kg=fuse_mass,
            source=fuse_source,
            classification=fuse_class,
            position_x_m=fuse_x,
            position_y_m=0.0,
            position_z_m=0.0,
            status=MassStatus.SIZED if fuse_class == MassClassification.DERIVED else MassStatus.ESTIMATED,
            notes="Composite fuselage monocoque shell and internal formers."
        ))

        # C. Tail Structure
        tail_mass = None
        tail_source = "UNRESOLVED"
        tail_class = MassClassification.UNRESOLVED

        if "tail_structure_mass_kg" in overrides:
            tail_mass = overrides["tail_structure_mass_kg"]
            tail_source = "USER_OVERRIDE"
            tail_class = MassClassification.CONFIGURABLE_ASSUMPTION
        elif tail_result is not None and hasattr(tail_result, "tail_structure"):
            tail_mass = getattr(tail_result.tail_structure, "estimated_tail_weight_kg", None)
            if tail_mass is not None and tail_mass > 0:
                tail_source = "TAIL_SUBSYSTEM_ANALYSIS"
                tail_class = MassClassification.DERIVED
        elif fixed_wing_subsystems is not None and hasattr(fixed_wing_subsystems, "tail"):
            fw_tail = fixed_wing_subsystems.tail
            tail_mass = getattr(fw_tail, "mass_kg", None)
            if tail_mass is not None and tail_mass > 0:
                tail_source = "FIXED_WING_ADAPTER"
                tail_class = MassClassification.DERIVED

        if tail_mass is None or tail_mass <= 0:
            tail_mass = max(0.25, sizing_mass_kg * 0.045)
            tail_source = "ESTIMATED_TAIL_FRACTION_ASSUMPTION"
            tail_class = MassClassification.CONFIGURABLE_ASSUMPTION

        components.append(AuthoritativeComponentMass(
            name="Tail Structure",
            category=MassCategory.STRUCTURE,
            value_kg=tail_mass,
            source=tail_source,
            classification=tail_class,
            position_x_m=cls.DEFAULT_TAIL_X_M,
            position_y_m=0.0,
            position_z_m=0.15,
            status=MassStatus.SIZED if tail_class == MassClassification.DERIVED else MassStatus.ESTIMATED,
            notes="Inverted V-tail or empennage surfaces, stabilizers, and control horns."
        ))

        # D. Booms & Mounts (VTOL specific twin booms)
        booms_mass = None
        booms_source = "UNRESOLVED"
        booms_class = MassClassification.UNRESOLVED

        if "boom_structure_mass_kg" in overrides:
            booms_mass = overrides["boom_structure_mass_kg"]
            booms_source = "USER_OVERRIDE"
            booms_class = MassClassification.CONFIGURABLE_ASSUMPTION
        else:
            # Sized from boom diameter & length: 2 booms * carbon tube density (~180 g/m) * length (~1.0 m)
            # Typically 0.35 - 0.60 kg total for twin boom VTOL
            booms_mass = 0.45
            booms_source = "TWIN_BOOM_STRUCTURAL_SIZING"
            booms_class = MassClassification.CONFIGURABLE_ASSUMPTION

        components.append(AuthoritativeComponentMass(
            name="Twin Booms Structure",
            category=MassCategory.STRUCTURE,
            value_kg=booms_mass,
            source=booms_source,
            classification=booms_class,
            position_x_m=0.60,
            position_y_m=0.0,
            position_z_m=0.05,
            status=MassStatus.SIZED,
            notes="Twin carbon fiber motor boom tubes and fuselage joint sleeves."
        ))

        # E. Landing Gear
        gear_mass = overrides.get("landing_gear_mass_kg", 0.28)
        components.append(AuthoritativeComponentMass(
            name="Landing Gear Assembly",
            category=MassCategory.STRUCTURE,
            value_kg=gear_mass,
            source="LANDING_GEAR_SPECIFICATION" if "landing_gear_mass_kg" in overrides else "LANDING_GEAR_ASSUMPTION",
            classification=MassClassification.CONFIGURABLE_ASSUMPTION,
            position_x_m=cls.DEFAULT_LANDING_GEAR_X_M,
            position_y_m=0.0,
            position_z_m=-0.20,
            status=MassStatus.ESTIMATED,
            notes="Carbon fiber landing skids and shock-absorption brackets."
        ))

        # F. Structural Hardware & Fasteners
        hardware_mass = overrides.get("structural_hardware_mass_kg", 0.18)
        components.append(AuthoritativeComponentMass(
            name="Structural Hardware & Fasteners",
            category=MassCategory.STRUCTURE,
            value_kg=hardware_mass,
            source="HARDWARE_WEIGHT_ASSUMPTION",
            classification=MassClassification.CONFIGURABLE_ASSUMPTION,
            position_x_m=0.50,
            position_y_m=0.0,
            position_z_m=0.0,
            status=MassStatus.ESTIMATED,
            notes="Bonding adhesive, joiner pins, bolts, and wing attachment inserts."
        ))

        # -------------------------------------------------------------
        # 2. PROPULSION MASSES
        # -------------------------------------------------------------
        # A. Lift Motors
        unit_lift_motor_mass = None
        lift_motor_src = "UNRESOLVED"
        lift_motor_cls = MassClassification.UNRESOLVED

        if lift_system_result is not None and hasattr(lift_system_result, "lift_motor_selection"):
            sel = lift_system_result.lift_motor_selection
            if isinstance(sel, dict) and "mass_kg" in sel:
                unit_lift_motor_mass = float(sel["mass_kg"])
                lift_motor_src = f"LIFT_MOTOR_CATALOG_{sel.get('name', 'SELECTION')}"
                lift_motor_cls = MassClassification.DERIVED

        if unit_lift_motor_mass is None or unit_lift_motor_mass <= 0:
            unit_lift_motor_mass = 0.14  # Default ~140g brushless motor (e.g. T-Motor MN5008)
            lift_motor_src = "DEFAULT_LIFT_MOTOR_ESTIMATE"
            lift_motor_cls = MassClassification.CONFIGURABLE_ASSUMPTION

        total_lift_motors_mass = unit_lift_motor_mass * lift_motor_count
        lift_motors_cg_x = 0.5 * (cls.DEFAULT_LIFT_FRONT_MOTOR_X_M + cls.DEFAULT_LIFT_REAR_MOTOR_X_M)

        components.append(AuthoritativeComponentMass(
            name=f"Lift Motors ({lift_motor_count}x)",
            category=MassCategory.PROPULSION,
            value_kg=total_lift_motors_mass,
            source=lift_motor_src,
            classification=lift_motor_cls,
            position_x_m=lift_motors_cg_x,
            position_y_m=0.0,
            position_z_m=0.08,
            status=MassStatus.SIZED,
            notes=f"{lift_motor_count} brushless outrunner vertical lift motors ({unit_lift_motor_mass * 1000.0:.0f}g each)."
        ))

        # B. Lift ESCs
        unit_lift_esc_mass = 0.042  # ~42g 40A-60A OPTO ESC
        total_lift_escs_mass = unit_lift_esc_mass * lift_motor_count
        components.append(AuthoritativeComponentMass(
            name=f"Lift ESCs ({lift_motor_count}x)",
            category=MassCategory.PROPULSION,
            value_kg=total_lift_escs_mass,
            source="LIFT_ESC_SPECIFICATION",
            classification=MassClassification.CONFIGURABLE_ASSUMPTION,
            position_x_m=lift_motors_cg_x,
            position_y_m=0.0,
            position_z_m=0.05,
            status=MassStatus.ESTIMATED,
            notes=f"{lift_motor_count} vertical motor electronic speed controllers with heat sinks."
        ))

        # C. Lift Propellers / Rotors
        unit_lift_prop_mass = 0.028  # ~28g carbon propeller
        if lift_system_result is not None and hasattr(lift_system_result, "lift_propeller_selection"):
            psel = lift_system_result.lift_propeller_selection
            if isinstance(psel, dict) and "mass_kg" in psel:
                unit_lift_prop_mass = float(psel["mass_kg"])

        total_lift_props_mass = unit_lift_prop_mass * lift_motor_count
        components.append(AuthoritativeComponentMass(
            name=f"Lift Propellers ({lift_motor_count}x)",
            category=MassCategory.PROPULSION,
            value_kg=total_lift_props_mass,
            source="LIFT_PROPELLER_SELECTION",
            classification=MassClassification.DERIVED if lift_system_result else MassClassification.CONFIGURABLE_ASSUMPTION,
            position_x_m=lift_motors_cg_x,
            position_y_m=0.0,
            position_z_m=0.12,
            status=MassStatus.SIZED,
            notes=f"{lift_motor_count} carbon fiber lift rotors."
        ))

        # D. Cruise Propulsion (Forward Motor, ESC, Propeller)
        cruise_motor_mass = 0.15  # ~150g brushless motor
        cruise_src = "DEFAULT_CRUISE_MOTOR_ESTIMATE"
        cruise_cls = MassClassification.CONFIGURABLE_ASSUMPTION

        if forward_propulsion_result is not None and hasattr(forward_propulsion_result, "motor_selection"):
            c_sel = forward_propulsion_result.motor_selection
            if isinstance(c_sel, dict) and "mass_kg" in c_sel:
                cruise_motor_mass = float(c_sel["mass_kg"])
                cruise_src = f"CRUISE_MOTOR_CATALOG_{c_sel.get('name', 'SELECTION')}"
                cruise_cls = MassClassification.DERIVED

        components.append(AuthoritativeComponentMass(
            name="Forward Cruise Motor",
            category=MassCategory.PROPULSION,
            value_kg=cruise_motor_mass,
            source=cruise_src,
            classification=cruise_cls,
            position_x_m=cls.DEFAULT_CRUISE_MOTOR_X_M,
            position_y_m=0.0,
            position_z_m=0.02,
            status=MassStatus.SIZED if cruise_cls == MassClassification.DERIVED else MassStatus.ESTIMATED,
            notes="Brushless pusher motor for forward flight cruise and loiter."
        ))

        cruise_esc_mass = 0.045
        components.append(AuthoritativeComponentMass(
            name="Forward Cruise ESC",
            category=MassCategory.PROPULSION,
            value_kg=cruise_esc_mass,
            source="CRUISE_ESC_SPECIFICATION",
            classification=MassClassification.CONFIGURABLE_ASSUMPTION,
            position_x_m=cls.DEFAULT_CRUISE_MOTOR_X_M - 0.10,
            position_y_m=0.0,
            position_z_m=0.0,
            status=MassStatus.ESTIMATED,
            notes="Forward propulsion electronic speed controller."
        ))

        cruise_prop_mass = 0.035
        components.append(AuthoritativeComponentMass(
            name="Forward Cruise Propeller",
            category=MassCategory.PROPULSION,
            value_kg=cruise_prop_mass,
            source="CRUISE_PROPELLER_SPECIFICATION",
            classification=MassClassification.CONFIGURABLE_ASSUMPTION,
            position_x_m=cls.DEFAULT_CRUISE_MOTOR_X_M + 0.05,
            position_y_m=0.0,
            position_z_m=0.02,
            status=MassStatus.ESTIMATED,
            notes="Forward flight pusher propeller."
        ))

        # E. Propulsion Installation Hardware
        prop_hardware_mass = 0.12
        components.append(AuthoritativeComponentMass(
            name="Propulsion Mounts & Hardware",
            category=MassCategory.PROPULSION,
            value_kg=prop_hardware_mass,
            source="PROPULSION_HARDWARE_ASSUMPTION",
            classification=MassClassification.CONFIGURABLE_ASSUMPTION,
            position_x_m=lift_motors_cg_x,
            position_y_m=0.0,
            position_z_m=0.05,
            status=MassStatus.ESTIMATED,
            notes="Motor mount plates, CNC aluminum clamps, and prop adapters."
        ))

        # -------------------------------------------------------------
        # 3. ELECTRICAL MASSES (Phase 4 Direct Battery Coupling)
        # -------------------------------------------------------------
        batt_mass = None
        batt_source = "UNRESOLVED"
        batt_class = MassClassification.UNRESOLVED

        if "battery_mass_kg" in overrides:
            batt_mass = overrides["battery_mass_kg"]
            batt_source = "USER_OVERRIDE"
            batt_class = MassClassification.CONFIGURABLE_ASSUMPTION
        elif electrical_result is not None and hasattr(electrical_result, "authoritative_energy_result"):
            auth_e = electrical_result.authoritative_energy_result
            if auth_e is not None and hasattr(auth_e, "battery_sizing"):
                b_sz = auth_e.battery_sizing
                if b_sz is not None and getattr(b_sz, "estimated_battery_mass_kg", None) is not None:
                    batt_mass = float(b_sz.estimated_battery_mass_kg)
                    batt_source = "PHASE_4_AUTHORITATIVE_ENERGY_COUPLING"
                    batt_class = MassClassification.DERIVED

        if batt_mass is None:
            if electrical_result is not None and hasattr(electrical_result, "battery_pack"):
                b_pk = electrical_result.battery_pack
                if b_pk is not None and getattr(b_pk, "mass_kg", None) is not None:
                    batt_mass = float(b_pk.mass_kg)
                    batt_source = "ELECTRICAL_BATTERY_PACK_RESULT"
                    batt_class = MassClassification.DERIVED

        if batt_mass is None or batt_mass <= 0:
            unresolved.append("battery_mass_kg")
            batt_mass = max(0.50, sizing_mass_kg * 0.28)
            batt_source = "FALLBACK_BATTERY_FRACTION_ASSUMPTION"
            batt_class = MassClassification.UNRESOLVED

        components.append(AuthoritativeComponentMass(
            name="Primary Flight Battery Pack",
            category=MassCategory.ELECTRICAL,
            value_kg=batt_mass,
            source=batt_source,
            classification=batt_class,
            position_x_m=cls.DEFAULT_BATTERY_X_M,
            position_y_m=0.0,
            position_z_m=-0.04,
            status=MassStatus.SIZED if batt_class == MassClassification.DERIVED else MassStatus.UNRESOLVED,
            notes="Coupled directly from Phase 4 required nominal energy & specific energy."
        ))

        wiring_mass = overrides.get("wiring_harness_mass_kg", 0.22)
        components.append(AuthoritativeComponentMass(
            name="Electrical Wiring Harness",
            category=MassCategory.ELECTRICAL,
            value_kg=wiring_mass,
            source="WIRING_HARNESS_ASSUMPTION",
            classification=MassClassification.CONFIGURABLE_ASSUMPTION,
            position_x_m=0.45,
            position_y_m=0.0,
            position_z_m=0.0,
            status=MassStatus.ESTIMATED,
            notes="Main high-current battery leads, motor wire extensions, and signal harnesses."
        ))

        pdb_mass = overrides.get("power_distribution_mass_kg", 0.085)
        components.append(AuthoritativeComponentMass(
            name="Power Distribution Board & Regulators",
            category=MassCategory.ELECTRICAL,
            value_kg=pdb_mass,
            source="PDB_BEC_ASSUMPTION",
            classification=MassClassification.CONFIGURABLE_ASSUMPTION,
            position_x_m=0.40,
            position_y_m=0.0,
            position_z_m=0.0,
            status=MassStatus.ESTIMATED,
            notes="Dual-bus power distribution board, current sensors, and 5V/12V BEC units."
        ))

        # -------------------------------------------------------------
        # 4. AVIONICS MASSES
        # -------------------------------------------------------------
        fc_mass = 0.095
        fc_source = "DEFAULT_AUTOPILOT_WEIGHT"
        fc_class = MassClassification.CONFIGURABLE_ASSUMPTION

        if avionics_result is not None and hasattr(avionics_result, "flight_controller"):
            fc = avionics_result.flight_controller
            if fc is not None and getattr(fc, "weight_kg", None) is not None:
                fc_mass = float(fc.weight_kg)
                fc_source = f"AVIONICS_FC_{getattr(fc, 'name', 'SELECTION')}"
                fc_class = MassClassification.DERIVED

        components.append(AuthoritativeComponentMass(
            name="Primary Flight Controller",
            category=MassCategory.AVIONICS,
            value_kg=fc_mass,
            source=fc_source,
            classification=fc_class,
            position_x_m=cls.DEFAULT_AVIONICS_X_M,
            position_y_m=0.0,
            position_z_m=0.02,
            status=MassStatus.SIZED,
            notes="Triple-redundant autopilot computer with internal IMUs."
        ))

        nav_mass = 0.065
        comm_mass = 0.050
        comp_mass = 0.0
        sensor_mass = 0.035

        if avionics_result is not None:
            if hasattr(avionics_result, "navigation_system") and getattr(avionics_result.navigation_system, "weight_kg", None):
                nav_mass = float(avionics_result.navigation_system.weight_kg)
            if hasattr(avionics_result, "communication_system") and getattr(avionics_result.communication_system, "weight_kg", None):
                comm_mass = float(avionics_result.communication_system.weight_kg)
            if hasattr(avionics_result, "sensor_suite") and getattr(avionics_result.sensor_suite, "weight_kg", None):
                sensor_mass = float(avionics_result.sensor_suite.weight_kg)
            if hasattr(avionics_result, "companion_computer") and getattr(avionics_result.companion_computer, "weight_kg", None):
                comp_mass = float(avionics_result.companion_computer.weight_kg)

        components.append(AuthoritativeComponentMass(
            name="GNSS & Navigation Unit",
            category=MassCategory.AVIONICS,
            value_kg=nav_mass,
            source="AVIONICS_NAV_SUBSYSTEM" if avionics_result else "AVIONICS_NAV_ASSUMPTION",
            classification=MassClassification.DERIVED if avionics_result else MassClassification.CONFIGURABLE_ASSUMPTION,
            position_x_m=0.35,
            position_y_m=0.0,
            position_z_m=0.12,
            status=MassStatus.SIZED,
            notes="High-precision GNSS receiver and external compass mast."
        ))

        components.append(AuthoritativeComponentMass(
            name="Telemetry & RC Communication",
            category=MassCategory.AVIONICS,
            value_kg=comm_mass,
            source="AVIONICS_COMM_SUBSYSTEM" if avionics_result else "AVIONICS_COMM_ASSUMPTION",
            classification=MassClassification.DERIVED if avionics_result else MassClassification.CONFIGURABLE_ASSUMPTION,
            position_x_m=0.48,
            position_y_m=0.0,
            position_z_m=0.05,
            status=MassStatus.SIZED,
            notes="Air-to-ground telemetry modem and control link receivers."
        ))

        components.append(AuthoritativeComponentMass(
            name="Pitot-Static & Air Data Sensors",
            category=MassCategory.AVIONICS,
            value_kg=sensor_mass,
            source="AVIONICS_SENSORS_SUBSYSTEM" if avionics_result else "AVIONICS_SENSORS_ASSUMPTION",
            classification=MassClassification.DERIVED if avionics_result else MassClassification.CONFIGURABLE_ASSUMPTION,
            position_x_m=0.10,
            position_y_m=0.20,
            position_z_m=0.0,
            status=MassStatus.SIZED,
            notes="Differential pressure pitot tube and barometric sensors."
        ))

        if comp_mass > 0:
            components.append(AuthoritativeComponentMass(
                name="Companion Computer",
                category=MassCategory.AVIONICS,
                value_kg=comp_mass,
                source="AVIONICS_COMPANION_SUBSYSTEM",
                classification=MassClassification.DERIVED,
                position_x_m=cls.DEFAULT_AVIONICS_X_M + 0.05,
                position_y_m=0.0,
                position_z_m=0.02,
                status=MassStatus.SIZED,
                notes="Onboard SBC for mission autonomy and sensor processing."
            ))

        # -------------------------------------------------------------
        # 5. PAYLOAD MASSES (Included Exactly Once)
        # -------------------------------------------------------------
        pld_mass = None
        pld_source = "UNRESOLVED"
        pld_class = MassClassification.UNRESOLVED

        if "payload_mass_kg" in overrides:
            pld_mass = overrides["payload_mass_kg"]
            pld_source = "USER_OVERRIDE"
            pld_class = MassClassification.PROJECT_REQUIREMENT
        elif payload_result is not None and hasattr(payload_result, "payload_selection"):
            psel = payload_result.payload_selection
            if psel is not None and getattr(psel, "weight_kg", None) is not None and float(psel.weight_kg) > 0:
                pld_mass = float(psel.weight_kg)
                pld_source = f"PAYLOAD_SUBSYSTEM_{getattr(psel, 'name', 'SELECTION')}"
                pld_class = MassClassification.DERIVED
        elif mission_result is not None and hasattr(mission_result, "mission_profile"):
            mp = mission_result.mission_profile
            if mp is not None and getattr(mp, "payload_kg", None) is not None and float(mp.payload_kg) > 0:
                pld_mass = float(mp.payload_kg)
                pld_source = "MISSION_REQUIREMENT_SPECIFICATION"
                pld_class = MassClassification.PROJECT_REQUIREMENT

        if pld_mass is None or pld_mass <= 0:
            pld_mass = 2.0
            pld_source = "DEFAULT_PAYLOAD_ASSUMPTION"
            pld_class = MassClassification.CONFIGURABLE_ASSUMPTION

        components.append(AuthoritativeComponentMass(
            name="Primary Mission Payload",
            category=MassCategory.PAYLOAD,
            value_kg=pld_mass,
            source=pld_source,
            classification=pld_class,
            position_x_m=cls.DEFAULT_PAYLOAD_X_M,
            position_y_m=0.0,
            position_z_m=-0.08,
            status=MassStatus.SIZED,
            notes="Mission sensor (camera, gimbal, or environmental sensor package)."
        ))

        pld_mount_mass = 0.15
        if payload_result is not None and hasattr(payload_result, "payload_mount"):
            pm = payload_result.payload_mount
            if pm is not None and getattr(pm, "weight_kg", None) is not None:
                pld_mount_mass = float(pm.weight_kg)

        components.append(AuthoritativeComponentMass(
            name="Payload Mount & Dampener",
            category=MassCategory.PAYLOAD,
            value_kg=pld_mount_mass,
            source="PAYLOAD_MOUNT_SUBSYSTEM" if payload_result else "PAYLOAD_MOUNT_ASSUMPTION",
            classification=MassClassification.DERIVED if payload_result else MassClassification.CONFIGURABLE_ASSUMPTION,
            position_x_m=cls.DEFAULT_PAYLOAD_X_M - 0.02,
            position_y_m=0.0,
            position_z_m=-0.04,
            status=MassStatus.SIZED,
            notes="Vibration isolation tray, quick-release plate, and wiring harness."
        ))

        # -------------------------------------------------------------
        # 6. OTHER MASSES
        # -------------------------------------------------------------
        if "other_equipment_mass_kg" in overrides and overrides["other_equipment_mass_kg"] > 0:
            components.append(AuthoritativeComponentMass(
                name="Auxiliary Equipment",
                category=MassCategory.OTHER,
                value_kg=overrides["other_equipment_mass_kg"],
                source="USER_EQUIPMENT_SPECIFICATION",
                classification=MassClassification.PROJECT_REQUIREMENT,
                position_x_m=0.50,
                position_y_m=0.0,
                position_z_m=0.0,
                status=MassStatus.SIZED,
                notes="Custom mission hardware or ballast."
            ))

        # -------------------------------------------------------------
        # 7. AGGREGATION & MASS CONSERVATION VERIFICATION
        # -------------------------------------------------------------
        total_mass = sum(c.value_kg for c in components)
        structure_sum = sum(c.value_kg for c in components if c.category == MassCategory.STRUCTURE)
        propulsion_sum = sum(c.value_kg for c in components if c.category == MassCategory.PROPULSION)
        electrical_sum = sum(c.value_kg for c in components if c.category == MassCategory.ELECTRICAL)
        avionics_sum = sum(c.value_kg for c in components if c.category == MassCategory.AVIONICS)
        payload_sum = sum(c.value_kg for c in components if c.category == MassCategory.PAYLOAD)
        other_sum = sum(c.value_kg for c in components if c.category == MassCategory.OTHER)

        battery_comp_mass = batt_mass
        empty_weight = total_mass - battery_comp_mass - payload_sum

        return cls.build_ledger(components, unresolved)

    @classmethod
    def build_ledger(
        cls,
        components: List[AuthoritativeComponentMass],
        unresolved: Optional[List[str]] = None,
    ) -> MassLedger:
        """
        Validates component masses, checks duplicates and non-positive masses,
        and constructs an authoritative MassLedger with category breakdown.
        """
        unresolved = unresolved or []
        names = [c.name for c in components]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate component detected in mass ledger")

        if any(c.value_kg <= 0 for c in components):
            raise ValueError("Non-positive component mass detected in mass ledger")

        total_mass = sum(c.value_kg for c in components)
        structure_sum = sum(c.value_kg for c in components if c.category == MassCategory.STRUCTURE)
        propulsion_sum = sum(c.value_kg for c in components if c.category == MassCategory.PROPULSION)
        electrical_sum = sum(c.value_kg for c in components if c.category == MassCategory.ELECTRICAL)
        avionics_sum = sum(c.value_kg for c in components if c.category == MassCategory.AVIONICS)
        payload_sum = sum(c.value_kg for c in components if c.category == MassCategory.PAYLOAD)
        other_sum = sum(c.value_kg for c in components if c.category == MassCategory.OTHER)

        battery_comps = [c.value_kg for c in components if "battery" in c.name.lower()]
        battery_comp_mass = sum(battery_comps)
        empty_weight = total_mass - battery_comp_mass - payload_sum

        category_sum = structure_sum + propulsion_sum + electrical_sum + avionics_sum + payload_sum + other_sum
        conservation_residual = abs(total_mass - category_sum)
        is_conserved = conservation_residual < 1e-6

        breakdown = MassCategoryBreakdown(
            structure_mass_kg=structure_sum,
            propulsion_mass_kg=propulsion_sum,
            electrical_mass_kg=electrical_sum,
            avionics_mass_kg=avionics_sum,
            payload_mass_kg=payload_sum,
            other_mass_kg=other_sum,
            battery_mass_kg=battery_comp_mass,
            empty_mass_kg=empty_weight,
            total_mass_kg=total_mass,
            structure_fraction=(structure_sum / total_mass) if total_mass > 0 else 0.0,
            propulsion_fraction=(propulsion_sum / total_mass) if total_mass > 0 else 0.0,
            electrical_fraction=(electrical_sum / total_mass) if total_mass > 0 else 0.0,
            avionics_fraction=(avionics_sum / total_mass) if total_mass > 0 else 0.0,
            payload_fraction=(payload_sum / total_mass) if total_mass > 0 else 0.0,
            battery_fraction=(battery_comp_mass / total_mass) if total_mass > 0 else 0.0,
            empty_mass_fraction=(empty_weight / total_mass) if total_mass > 0 else 0.0,
        )

        return MassLedger(
            components=components,
            category_breakdown=breakdown,
            total_mass_kg=total_mass,
            mass_conservation_residual=conservation_residual,
            is_conserved=is_conserved,
            has_duplicates=False,
            has_negative_mass=False,
            unresolved_components=unresolved,
        )

    @classmethod
    def calculate_center_of_gravity(
        cls,
        mass_ledger: MassLedger,
        mac_m: Optional[float] = None,
        x_lemac_m: Optional[float] = None,
        forward_cg_limit_m: Optional[float] = None,
        aft_cg_limit_m: Optional[float] = None,
    ) -> CenterOfGravityResult:
        """
        Calculates authoritative longitudinal center-of-gravity (CG)
        and static balance relative to the consistent reference datum (FUSELAGE_NOSE).
        """
        total_mass = mass_ledger.total_mass_kg
        if total_mass <= 0:
            return CenterOfGravityResult(
                reference_datum=cls.DEFAULT_REFERENCE_DATUM,
                total_mass_kg=0.0,
                total_moment_kg_m=0.0,
                x_cg_m=0.0,
                cg_status="INVALID_ZERO_MASS",
            )

        total_moment_x = sum(c.moment_kg_m for c in mass_ledger.components)
        total_moment_y = sum(c.value_kg * c.position_y_m for c in mass_ledger.components)
        total_moment_z = sum(c.value_kg * c.position_z_m for c in mass_ledger.components)

        x_cg = total_moment_x / total_mass
        y_cg = total_moment_y / total_mass
        z_cg = total_moment_z / total_mass

        x_cg_pct_mac = None
        if mac_m is not None and mac_m > 0 and x_lemac_m is not None:
            x_cg_pct_mac = ((x_cg - x_lemac_m) / mac_m) * 100.0

        fwd_margin = None
        aft_margin = None
        cg_status = "DEFERRED_TO_PHASE_6"

        if forward_cg_limit_m is not None and aft_cg_limit_m is not None:
            fwd_margin = x_cg - forward_cg_limit_m
            aft_margin = aft_cg_limit_m - x_cg
            if fwd_margin < 0:
                cg_status = "EXCEEDED_FORWARD_LIMIT"
            elif aft_margin < 0:
                cg_status = "EXCEEDED_AFT_LIMIT"
            else:
                cg_status = "WITHIN_LIMITS"

        return CenterOfGravityResult(
            reference_datum=cls.DEFAULT_REFERENCE_DATUM,
            total_mass_kg=total_mass,
            total_moment_kg_m=total_moment_x,
            x_cg_m=x_cg,
            y_cg_m=y_cg,
            z_cg_m=z_cg,
            mean_aerodynamic_chord_m=mac_m,
            x_lemac_m=x_lemac_m,
            x_cg_pct_mac=x_cg_pct_mac,
            forward_cg_limit_m=forward_cg_limit_m,
            aft_cg_limit_m=aft_cg_limit_m,
            forward_margin_m=fwd_margin,
            aft_margin_m=aft_margin,
            cg_status=cg_status,
        )

    @classmethod
    def evaluate_convergence_step(
        cls,
        iteration: int,
        assumed_mass_kg: float,
        calculated_mass_kg: float,
        tolerance_kg: float = DEFAULT_MASS_TOLERANCE_KG,
        relaxation_alpha: float = DEFAULT_RELAXATION_ALPHA,
        battery_mass_kg: float = 0.0,
        structural_mass_kg: float = 0.0,
        propulsion_mass_kg: float = 0.0,
    ) -> Tuple[ConvergenceStepRecord, float, bool]:
        """
        Evaluates convergence residual between assumed iteration mass and
        independently synthesized calculated mass.
        Applies under-relaxation to compute next mass guess.
        """
        residual_kg = abs(calculated_mass_kg - assumed_mass_kg)
        converged = residual_kg <= tolerance_kg

        next_mass_kg = relaxation_alpha * calculated_mass_kg + (1.0 - relaxation_alpha) * assumed_mass_kg

        record = ConvergenceStepRecord(
            iteration=iteration,
            assumed_mass_kg=assumed_mass_kg,
            calculated_mass_kg=calculated_mass_kg,
            residual_kg=residual_kg,
            relaxation_alpha=relaxation_alpha,
            next_mass_kg=next_mass_kg,
            battery_mass_kg=battery_mass_kg,
            structural_mass_kg=structural_mass_kg,
            propulsion_mass_kg=propulsion_mass_kg,
            converged=converged,
        )

        return record, next_mass_kg, converged
