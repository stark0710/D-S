"""
Fixed-Wing Flight Validator Subsystem

Purpose:
    Defines the `FlightValidator` class to validate range, endurance, takeoff, and landing rolls.

Role in Architecture:
    `FlightValidator` checks speeds, checks if takeoff runs fit within runway limits,
    and flags low battery range reserves.
"""

from typing import List
from backend.design.fixed_wing.flight_performance.flight_requirements import FlightRequirements
from backend.design.fixed_wing.flight_performance.flight_constraints import FlightConstraints
from backend.design.fixed_wing.flight_performance.flight_profile import FlightProfile
from backend.design.fixed_wing.flight_performance.performance_analysis import PerformanceAnalysis
from backend.design.fixed_wing.flight_performance.takeoff_analysis import TakeoffAnalysis
from backend.design.fixed_wing.flight_performance.landing_analysis import LandingAnalysis
from backend.design.fixed_wing.flight_performance.climb_analysis import ClimbAnalysis
from backend.design.fixed_wing.flight_performance.range_analysis import RangeAnalysis
from backend.design.fixed_wing.flight_performance.endurance_analysis import EnduranceAnalysis
from backend.design.fixed_wing.flight_performance.stall_analysis import StallAnalysis
from backend.design.fixed_wing.flight_performance.stability_analysis import StabilityAnalysis


class FlightValidationError(ValueError):
    """Exception raised when sized flight performance parameters fail safety thresholds."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class FlightValidator:
    """
    Validator enforcing aerodynamic and flight performance boundaries.
    """

    def validate(
        self,
        requirements: FlightRequirements,
        constraints: FlightConstraints,
        profile: FlightProfile,
        perf: PerformanceAnalysis,
        to_anal: TakeoffAnalysis,
        land_anal: LandingAnalysis,
        cl_anal: ClimbAnalysis,
        r_anal: RangeAnalysis,
        ed_anal: EnduranceAnalysis,
        stab_anal: StabilityAnalysis,
        stall_margin_pct: float,
        stall: StallAnalysis | None = None,
    ) -> List[str]:
        """
        Validates the sized flight performance.

        Args:
            requirements (FlightRequirements): Sizing requirements context.
            constraints (FlightConstraints): Sizing bounds.
            profile (FlightProfile): reference safety parameters.
            perf (PerformanceAnalysis): speed envelopes.
            to_anal (TakeoffAnalysis): ground run takeoff lengths.
            land_anal (LandingAnalysis): braking landing lengths.
            cl_anal (ClimbAnalysis): rate of climbs.
            r_anal (RangeAnalysis): travel ranges.
            ed_anal (EnduranceAnalysis): flight endurances.
            stab_anal (StabilityAnalysis): pitch stability.
            stall_margin_pct (float): safety speed factor above stall.

        Returns:
            List[str]: A list of non-fatal warnings (compromises).

        Raises:
            FlightValidationError: If critical constraints are violated.
        """
        errors: List[str] = []
        warnings: List[str] = []

        m_profile = requirements.mission_result.mission_profile

        # 1. Takeoff roll check
        if to_anal.takeoff_distance_m > constraints.max_takeoff_distance_m:
            errors.append(
                f"Sized takeoff ground roll ({to_anal.takeoff_distance_m:.1f} m) exceeds "
                f"maximum runway constraint limit ({constraints.max_takeoff_distance_m:.1f} m)."
            )

        # 2. Landing roll check
        if land_anal.landing_distance_m > constraints.max_landing_distance_m:
            errors.append(
                f"Sized landing braking roll ({land_anal.landing_distance_m:.1f} m) exceeds "
                f"maximum runway constraint limit ({constraints.max_landing_distance_m:.1f} m)."
            )

        # 3. Climb rate check
        if cl_anal.rate_of_climb_m_s < constraints.min_rate_of_climb_m_s:
            errors.append(
                f"Rate of climb ({cl_anal.rate_of_climb_m_s:.2f} m/s) is below the "
                f"minimum required rate of climb constraint ({constraints.min_rate_of_climb_m_s:.2f} m/s)."
            )

        # 4. Range feasibility check
        if r_anal.maximum_range_km < constraints.min_range_km:
            errors.append(
                f"Sized maximum flight range ({r_anal.maximum_range_km:.1f} km) is below "
                f"mission range requirement ({constraints.min_range_km:.1f} km)."
            )

        # 5. Endurance feasibility check
        if ed_anal.maximum_endurance_min < constraints.min_endurance_min:
            errors.append(
                f"Sized maximum flight endurance ({ed_anal.maximum_endurance_min:.1f} min) is below "
                f"mission endurance requirement ({constraints.min_endurance_min:.1f} min)."
            )

        # 6. Cruise stall margin check
        stall_speed_clean = stall.stall_speed_clean_kmh if stall else (perf.minimum_controllable_speed_kmh / 1.15)
        min_safe_cruise = stall_speed_clean * (1.0 + stall_margin_pct / 100.0)
        if perf.cruise_speed_kmh < min_safe_cruise:
            errors.append(
                f"Cruise speed ({perf.cruise_speed_kmh:.1f} kmh) is below the "
                f"minimum safe cruise speed boundary ({min_safe_cruise:.1f} kmh, "
                f"representing a {stall_margin_pct:.1f}% safety margin above clean stall)."
            )

        # 7. Low battery margin warning
        if r_anal.cruise_range_km < m_profile.mission_range_km * 1.15:
            warnings.append(
                f"Narrow range reserve ({r_anal.cruise_range_km:.1f} km vs mission target {m_profile.mission_range_km:.1f} km). "
                "Recommend increasing battery cell size or lowering payload payload weight."
            )

        if errors:
            raise FlightValidationError(errors)

        return warnings
