from dataclasses import dataclass
from typing import List

@dataclass(slots=True)
class CatalogBatteryRecord:
    """
    Metadata representation of a battery pack in the component catalog.
    """
    manufacturer: str
    model: str
    chemistry: str  # "LiPo", "LiHV", "Li-Ion"
    capacity_mah: float
    cell_count: int
    continuous_c_rating: float
    burst_c_rating: float
    empty_mass_kg: float
    nominal_voltage_v: float
    price_usd: float


class BatterySelector:
    """
    Manages catalog search queries and filters for compatible batteries.
    """
    def __init__(self) -> None:
        self._catalog: List[CatalogBatteryRecord] = [
            CatalogBatteryRecord("T-Line", "1300mAh 4S LiPo", "LiPo", 1300.0, 4, 95.0, 190.0, 0.150, 14.8, 25.00),
            CatalogBatteryRecord("T-Line", "4500mAh 6S LiPo", "LiPo", 4500.0, 6, 60.0, 120.0, 0.650, 22.2, 75.00),
            CatalogBatteryRecord("GensAce", "10000mAh 6S LiPo", "LiPo", 10000.0, 6, 25.0, 50.0, 1.420, 22.2, 150.00),
            CatalogBatteryRecord("T-Motor", "16000mAh 6S LiHV", "LiHV", 16000.0, 6, 15.0, 30.0, 1.980, 22.8, 240.00),
            CatalogBatteryRecord("T-Motor", "22000mAh 12S LiPo", "LiPo", 22000.0, 12, 25.0, 50.0, 4.600, 44.4, 450.00),
            CatalogBatteryRecord("Molicel", "4200mAh 6S Li-Ion", "Li-Ion", 4200.0, 6, 8.3, 10.7, 0.430, 22.2, 40.00),  # 35A cont, 45A burst
            CatalogBatteryRecord("Samsung", "5000mAh 6S Li-Ion", "Li-Ion", 5000.0, 6, 3.0, 5.0, 0.435, 22.2, 35.00),  # 15A cont, 25A burst
        ]

    def get_all_batteries(self) -> List[CatalogBatteryRecord]:
        """Returns the full catalog list."""
        return list(self._catalog)
