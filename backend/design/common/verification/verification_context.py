from typing import Dict, Any

class VerificationContext:
    def __init__(self, 
                 mission_requirements: Any, 
                 final_specification: Any, 
                 subsystem_specifications: Dict[str, Any], 
                 convergence_report: Dict[str, Any] = None):
        self.mission_requirements = mission_requirements
        self.final_specification = final_specification
        self.subsystem_specifications = subsystem_specifications
        self.convergence_report = convergence_report or {}
