import math
from dataclasses import dataclass
from typing import List, Tuple

@dataclass(slots=True)
class FrameGeometry:
    """
    Physical geometric properties of a multirotor frame design candidate.
    """
    configuration: str
    wheelbase_m: float
    arm_length_m: float
    arm_diameter_m: float
    arm_count: int
    motor_positions: List[Tuple[float, float, float]]  # (x, y, z) coordinates in meters
    payload_bay_dimensions_m: Tuple[float, float, float]  # (length, width, height)
    landing_gear_height_m: float
    ground_clearance_m: float
    envelope_dimensions_m: Tuple[float, float, float]  # (outer diameter, width, height)
    arm_thickness_m: float = 0.002  # default tube wall thickness 2mm


class FrameGeometryGenerator:
    """
    Generator class executing coordinate mathematics for multirotor topologies.
    """
    @staticmethod
    def generate_motor_coordinates(config: str, arm_length: float) -> List[Tuple[float, float, float]]:
        """
        Calculates (x, y, z) coordinates of motors relative to center of thrust.
        """
        coords: List[Tuple[float, float, float]] = []
        config_clean = config.lower().replace("copter", "").replace(" ", "").strip()
        L = arm_length

        if "quadx" in config_clean:
            angles = [45.0, 135.0, 225.0, 315.0]
            for a in angles:
                rad = math.radians(a)
                coords.append((round(L * math.cos(rad), 4), round(L * math.sin(rad), 4), 0.0))
        elif "quad+" in config_clean:
            angles = [0.0, 90.0, 180.0, 270.0]
            for a in angles:
                rad = math.radians(a)
                coords.append((round(L * math.cos(rad), 4), round(L * math.sin(rad), 4), 0.0))
        elif "hexx" in config_clean:
            angles = [30.0, 90.0, 150.0, 210.0, 270.0, 330.0]
            for a in angles:
                rad = math.radians(a)
                coords.append((round(L * math.cos(rad), 4), round(L * math.sin(rad), 4), 0.0))
        elif "hex+" in config_clean:
            angles = [0.0, 60.0, 120.0, 180.0, 240.0, 300.0]
            for a in angles:
                rad = math.radians(a)
                coords.append((round(L * math.cos(rad), 4), round(L * math.sin(rad), 4), 0.0))
        elif "octox" in config_clean:
            angles = [22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5]
            for a in angles:
                rad = math.radians(a)
                coords.append((round(L * math.cos(rad), 4), round(L * math.sin(rad), 4), 0.0))
        elif "octo+" in config_clean:
            angles = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]
            for a in angles:
                rad = math.radians(a)
                coords.append((round(L * math.cos(rad), 4), round(L * math.sin(rad), 4), 0.0))
        elif "coaxialx8" in config_clean or "x8" in config_clean:
            # 8 motors on 4 arms, upper and lower layout
            angles = [45.0, 135.0, 225.0, 315.0]
            dz = 0.04  # standard coaxial offset in meters
            for a in angles:
                rad = math.radians(a)
                x = round(L * math.cos(rad), 4)
                y = round(L * math.sin(rad), 4)
                coords.append((x, y, dz))
                coords.append((x, y, -dz))
        else:
            # Default to Quad X
            angles = [45.0, 135.0, 225.0, 315.0]
            for a in angles:
                rad = math.radians(a)
                coords.append((round(L * math.cos(rad), 4), round(L * math.sin(rad), 4), 0.0))
                
        return coords
