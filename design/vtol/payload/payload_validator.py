from typing import List
from .payload_result import PayloadResult
from .payload_constraints import PayloadConstraints

class PayloadValidator:
    """
    Asserts payload design boundaries and flags violations.
    """
    @staticmethod
    def validate(result: PayloadResult, constraints: PayloadConstraints) -> List[str]:
        warnings = []
        
        if result.payload_selection.weight_kg > constraints.max_payload_mass_kg:
            warnings.append(
                f"Payload mass ({result.payload_selection.weight_kg:.2f} kg) "
                f"exceeds maximum allowed limit ({constraints.max_payload_mass_kg:.2f} kg)"
            )
            
        total_power = result.payload_power.continuous_power_watts
        if total_power > constraints.max_payload_power_watts:
            warnings.append(
                f"Continuous power consumption ({total_power:.1f} W) "
                f"exceeds maximum budget ({constraints.max_payload_power_watts:.1f} W)"
            )

        if abs(result.payload_cg.cg_shift_pct_mac) > constraints.max_cg_shift_pct_mac:
            warnings.append(
                f"Center-of-gravity shift ({result.payload_cg.cg_shift_pct_mac:.2f}% MAC) "
                f"exceeds safe limits (+/- {constraints.max_cg_shift_pct_mac:.1f}% MAC)"
            )

        if not result.payload_bay.fit_status:
            warnings.append("Payload physical dimensions exceed payload bay envelope.")

        for req_int in constraints.required_interfaces:
            if req_int not in result.payload_interfaces.data_connections:
                warnings.append(f"Required data interface '{req_int}' is not supported by payload connections.")

        return warnings
