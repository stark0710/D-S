from backend.design.multirotor.battery.battery_result import BatterySpecification, PropulsionAssembly

class BatteryValidationError(ValueError):
    """Exception raised when BatterySpecification or PropulsionAssembly validation fails."""
    pass

class BatteryValidator:
    """
    Validates output specifications from the Battery sizer solver.
    """
    def validate_battery(self, spec: BatterySpecification) -> None:
        """
        Validates Battery properties. Raises BatteryValidationError on failure.
        """
        if not spec:
            raise BatteryValidationError("Battery specification cannot be None.")
            
        if spec.voltage <= 0.0:
            raise BatteryValidationError(f"Battery voltage must be positive. Obtained: {spec.voltage}")
            
        if spec.weight_kg <= 0.0:
            raise BatteryValidationError(f"Battery weight must be positive. Obtained: {spec.weight_kg}")
            
        if spec.estimated_flight_time_min <= 0.0:
            raise BatteryValidationError(f"Flight time must be positive. Obtained: {spec.estimated_flight_time_min}")

    def validate_assembly(self, assembly: PropulsionAssembly) -> None:
        """
        Validates unified PropulsionAssembly components.
        """
        if not assembly:
            raise BatteryValidationError("PropulsionAssembly cannot be None.")
            
        if not assembly.motor or not assembly.propeller or not assembly.esc or not assembly.battery:
            raise BatteryValidationError("PropulsionAssembly contains missing or empty components.")
