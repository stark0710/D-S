from backend.design.multirotor.propeller.propeller_result import PropellerSpecification

class PropellerValidationError(ValueError):
    """Exception raised when PropellerSpecification validation fails."""
    pass

class PropellerValidator:
    """
    Validates output specifications from the propeller sizer solver.
    """
    def validate_propeller(self, spec: PropellerSpecification) -> None:
        """
        Validates propeller properties. Raises PropellerValidationError on failure.
        """
        if not spec:
            raise PropellerValidationError("Propeller specification cannot be None.")
            
        if spec.diameter_m <= 0.0:
            raise PropellerValidationError(f"Propeller diameter must be positive. Obtained: {spec.diameter_m}")
            
        if spec.pitch_m <= 0.0:
            raise PropellerValidationError(f"Propeller pitch must be positive. Obtained: {spec.pitch_m}")
            
        if spec.hover_efficiency_g_w <= 0.0:
            raise PropellerValidationError(f"Hover efficiency must be positive. Obtained: {spec.hover_efficiency_g_w}")
            
        if spec.weight_kg <= 0.0:
            raise PropellerValidationError(f"Propeller weight must be positive. Obtained: {spec.weight_kg}")
