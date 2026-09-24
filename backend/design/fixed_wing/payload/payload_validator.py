"""
Fixed-Wing Payload Validator Subsystem

Purpose:
    Defines the `PayloadValidator` class to validate payload fit, power, and CG limits.

Role in Architecture:
    `PayloadValidator` checks if payload weight exceeds structural capacity,
    if power draws exceed limits, and if CG shifts remain within aerodynamic stability bounds.
"""

from typing import List
from backend.design.fixed_wing.payload.payload_requirements import PayloadRequirements
from backend.design.fixed_wing.payload.payload_constraints import PayloadConstraints
from backend.design.fixed_wing.payload.payload_profile import PayloadProfile
from backend.design.fixed_wing.payload.payload_analysis import PayloadAnalysis


class PayloadValidationError(ValueError):
    """Exception raised when sized payload integration parameters fail safety limits."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class PayloadValidator:
    """
    Validator enforcing volumetric, weight, and electrical load limits on mission payloads.
    """

    def validate(
        self,
        requirements: PayloadRequirements,
        constraints: PayloadConstraints,
        profile: PayloadProfile,
        selected_payloads_weight: float,
        selected_payloads_vol: float,
        compartment_vol: float,
        analysis: PayloadAnalysis,
    ) -> List[str]:
        """
        Validates the sized payload subsystem.

        Args:
            requirements (PayloadRequirements): Sizing requirements context.
            constraints (PayloadConstraints): Sizing bounds.
            profile (PayloadProfile): Safety tolerances.
            selected_payloads_weight (float): Cumulative weight of payloads (kg).
            selected_payloads_vol (float): Cumulative volume of payloads (m^3).
            compartment_vol (float): Available fuselage compartment volume (m^3).
            analysis (PayloadAnalysis): Calculated payload metrics.

        Returns:
            List[str]: A list of non-fatal warnings (compromises).

        Raises:
            PayloadValidationError: If critical constraints are violated.
        """
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Structural compatibility: weight check
        if selected_payloads_weight > constraints.max_payload_weight_kg:
            errors.append(
                f"Sized payload weight ({selected_payloads_weight:.2f} kg) exceeds "
                f"maximum structural payload weight constraint ({constraints.max_payload_weight_kg:.2f} kg)."
            )

        # 2. Payload fit: volumetric check
        if selected_payloads_vol > compartment_vol * 0.90:
            errors.append(
                f"Sized payload volume ({selected_payloads_vol*1e6:.1f} cm3) exceeds the physical "
                f"90% fuselage compartment volume capacity ({compartment_vol*0.90*1e6:.1f} cm3)."
            )

        # 3. Power availability check
        if analysis.power_consumption_w > constraints.max_payload_power_w:
            errors.append(
                f"Sized payload continuous power draw ({analysis.power_consumption_w:.1f} W) "
                f"exceeds the maximum payload power constraint limit ({constraints.max_payload_power_w:.1f} W)."
            )

        # 4. CG limits check
        if abs(analysis.cg_shift_offset_m) > profile.max_allowable_cg_offset_m:
            errors.append(
                f"Payload integration causes Center of Gravity displacement ({analysis.cg_shift_offset_m*1000:.1f} mm) "
                f"exceeding aerodynamic safety tolerance ({profile.max_allowable_cg_offset_m*1000:.1f} mm)."
            )

        # 5. Cooling adequacy check
        if analysis.power_consumption_w >= 12.0:
            warnings.append(
                f"High thermal power output ({analysis.power_consumption_w:.1f} W). "
                "Passive cooling may be inadequate. Recommend installing cooling scoops or vents."
            )

        # 6. Communication compatibility
        if analysis.required_bandwidth_mbps > constraints.max_bandwidth_mbps:
            warnings.append(
                f"Payload bandwidth requirements ({analysis.required_bandwidth_mbps:.1f} Mbps) "
                f"exceed standard data link limits ({constraints.max_bandwidth_mbps:.1f} Mbps)."
            )

        if errors:
            raise PayloadValidationError(errors)

        return warnings
