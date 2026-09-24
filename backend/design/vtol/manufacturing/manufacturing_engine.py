from .manufacturing_requirements import ManufacturingRequirements
from .manufacturing_profile import ManufacturingProfile
from .manufacturing_constraints import ManufacturingConstraints
from .manufacturing_result import ManufacturingResult
from .manufacturing_registry import ManufacturingRegistry
from .manufacturing_validator import ManufacturingValidator

class VTOLManufacturingEngine:
    """
    Façade manager coordinating complete VTOL aircraft manufacturing release outputs.
    """
    def __init__(self, profile: ManufacturingProfile = None, constraints: ManufacturingConstraints = None):
        self.profile = profile or ManufacturingProfile()
        self.constraints = constraints or ManufacturingConstraints()

    def design(self, requirements: ManufacturingRequirements) -> ManufacturingResult:
        strategy = ManufacturingRegistry.get_strategy(requirements.mission_result.mission_profile.mission_category)
        result = strategy.generate_package(requirements, self.profile)
        
        errors = ManufacturingValidator.validate(result, self.constraints)
        if errors:
            result.warnings.extend(errors)
            
        return result
