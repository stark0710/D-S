from backend.design.multirotor.layout.layout_result import LayoutSpecification

class LayoutValidationError(ValueError):
    """Exception raised when LayoutSpecification validation fails."""
    pass

class LayoutValidator:
    """
    Validates output specifications from the Layout integration engine.
    """
    def validate_layout(self, spec: LayoutSpecification) -> None:
        """
        Validates Layout properties. Raises LayoutValidationError on failure.
        """
        if not spec:
            raise LayoutValidationError("Layout specification cannot be None.")
            
        if not spec.component_coordinates:
            raise LayoutValidationError("Component coordinates dict cannot be empty.")
            
        if "FlightController" not in spec.component_coordinates:
            raise LayoutValidationError("FlightController coordinates are missing from layout spec.")
            
        if spec.accessibility_score < 0.0 or spec.accessibility_score > 100.0:
            raise LayoutValidationError(f"Accessibility score must be in range [0, 100]. Obtained: {spec.accessibility_score}")
