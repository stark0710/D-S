from typing import List
from .avionics_result import AvionicsResult
from .avionics_constraints import AvionicsConstraints

class AvionicsValidator:
    """
    Validates design results against physical, resource, and network boundaries.
    """
    @staticmethod
    def validate(result: AvionicsResult, constraints: AvionicsConstraints) -> List[str]:
        warnings = []
        
        if result.analysis.cpu_utilization_pct > constraints.max_cpu_utilization_pct:
            warnings.append(
                f"CPU utilization ({result.analysis.cpu_utilization_pct:.1f}%) exceeds maximum limit "
                f"({constraints.max_cpu_utilization_pct:.1f}%)"
            )
            
        if result.analysis.memory_utilization_pct > constraints.max_memory_utilization_pct:
            warnings.append(
                f"Memory utilization ({result.analysis.memory_utilization_pct:.1f}%) exceeds maximum limit "
                f"({constraints.max_memory_utilization_pct:.1f}%)"
            )

        if result.analysis.power_consumption_watts > constraints.max_power_consumption_watts:
            warnings.append(
                f"Power draw ({result.analysis.power_consumption_watts:.1f} W) exceeds maximum budget "
                f"({constraints.max_power_consumption_watts:.1f} W)"
            )
            
        if result.analysis.reliability_score < constraints.min_reliability_score:
            warnings.append(
                f"Reliability score ({result.analysis.reliability_score:.2f}) falls below target threshold "
                f"({constraints.min_reliability_score:.2f})"
            )

        if result.flight_controller.name not in constraints.allowed_flight_controllers:
            warnings.append(f"Flight Controller '{result.flight_controller.name}' is not in approved hardware list.")

        if result.companion_computer.name not in constraints.allowed_companion_computers and result.companion_computer.name != "None":
            warnings.append(f"Companion Computer '{result.companion_computer.name}' is not in approved hardware list.")

        if result.autonomy_stack.vision_based_navigation_active and result.time_synchronization.synchronization_protocol != "PTP":
            warnings.append("Vision-based navigation is enabled, but PTP time synchronization is not configured. Jitter may occur.")

        return warnings
