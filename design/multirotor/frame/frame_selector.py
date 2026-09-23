from dataclasses import dataclass
from typing import List, Optional

@dataclass(slots=True)
class CatalogFrameRecord:
    """
    Metadata representation of an off-the-shelf catalog frame option.
    """
    name: str
    configuration_type: str  # e.g., "Quadcopter X", "Hexacopter X", "Octocopter X", "Coaxial X8"
    wheelbase_m: float
    empty_mass_kg: float
    max_propeller_diameter_m: float
    arm_diameter_m: float
    price_usd: float
    landing_gear_height_m: float


class FrameSelector:
    """
    Queries catalog frame options matching wheelbase and configurations constraints.
    """
    def __init__(self) -> None:
        self._catalog: List[CatalogFrameRecord] = [
            CatalogFrameRecord("Micro 210 Carbon", "Quadcopter X", 0.21, 0.095, 0.127, 0.008, 15.0, 0.04),
            CatalogFrameRecord("DJI F450 FlameWheel", "Quadcopter X", 0.45, 0.282, 0.254, 0.012, 35.0, 0.08),
            CatalogFrameRecord("Tarot FY650 Sport", "Quadcopter X", 0.65, 0.476, 0.381, 0.016, 120.0, 0.15),
            CatalogFrameRecord("Tarot 680PRO Hexa", "Hexacopter X", 0.68, 0.530, 0.330, 0.016, 160.0, 0.18),
            CatalogFrameRecord("Tarot T810 Carbon", "Hexacopter X", 0.81, 1.020, 0.381, 0.025, 280.0, 0.22),
            CatalogFrameRecord("Tarot T18 Heavy", "Octocopter X", 1.27, 2.000, 0.457, 0.025, 540.0, 0.35),
            CatalogFrameRecord("Tarot T18 Coaxial X8", "Coaxial X8", 1.27, 2.100, 0.457, 0.025, 560.0, 0.35),
        ]

    def get_matching_frames(self, config: str, max_wheelbase: float) -> List[CatalogFrameRecord]:
        """
        Filters catalog records that support the configuration layout and do not exceed maximum size constraints.
        """
        results: List[CatalogFrameRecord] = []
        conf_clean = config.lower().replace(" ", "").replace("copter", "").strip()

        for f in self._catalog:
            f_conf_clean = f.configuration_type.lower().replace(" ", "").replace("copter", "").strip()
            
            # Check configuration compatibility
            if conf_clean in f_conf_clean or f_conf_clean in conf_clean:
                if f.wheelbase_m <= max_wheelbase:
                    results.append(f)
        return results

    def get_all_frames(self) -> List[CatalogFrameRecord]:
        """Returns the full catalog list."""
        return list(self._catalog)
