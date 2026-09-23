from backend.design.multirotor.esc.esc_result import ESCSpecification

class EscValidationError(ValueError):
    """Exception raised when ESCSpecification validation fails."""
    pass

class EscValidator:
    """
    Validates output specifications from the ESC sizer solver.
    """
    def validate_esc(self, spec: ESCSpecification) -> None:
        """
        Validates ESC properties. Raises EscValidationError on failure.
        """
        if not spec:
            raise EscValidationError("ESC specification cannot be None.")
            
        if spec.continuous_current_a <= 0.0:
            raise EscValidationError(f"Continuous current must be positive. Obtained: {spec.continuous_current_a}")
            
        if spec.weight_kg <= 0.0:
            raise EscValidationError(f"ESC weight must be positive. Obtained: {spec.weight_kg}")
            
        if not spec.protocol:
            raise EscValidationError("Selected signaling protocol cannot be empty.")
            
        if spec.current_margin_a < 0.0:
            raise EscValidationError(f"Current safety margin must be non-negative. Obtained: {spec.current_margin_a}")
