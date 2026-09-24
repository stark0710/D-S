from typing import List
from .manufacturing_result import ManufacturingResult
from .manufacturing_constraints import ManufacturingConstraints

class ManufacturingValidator:
    """
    Validates manufacturing costs, lead times, and materials.
    """
    @staticmethod
    def validate(result: ManufacturingResult, constraints: ManufacturingConstraints) -> List[str]:
        warnings = []

        # Check total cost
        cost = result.production_cost.total_unit_cost_usd
        if cost > constraints.max_production_cost_usd:
            warnings.append(
                f"Estimated production cost (${cost:.2f}) "
                f"exceeds manufacturing budget constraints (${constraints.max_production_cost_usd:.2f})"
            )

        # Check assembly time
        time_hrs = result.assembly_instructions.estimated_assembly_time_hours
        if time_hrs > constraints.max_assembly_time_hours:
            warnings.append(
                f"Sized build assembly time ({time_hrs:.1f} hrs) "
                f"exceeds allocated build schedule hours ({constraints.max_assembly_time_hours:.1f} hrs)"
            )

        # Check material utilization
        util = result.manufacturability_assessment.material_utilization_pct
        if util < constraints.min_material_utilization_pct:
            warnings.append(
                f"Sized material utilization ({util:.1f}%) "
                f"is below target threshold ({constraints.min_material_utilization_pct:.1f}%)"
            )

        return warnings
