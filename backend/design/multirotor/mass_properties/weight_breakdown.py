from dataclasses import dataclass

@dataclass(slots=True)
class WeightBreakdownResult:
    """
    Subsystem weight breakdown details and mass fractions.
    """
    empty_mass_kg: float
    payload_mass_kg: float
    battery_mass_kg: float
    propulsion_mass_kg: float
    electrical_mass_kg: float
    frame_mass_kg: float
    avionics_mass_kg: float
    total_mass_kg: float
    
    # Mass fractions
    payload_fraction: float
    battery_fraction: float
    structural_fraction: float


class WeightBreakdown:
    """
    Computes system weight details and mass fractions.
    """
    @staticmethod
    def calculate_breakdown(
        payload_kg: float,
        frame_mass_kg: float,
        motor_weight_kg: float,
        prop_weight_kg: float,
        esc_weight_kg: float,
        battery_weight_kg: float,
        wire_weight_kg: float,
        pdb_weight_kg: float,
        arm_count: int
    ) -> WeightBreakdownResult:
        """
        Sums categories and resolves component mass fractions.
        """
        # 1. Subsystem masses
        propulsion_mass = arm_count * (motor_weight_kg + prop_weight_kg + esc_weight_kg)
        electrical_mass = wire_weight_kg + pdb_weight_kg
        
        # FC (15g) + GPS (10g) + Telemetry (8g) + Receiver (4g) = 0.037 kg
        avionics_mass = 0.037
        
        empty_mass = frame_mass_kg + propulsion_mass + electrical_mass + avionics_mass
        total_mass = empty_mass + payload_kg + battery_weight_kg
        
        # 2. Fractions
        payload_fraction = payload_kg / total_mass
        battery_fraction = battery_weight_kg / total_mass
        structural_fraction = (frame_mass_kg + electrical_mass) / total_mass

        return WeightBreakdownResult(
            empty_mass_kg=empty_mass,
            payload_mass_kg=payload_kg,
            battery_mass_kg=battery_weight_kg,
            propulsion_mass_kg=propulsion_mass,
            electrical_mass_kg=electrical_mass,
            frame_mass_kg=frame_mass_kg,
            avionics_mass_kg=avionics_mass,
            total_mass_kg=total_mass,
            payload_fraction=payload_fraction,
            battery_fraction=battery_fraction,
            structural_fraction=structural_fraction
        )
