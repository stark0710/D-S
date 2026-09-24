"""
VTOL Airfoil Database Subsystem

Purpose:
    Defines the `AirfoilDatabase` providing geometry data, pitching moments,
    and polar parameters for standard VTOL and glider airfoils.
"""

from typing import Dict, List, Any


class AirfoilDatabase:
    """
    In-memory database holding aerodynamic properties of standard airfoils.
    """

    _db: Dict[str, Dict[str, Any]] = {
        "Selig S1223": {
            "name": "Selig S1223",
            "thickness_ratio": 0.122,
            "camber": 0.081,
            "le_radius": 0.022,
            "max_thickness_loc": 0.20,
            "max_camber_loc": 0.35,
            "cm0": -0.142,
            "cl_max": 1.95,
            "cd0": 0.021,
            "description": "High-lift low-speed airfoil designed for cargo planes.",
        },
        "NACA 4412": {
            "name": "NACA 4412",
            "thickness_ratio": 0.120,
            "camber": 0.040,
            "le_radius": 0.016,
            "max_thickness_loc": 0.30,
            "max_camber_loc": 0.40,
            "cm0": -0.090,
            "cl_max": 1.45,
            "cd0": 0.010,
            "description": "Classic cambered general aviation and utility drone airfoil.",
        },
        "NACA 0012": {
            "name": "NACA 0012",
            "thickness_ratio": 0.120,
            "camber": 0.0,
            "le_radius": 0.016,
            "max_thickness_loc": 0.30,
            "max_camber_loc": 0.0,
            "cm0": 0.0,
            "cl_max": 1.10,
            "cd0": 0.008,
            "description": "Symmetric airfoil used for tail stabilizers and tilt-rotors.",
        },
        "Clark Y": {
            "name": "Clark Y",
            "thickness_ratio": 0.117,
            "camber": 0.034,
            "le_radius": 0.015,
            "max_thickness_loc": 0.28,
            "max_camber_loc": 0.35,
            "cm0": -0.080,
            "cl_max": 1.38,
            "cd0": 0.012,
            "description": "Flat-bottomed wing airfoil, highly suitable for easy foam manufacturing.",
        },
        "MH 32": {
            "name": "MH 32",
            "thickness_ratio": 0.087,
            "camber": 0.024,
            "le_radius": 0.010,
            "max_thickness_loc": 0.32,
            "max_camber_loc": 0.40,
            "cm0": -0.052,
            "cl_max": 1.25,
            "cd0": 0.007,
            "description": "High performance low-drag glider airfoil with high L/D.",
        },
        "MH 45": {
            "name": "MH 45",
            "thickness_ratio": 0.098,
            "camber": 0.016,
            "le_radius": 0.011,
            "max_thickness_loc": 0.28,
            "max_camber_loc": 0.35,
            "cm0": 0.012,  # Reflexed trailing edge gives positive pitching moment
            "cl_max": 1.05,
            "cd0": 0.009,
            "description": "Reflexed airfoil designed for tailless flying wings or tilt wings.",
        },
        "Eppler 387": {
            "name": "Eppler 387",
            "thickness_ratio": 0.091,
            "camber": 0.038,
            "le_radius": 0.012,
            "max_thickness_loc": 0.30,
            "max_camber_loc": 0.38,
            "cm0": -0.072,
            "cl_max": 1.30,
            "cd0": 0.011,
            "description": "Smooth stall transition airfoil at low Reynolds numbers.",
        },
        "RG 15": {
            "name": "RG 15",
            "thickness_ratio": 0.089,
            "camber": 0.018,
            "le_radius": 0.010,
            "max_thickness_loc": 0.30,
            "max_camber_loc": 0.35,
            "cm0": -0.043,
            "cl_max": 1.20,
            "cd0": 0.007,
            "description": "Thin streamlined airfoil optimized for clean fast gliding.",
        },
    }

    @classmethod
    def get_airfoil(cls, name: str) -> Dict[str, Any] | None:
        """Retrieves details of an airfoil by name."""
        return cls._db.get(name)

    @classmethod
    def get_all_airfoils(cls) -> List[str]:
        """Returns list of names of all registered airfoils."""
        return list(cls._db.keys())
