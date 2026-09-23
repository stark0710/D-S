"""
Fixed-Wing Camera Selector Subsystem

Purpose:
    Defines the `CameraSelector` class and camera sensors database.

Role in Architecture:
    `CameraSelector` selects FPV or mapping cameras.
"""

from typing import List


class CameraRecord:
    """Camera description."""

    def __init__(self, name: str, weight_g: float, resolution_mp: float, price: float, primary_use: str) -> None:
        self.name = name
        self.weight_g = weight_g
        self.resolution_mp = resolution_mp
        self.price = price
        self.primary_use = primary_use


class CameraSelector:
    """
    Selector class matching camera uses to hardware units.
    """

    _cameras: List[CameraRecord] = [
        CameraRecord("RunCam Swift FPV", 12, 0.5, 45.0, "FPV Navigation"),
        CameraRecord("RunCam Split 4 HD", 26, 8.0, 95.0, "HD Video Recording"),
        CameraRecord("GoPro Hero 11", 154, 27.0, 399.0, "High-Res Action Capture"),
        CameraRecord("FLIR Duo Pro R", 220, 12.0, 4800.0, "Agricultural Thermal Mapping"),
        CameraRecord("Sony RX1R II", 507, 42.4, 3299.0, "Survey and Mapping Photogrammetry"),
    ]

    def select_camera(self, primary_use: str) -> CameraRecord | None:
        for camera in self._cameras:
            if primary_use.lower() in camera.primary_use.lower():
                return camera
        return None
