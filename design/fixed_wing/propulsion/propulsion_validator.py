"""
Fixed-Wing Propulsion Validator Subsystem

Purpose:
    Defines the `PropulsionValidator` class to validate power, thrust, and configuration layouts.

Role in Architecture:
    `PropulsionValidator` checks thrust-to-weight minimums, climb rates, throttle settings,
    and component engine compatibility bounds.
"""

from typing import List
from backend.design.fixed_wing.propulsion.propulsion_requirements import PropulsionRequirements, PropulsionType
from backend.design.fixed_wing.propulsion.propulsion_constraints import PropulsionConstraints
from backend.design.fixed_wing.propulsion.thrust_analysis import ThrustAnalysis
from backend.design.fixed_wing.propulsion.power_analysis import PowerAnalysis
from backend.design.fixed_wing.propulsion.efficiency_analysis import EfficiencyAnalysis
from backend.design.fixed_wing.propulsion.cruise_analysis import CruiseAnalysis
from backend.design.fixed_wing.propulsion.climb_analysis import ClimbAnalysis
from backend.design.fixed_wing.propulsion.takeoff_analysis import TakeoffAnalysis


class PropulsionValidationError(ValueError):
    """Exception raised when sized propulsion parameters fail limits."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class PropulsionValidator:
    """
    Validator enforcing aerodynamic and electrical compatibility constraints.
    """

    def validate(
        self,
        requirements: PropulsionRequirements,
        constraints: PropulsionConstraints,
        prop_type: PropulsionType,
        t_anal: ThrustAnalysis,
        p_anal: PowerAnalysis,
        c_anal: CruiseAnalysis,
        cl_anal: ClimbAnalysis,
        to_anal: TakeoffAnalysis,
    ) -> List[str]:
        """
        Validates the sized propulsion subsystem.

        Args:
            requirements (PropulsionRequirements): Sizing requirements context.
            constraints (PropulsionConstraints): Sizing bounds.
            prop_type (PropulsionType): Power source type (Electric, ICE).
            t_anal (ThrustAnalysis): Thrust forces.
            p_anal (PowerAnalysis): Power draws.
            c_anal (CruiseAnalysis): Cruise speeds.
            cl_anal (ClimbAnalysis): Climb rates.
            to_anal (TakeoffAnalysis): Takeoff run values.

        Returns:
            List[str]: A list of non-fatal warnings (compromises).

        Raises:
            PropulsionValidationError: If critical constraints are violated.
        """
        errors: List[str] = []
        warnings: List[str] = []

        mtow = requirements.mission_result.constraints.maximum_takeoff_weight_kg
        tail = requirements.tail_result.tail_configuration

        # 1. Takeoff Thrust check
        if t_anal.thrust_to_weight_ratio < constraints.min_thrust_to_weight:
            errors.append(
                f"Takeoff thrust-to-weight ratio ({t_anal.thrust_to_weight_ratio:.2f}) is below "
                f"minimum required constraint limit ({constraints.min_thrust_to_weight:.2f})."
            )

        # 2. Power margin vs climb load
        if p_anal.maximum_power_w < p_anal.required_climb_power_w:
            errors.append(
                f"Selected motor maximum power ({p_anal.maximum_power_w:.1f} W) is insufficient to sustain the "
                f"power required during steady rate of climb ({p_anal.required_climb_power_w:.1f} W)."
            )

        # 3. Climb performance check
        if cl_anal.rate_of_climb_m_s < 0.5:
            errors.append(
                f"Sized rate of climb ({cl_anal.rate_of_climb_m_s:.2f} m/s) is insufficient (minimum safe limit: 0.5 m/s)."
            )

        # 4. Cruise performance: throttle check
        if c_anal.throttle_setting_pct > 72.0:
            warnings.append(
                f"High cruise throttle setting ({c_anal.throttle_setting_pct:.1f}%). "
                "Leaves insufficient motor margin for headwind penetrations. Recommend selecting a larger motor/Kv."
            )
        elif c_anal.throttle_setting_pct < 28.0:
            warnings.append(
                f"Low cruise throttle setting ({c_anal.throttle_setting_pct:.1f}%). "
                "Propulsion system is oversized, causing excess weight and low cruise electrical efficiency."
            )

        # 5. Component compatibility: ICE on Tailless
        if prop_type == PropulsionType.ICE:
            if tail in ("Tailless", "Flying Wing"):
                errors.append(
                    "Internal Combustion Engines (ICE) are incompatible with Tailless/Flying Wing configurations "
                    "due to severe pitch trimming and fuselage fuel tank balancing limitations."
                )

        if errors:
            raise PropulsionValidationError(errors)

        return warnings
