from backend.design.multirotor.frame.frame_result import FrameSpecification

class FrameValidationError(ValueError):
    """Exception raised when FrameSpecification validation fails."""
    pass

class FrameValidator:
    """
    Validates the generated FrameSpecification output object.
    """
    def validate_frame(self, spec: FrameSpecification) -> None:
        """
        Validates the frame spec properties. Raises FrameValidationError on failure.
        """
        if not spec:
            raise FrameValidationError("Frame specification cannot be None.")
        
        if spec.wheelbase_m <= 0.0:
            raise FrameValidationError(f"Wheelbase must be positive. Obtained: {spec.wheelbase_m}")
            
        if spec.frame_mass_kg <= 0.0:
            raise FrameValidationError(f"Frame mass must be positive. Obtained: {spec.frame_mass_kg}")
            
        if len(spec.motor_coordinates) == 0:
            raise FrameValidationError("Motor coordinate positions cannot be empty.")
            
        if spec.ground_clearance_m <= 0.0:
            raise FrameValidationError(f"Ground clearance must be positive. Obtained: {spec.ground_clearance_m}")
