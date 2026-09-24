from typing import List
from .cad_result import CADResult
from .cad_constraints import CADConstraints

class CADValidator:
    """
    Validates CAD collision clearances and coordinate trees.
    """
    @staticmethod
    def validate(result: CADResult, constraints: CADConstraints) -> List[str]:
        warnings = []

        # Check interferences
        if result.interference_report.total_interference_volume_mm3 > constraints.max_interference_volume_mm3 or not result.interference_report.is_interference_free:
            warnings.append(
                f"Sized CAD assembly has active interferences ({result.interference_report.total_interference_volume_mm3:.1f} mm3) "
                f"violating design constraints."
            )

        # Check clearances
        if result.clearance_report.actual_clearance_mm < constraints.min_rotor_clearance_mm or not result.clearance_report.is_clearance_safe:
            warnings.append(
                f"Sized rotor clearance ({result.clearance_report.actual_clearance_mm:.1f} mm) "
                f"is below safety requirement ({constraints.min_rotor_clearance_mm:.1f} mm)"
            )

        return warnings
