from typing import List
from .mass_result import MassResult
from .mass_constraints import MassConstraints

class MassValidator:
    """
    Validates design weights and balance boundaries.
    """
    @staticmethod
    def validate(result: MassResult, constraints: MassConstraints) -> List[str]:
        warnings = []

        # Check MTOW limits
        budget = result.weight_budget
        if (budget.empty_weight_kg + budget.payload_mass_kg) > constraints.max_takeoff_weight_kg:
            warnings.append(
                f"Sized takeoff weight ({budget.empty_weight_kg + budget.payload_mass_kg:.2f} kg) "
                f"exceeds constraints MTOW ({constraints.max_takeoff_weight_kg:.2f} kg)"
            )

        # Check CG range X limits
        cg_pct = result.center_of_gravity.x_pct_mac / 100.0 if result.center_of_gravity.x_pct_mac > 1.0 else result.center_of_gravity.x_pct_mac
        if cg_pct < constraints.allowed_cg_range_x_pct_mac_min or cg_pct > constraints.allowed_cg_range_x_pct_mac_max:
            warnings.append(
                f"Calculated CG position ({cg_pct * 100.0:.1f}% MAC) "
                f"is outside stability envelope ({constraints.allowed_cg_range_x_pct_mac_min * 100.0:.1f}% - "
                f"{constraints.allowed_cg_range_x_pct_mac_max * 100.0:.1f}% MAC)"
            )

        # Check static margin
        if result.mass_analysis.cruise_static_margin < constraints.min_static_margin:
            warnings.append(
                f"Cruise static margin ({result.mass_analysis.cruise_static_margin * 100.0:.1f}%) "
                f"is below safety threshold ({constraints.min_static_margin * 100.0:.1f}%)"
            )

        # Check lateral offset
        if abs(result.center_of_gravity.y_m) > constraints.allowed_cg_range_y_m:
            warnings.append(
                f"Lateral CG offset ({result.center_of_gravity.y_m:.3f} m) "
                f"exceeds limit (+/- {constraints.allowed_cg_range_y_m:.3f} m)"
            )

        # Phase 5 Authoritative Mass Integrity Checks
        if result.authoritative_mass_result is not None:
            auth = result.authoritative_mass_result
            ledger = auth.mass_ledger

            if ledger.total_mass_kg <= 0:
                warnings.append("Authoritative total mass must be strictly positive.")

            if ledger.has_negative_mass:
                warnings.append("Authoritative mass ledger contains negative component mass values.")

            if ledger.has_duplicates:
                warnings.append("Authoritative mass ledger contains duplicate component names.")

            if not ledger.is_conserved:
                warnings.append(
                    f"Mass conservation violated: category sum residual {ledger.mass_conservation_residual:.6e} kg exceeds tolerance."
                )

        return warnings
