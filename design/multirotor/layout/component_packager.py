from dataclasses import dataclass
from typing import Dict

@dataclass
class BoundingBox3D:
    """
    3D spatial bounding box representation of a component.
    """
    name: str
    x_c: float
    y_c: float
    z_c: float
    dx: float
    dy: float
    dz: float

    def intersects(self, other: "BoundingBox3D") -> bool:
        """
        Determines if two 3D bounding boxes intersect (collision check).
        """
        x_overlap = abs(self.x_c - other.x_c) < 0.5 * (self.dx + other.dx)
        y_overlap = abs(self.y_c - other.y_c) < 0.5 * (self.dy + other.dy)
        z_overlap = abs(self.z_c - other.z_c) < 0.5 * (self.dz + other.dz)
        return x_overlap and y_overlap and z_overlap


class ComponentPackager:
    """
    Standardizes 3D packaging envelopes and checks for overlaps.
    """
    @staticmethod
    def get_fc_envelope(x: float, y: float, z: float) -> BoundingBox3D:
        return BoundingBox3D("FlightController", x, y, z, 0.05, 0.05, 0.02)

    @staticmethod
    def get_gps_envelope(x: float, y: float, z: float) -> BoundingBox3D:
        return BoundingBox3D("GPSReceiver", x, y, z, 0.04, 0.04, 0.015)

    @staticmethod
    def get_telemetry_envelope(x: float, y: float, z: float) -> BoundingBox3D:
        return BoundingBox3D("TelemetryModem", x, y, z, 0.04, 0.025, 0.01)

    @staticmethod
    def get_receiver_envelope(x: float, y: float, z: float) -> BoundingBox3D:
        return BoundingBox3D("RcReceiver", x, y, z, 0.03, 0.015, 0.008)

    @staticmethod
    def get_pdb_envelope(x: float, y: float, z: float) -> BoundingBox3D:
        return BoundingBox3D("PowerDistributionBoard", x, y, z, 0.06, 0.06, 0.015)

    @staticmethod
    def get_battery_envelope(x: float, y: float, z: float, battery_weight_kg: float) -> BoundingBox3D:
        # Estimate battery dimensions based on weight scaling
        vol = battery_weight_kg / 2000.0  # density index approx 2000kg/m3
        side = vol ** (1.0 / 3.0)
        # Typically battery is a brick (rectangular prism)
        return BoundingBox3D("BatteryPack", x, y, z, side * 1.5, side * 0.8, side * 0.8)

    @staticmethod
    def get_payload_envelope(x: float, y: float, z: float, dimensions_m: tuple[float, float, float]) -> BoundingBox3D:
        return BoundingBox3D("PayloadBay", x, y, z, dimensions_m[0], dimensions_m[1], dimensions_m[2])
