from dataclasses import dataclass

@dataclass(slots=True)
class ComponentMass:
    """
    Discrete item weights and coordinate offsets.
    """
    name: str
    mass_kg: float
    x_m: float  # forward positive relative to center
    y_m: float  # right positive
    z_m: float  # up positive
