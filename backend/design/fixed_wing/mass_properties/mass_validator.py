"""
Fixed-Wing Mass Validator Subsystem

Purpose:
    Defines the `MassValidator` class to validate takeoff weight, CG limits, and stability margins.

Role in Architecture:
    `MassValidator` checks weight budgets, checks if stability margins are positive and safe,
    and flags out-of-envelope CG travels.
"""

from typing import List
from backend.design.fixed_wing.mass_properties.mass_requirements import MassRequirements
from backend.design.fixed_wing.mass_properties.mass_constraints import MassConstraints
from backend.design.fixed_wing.mass_properties.mass_profile import MassProfile
from backend.design.fixed_wing.mass_properties.loading_conditions import LoadingCondition


class MassValidationError(ValueError):
    """Exception raised when sized mass properties fail limits."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class MassValidator:
    """
    Validator enforcing aerodynamic and structural constraints.
    """

    def validate(
        self,
        requirements: MassRequirements,
        constraints: MassConstraints,
        profile: MassProfile,
        total_mass_kg: float,
        cg_x: float,
        static_margin: float,
        loading_conditions: List[LoadingCondition],
    ) -> List[str]:
        """
        Validates the sized mass subsystem.

        Args:
            requirements (MassRequirements): Sizing requirements context.
            constraints (MassConstraints): Sizing bounds.
            profile (MassProfile): Safety tolerances.
            total_mass_kg (float): Sized total MTOW (kg).
            cg_x (float): Sized longitudinal center of gravity.
            static_margin (float): Sized stability margin.
            loading_conditions (List[LoadingCondition]): loading envelopes.

        Returns:
            List[str]: A list of non-fatal warnings (compromises).

        Raises:
            MassValidationError: If critical constraints are violated.
        """
        errors: List[str] = []
        warnings: List[str] = []

        # 1. MTOW check
        if total_mass_kg > constraints.max_takeoff_weight_kg:
            errors.append(
                f"Calculated takeoff weight ({total_mass_kg:.2f} kg) exceeds "
                f"maximum takeoff weight limit constraint ({constraints.max_takeoff_weight_kg:.2f} kg)."
            )

        # 2. CG location checks
        fuselage_len = requirements.fuselage_result.fuselage_geometry.length_m
        if cg_x < 0.0 or cg_x > fuselage_len:
            errors.append(
                f"Sized Center of Gravity location ({cg_x:.2f} m) is geometrically impossible "
                f"(located outside the fuselage length of {fuselage_len:.2f} m)."
            )

        # 3. Static Margin checks
        if static_margin < constraints.min_static_margin:
            errors.append(
                f"Longitudinal static stability margin ({static_margin*100:.1f}%) is below the "
                f"minimum safe stability reserve ({constraints.min_static_margin*100:.1f}%). "
                "Risk of loss of pitch control."
            )
        elif static_margin > constraints.max_static_margin:
            warnings.append(
                f"High static stability margin ({static_margin*100:.1f}%). "
                "The aircraft will be excessively nose-heavy, causing high trim drag and elevator control forces."
            )

        # 4. Loading Envelope: Worst-case CG travel checks
        # Find maximum and minimum CG coordinates across loading states
        cgs = [lc.cg_x_m for lc in loading_conditions]
        if cgs:
            cg_travel_m = max(cgs) - min(cgs)
            mac = requirements.wing_result.wing_geometry.mean_aerodynamic_chord_m
            travel_pct_mac = (cg_travel_m / mac) * 100.0

            if travel_pct_mac > 10.0:
                warnings.append(
                    f"Significant loading CG travel ({travel_pct_mac:.1f}% MAC). "
                    "Ensure the autopilot pitch trims can accommodate this travel range during flight."
                )

        if errors:
            raise MassValidationError(errors)

        return warnings
