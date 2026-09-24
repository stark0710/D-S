from backend.design.multirotor.motor.motor_result import MotorSpecification

class MotorValidationError(ValueError):
    """Exception raised when MotorSpecification validation fails."""
    pass

class MotorValidator:
    """
    Validates output specifications from the motor sizer solver.
    """
    def validate_motor(self, spec: MotorSpecification) -> None:
        """
        Validates motor properties. Raises MotorValidationError on failure.
        """
        if not spec:
            raise MotorValidationError("Motor specification cannot be None.")
            
        if spec.kv <= 0.0:
            raise MotorValidationError(f"Motor KV must be positive. Obtained: {spec.kv}")
            
        if spec.max_thrust_n <= 0.0:
            raise MotorValidationError(f"Max thrust must be positive. Obtained: {spec.max_thrust_n}")
            
        if spec.hover_current_a <= 0.0:
            raise MotorValidationError(f"Hover current must be positive. Obtained: {spec.hover_current_a}")
            
        if spec.weight_kg <= 0.0:
            raise MotorValidationError(f"Motor weight must be positive. Obtained: {spec.weight_kg}")
