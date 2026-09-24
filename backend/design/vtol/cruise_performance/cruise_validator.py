from typing import List
from .cruise_result import CruiseResult
from .cruise_constraints import CruiseConstraints

class CruiseValidator:
    """
    Validates cruise range, endurance, and climbs.
    """
    @staticmethod
    def validate(result: CruiseResult, constraints: CruiseConstraints) -> List[str]:
        warnings = []

        # Check range
        rng = result.cruise_analysis.range_km
        if rng < constraints.min_range_km:
            warnings.append(
                f"Sized cruise range ({rng:.1f} km) "
                f"is below minimum requirement ({constraints.min_range_km:.1f} km)"
            )

        # Check endurance
        end = result.cruise_analysis.endurance_min
        if end < constraints.min_endurance_min:
            warnings.append(
                f"Sized cruise endurance ({end:.1f} min) "
                f"falls below safety margin ({constraints.min_endurance_min:.1f} min)"
            )

        # Check climb rate
        roc = result.cruise_analysis.max_rate_of_climb_m_s
        if roc < constraints.min_climb_rate_m_s:
            warnings.append(
                f"Maximum rate of climb ({roc:.2f} m/s) "
                f"is below threshold ({constraints.min_climb_rate_m_s:.2f} m/s)"
            )

        # Check power margin
        p_cruise = result.power_analysis.cruise_power_watts
        if p_cruise > constraints.max_cruise_power_watts:
            warnings.append(
                f"Cruise power required ({p_cruise:.1f} W) "
                f"exceeds system limit ({constraints.max_cruise_power_watts:.1f} W)"
            )

        return warnings
