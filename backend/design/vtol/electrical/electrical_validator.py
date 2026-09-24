"""
VTOL Electrical Validator Subsystem

Purpose:
    Defines the `ElectricalValidator` class checking capacities, current ratings,
    voltage matching, and safety reserves.
"""

from typing import List
from backend.design.vtol.electrical.electrical_requirements import ElectricalRequirements
from backend.design.vtol.electrical.electrical_result import ElectricalResult


class ElectricalValidationError(ValueError):
    """
    Exception raised when VTOL electrical sizing violates capacity or voltage safety limits.
    """

    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class ElectricalValidator:
    """
    Validates sized battery packs and protection systems.
    """

    def validate(self, requirements: ElectricalRequirements, result: ElectricalResult) -> None:
        """
        Validates the electrical sizing results.

        Args:
            requirements (ElectricalRequirements): Inputs.
            result (ElectricalResult): Outputs.

        Raises:
            ElectricalValidationError: If rules are violated.
        """
        errors: List[str] = []

        if requirements is None:
            raise ElectricalValidationError(["Requirements object is null."])

        pack = result.battery_pack
        analysis = result.electrical_analysis
        power_budget = result.power_budget

        # 1. Battery capacity check
        # Sized reserve factor
        min_reserve = requirements.metadata.get(
            "min_reserve_energy_fraction",
            requirements.preferred_reserve_fraction if requirements.preferred_reserve_fraction is not None else 0.20
        )
        required_energy_reserve = analysis.mission_energy_wh * (1.0 + min_reserve)
        if pack.energy_wh < required_energy_reserve:
            errors.append(
                f"Battery capacity failure: sized battery energy ({pack.energy_wh:.1f} Wh) "
                f"is less than required energy budget with reserve limit ({required_energy_reserve:.1f} Wh)."
            )

        # 2. Peak current capability check
        # Peak current is drawn during hover or transition stages
        hover_current = result.metadata.get("hover_current_draw_a", 0.0)
        peak_current = hover_current
        if result.electrical_envelope and result.electrical_envelope.peak_current_a:
            peak_current = max(hover_current, result.electrical_envelope.peak_current_a)

        if peak_current > pack.peak_current_limit_a:
            errors.append(
                f"Discharge capability violation: peak current ({peak_current:.1f} A) "
                f"exceeds maximum battery pack peak current limit ({pack.peak_current_limit_a:.1f} A)."
            )

        # 3. Voltage compatibility check
        # check nominal voltages align with ESC limits
        if not (11.1 <= pack.nominal_voltage_v <= 60.0):
            errors.append(
                f"Voltage compatibility error: pack voltage ({pack.nominal_voltage_v:.1f} V) "
                f"is outside acceptable ESC limits (11.1V to 60.0V)."
            )

        # 4. Phase 4 Authoritative Energy Ledger Verification
        if result.mission_energy_ledger is not None:
            ledger = result.mission_energy_ledger
            # Check summation conservation
            sum_energy = sum(s.energy_wh for s in ledger.segments)
            if abs(sum_energy - ledger.total_mission_energy_wh) > 1e-4:
                errors.append(
                    f"Energy conservation violation: segment sum ({sum_energy:.4f} Wh) "
                    f"does not match total mission energy ({ledger.total_mission_energy_wh:.4f} Wh)."
                )

            # Check segment physical invariants
            seen_phases = set()
            for s in ledger.segments:
                if s.phase in seen_phases:
                    errors.append(f"Duplicate mission phase detected in ledger: {s.phase}")
                seen_phases.add(s.phase)

                if s.duration_s < 0.0:
                    errors.append(f"Invalid negative duration in segment {s.phase}: {s.duration_s}s")
                if s.average_power_w < 0.0 or s.peak_power_w < 0.0:
                    errors.append(f"Invalid negative power in segment {s.phase}")
                if s.energy_wh < 0.0:
                    errors.append(f"Invalid negative energy in segment {s.phase}: {s.energy_wh} Wh")

            if ledger.has_double_counting:
                errors.append("Energy double-counting detected in mission ledger.")

        if errors:
            raise ElectricalValidationError(errors)
