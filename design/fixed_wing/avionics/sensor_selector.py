"""
Fixed-Wing Avionics Sensor Selector Subsystem

Purpose:
    Defines the `SensorSelector` class and sensor database.

Role in Architecture:
    `SensorSelector` queries airspeed sensors, compasses, barometers, and lidars.
"""

from typing import List


class SensorRecord:
    """Sensor description."""

    def __init__(self, name: str, weight_g: float, category: str, interface: str, power_w: float) -> None:
        self.name = name
        self.weight_g = weight_g
        self.category = category  # "Airspeed", "Lidar", "Compass"
        self.interface = interface
        self.power_w = power_w


class SensorSelector:
    """
    Selector class matching sensor categories to hardware units.
    """

    _sensors: List[SensorRecord] = [
        SensorRecord("MS5611 Barometer", 2, "Barometer", "I2C", 0.01),
        SensorRecord("Holybro Digital Airspeed Sensor", 10, "Airspeed", "I2C", 0.1),
        SensorRecord("Matek CAN Compass", 8, "Compass", "CAN", 0.15),
        SensorRecord("Benewake TFmini Plus Lidar", 12, "Lidar", "UART", 0.5),
        SensorRecord("LightWare SF11/C Laser Altimeter", 35, "Lidar", "I2C", 1.1),
    ]

    def select_sensors(self, mission_category: str) -> List[SensorRecord]:
        """
        Selects standard sensors based on flight profile.
        """
        selected: List[SensorRecord] = []
        
        # Airspeed is critical for all fixed wings to avoid stall!
        selected.append(self._sensors[1])  # Airspeed
        
        # Compass is critical for navigation
        selected.append(self._sensors[2])  # Compass

        # Sized mapping models need Lidar ground altimeter for precision survey grids
        if mission_category.lower() in ("survey", "mapping"):
            selected.append(self._sensors[3])  # TFmini Lidar
        elif mission_category.lower() == "cargo":
            selected.append(self._sensors[4])  # Heavy SF11 Laser

        return selected
