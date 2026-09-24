from typing import List
from .hover_result import HoverResult
from .hover_constraints import HoverConstraints

class HoverValidator:
    """
    Validates sized margins against hover limits.
    """
    @staticmethod
    def validate(result: HoverResult, constraints: HoverConstraints) -> List[str]:
        warnings = []

        # Check thrust margin
        t_w = result.hover_thrust.thrust_margin_ratio
        if t_w < constraints.min_hover_thrust_margin_ratio:
            warnings.append(
                f"Sized hover thrust-to-weight ratio ({t_w:.2f}) "
                f"falls below safe operational threshold ({constraints.min_hover_thrust_margin_ratio:.2f})"
            )

        # Check power budget
        p_total = result.hover_power.total_hover_power_watts
        if p_total > constraints.max_hover_power_watts:
            warnings.append(
                f"Total hover power consumption ({p_total:.1f} W) "
                f"exceeds physical limits ({constraints.max_hover_power_watts:.1f} W)"
            )

        # Check control headroom
        headroom = result.hover_control.control_headroom_pct
        if headroom < constraints.min_control_authority_headroom_pct:
            warnings.append(
                f"Hover control authority headroom ({headroom:.1f}%) "
                f"is below safety margin ({constraints.min_control_authority_headroom_pct:.1f}%)"
            )

        # Check wind limit
        wind = result.wind_analysis.crosswind_limit_kts
        if wind < constraints.max_wind_velocity_kts:
            warnings.append(
                f"Crosswind hover tolerance ({wind:.1f} kts) "
                f"falls below minimum requirement ({constraints.max_wind_velocity_kts:.1f} kts)"
            )

        return warnings
