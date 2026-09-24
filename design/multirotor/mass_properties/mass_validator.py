from backend.design.multirotor.mass_properties.mass_result import MassPropertiesSpecification

class MassValidationError(ValueError):
    """Exception raised when MassPropertiesSpecification validation fails."""
    pass

class MassValidator:
    """
    Validates output specifications from the Mass properties sizing engine.
    """
    def validate_mass_properties(self, spec: MassPropertiesSpecification) -> None:
        """
        Validates Mass properties. Raises MassValidationError on failure.
        """
        if not spec:
            raise MassValidationError("Mass specification cannot be None.")
            
        if spec.total_mass_kg <= 0.0:
            raise MassValidationError(f"Total mass must be positive. Obtained: {spec.total_mass_kg}")
            
        if spec.empty_mass_kg <= 0.0:
            raise MassValidationError(f"Empty mass must be positive. Obtained: {spec.empty_mass_kg}")
            
        if not spec.center_of_gravity:
            raise MassValidationError("Center of gravity coordinates cannot be empty.")
            
        if spec.moments_of_inertia["Ixx (kg*m^2)"] <= 0.0:
            raise MassValidationError("Moments of inertia must be positive.")

        # Validate principal axes existence and shape
        if not spec.principal_axes:
            raise MassValidationError("Principal axes cannot be empty.")
            
        for axis_name in ["roll_axis", "pitch_axis", "yaw_axis"]:
            if axis_name not in spec.principal_axes:
                raise MassValidationError(f"Missing principal axis: {axis_name}")
            vec = spec.principal_axes[axis_name]
            if len(vec) != 3:
                raise MassValidationError(f"Principal axis {axis_name} must be a 3D vector.")
            norm = sum(x**2 for x in vec)
            if abs(norm - 1.0) > 1e-3:
                raise MassValidationError(f"Principal axis {axis_name} must be a unit vector. Norm squared: {norm}")
                
        # Validate orthogonality of principal axes
        v_roll = spec.principal_axes["roll_axis"]
        v_pitch = spec.principal_axes["pitch_axis"]
        v_yaw = spec.principal_axes["yaw_axis"]
        
        dot_rp = sum(x*y for x, y in zip(v_roll, v_pitch))
        dot_py = sum(x*y for x, y in zip(v_pitch, v_yaw))
        dot_ry = sum(x*y for x, y in zip(v_roll, v_yaw))
        
        if abs(dot_rp) > 1e-2 or abs(dot_py) > 1e-2 or abs(dot_ry) > 1e-2:
            raise MassValidationError(
                f"Principal axes are not orthogonal. Dot products: "
                f"roll.pitch = {dot_rp:.4f}, pitch.yaw = {dot_py:.4f}, roll.yaw = {dot_ry:.4f}"
            )
