from backend.design.multirotor.electrical.electrical_result import ElectricalSpecification

class ElectricalValidationError(ValueError):
    """Exception raised when ElectricalSpecification validation fails."""
    pass

class ElectricalValidator:
    """
    Validates output specifications from the Electrical integration engine.
    """
    def validate_electrical(self, spec: ElectricalSpecification) -> None:
        """
        Validates Electrical properties. Raises ElectricalValidationError on failure.
        """
        if not spec:
            raise ElectricalValidationError("Electrical specification cannot be None.")
            
        if not spec.power_distribution:
            raise ElectricalValidationError("Selected power distribution system cannot be empty.")
            
        if spec.electrical_efficiency_pct <= 0.0 or spec.electrical_efficiency_pct > 100.0:
            raise ElectricalValidationError(f"Electrical efficiency percentage must be in (0, 100]. Obtained: {spec.electrical_efficiency_pct}")
            
        if not spec.wire_gauge_summary:
            raise ElectricalValidationError("Wire gauge summary dict cannot be empty.")
            
        if not spec.connector_summary:
            raise ElectricalValidationError("Connector summary dict cannot be empty.")
