"""
Fixed-Wing Airfoil Database Subsystem

Purpose:
    Defines the standard airfoil database containing geometric properties and polar interpolation functions
    for UIUC, Airfoil Tools, and custom libraries.

Role in Architecture:
    `AirfoilDatabase` provides standard aerodynamic parameters (thickness, camber, C_m0, C_l_max, polar shapes)
    for lookup by selector engines.
"""

from typing import Dict, Any, List
from backend.design.fixed_wing.airfoil.airfoil_requirements import AirfoilType


class AirfoilRecord:
    """
    Representation of an airfoil definition in the database.
    """

    def __init__(
        self,
        name: str,
        airfoil_type: AirfoilType,
        thickness_ratio: float,
        camber_ratio: float,
        c_m0: float,
        c_l_max_ref: float,
        stall_angle_ref: float,
        c_d0_ref: float,
        c_l_opt: float,
        k_factor: float,
    ) -> None:
        self.name = name
        self.airfoil_type = airfoil_type
        self.thickness_ratio = thickness_ratio  # e.g. 0.117 for 11.7%
        self.camber_ratio = camber_ratio        # e.g. 0.034 for 3.4%
        self.c_m0 = c_m0                        # Pitching moment coefficient at zero lift
        self.c_l_max_ref = c_l_max_ref          # Cl_max at Re = 500,000
        self.stall_angle_ref = stall_angle_ref  # Stall angle at Re = 500,000 in degrees
        self.c_d0_ref = c_d0_ref                # Minimum drag Cd0 at Re = 500,000
        self.c_l_opt = c_l_opt                  # Cl at which Cd is minimized
        self.k_factor = k_factor                # Polar shape parameter Cd = Cd0 + K*(Cl - Cl_opt)^2

    def get_max_lift_coefficient(self, reynolds: float) -> float:
        """Reynolds-corrected maximum lift coefficient (Cl_max increases with Re)."""
        # Heuristic correction: Cl_max scales with log10(Re)
        factor = 1.0 + 0.15 * (reynolds / 500000.0 - 1.0)
        # Cap variance to avoid physical nonsense
        factor = max(0.7, min(1.3, factor))
        return round(self.c_l_max_ref * factor, 3)

    def get_stall_angle_deg(self, reynolds: float) -> float:
        """Reynolds-corrected stall angle (stall delay at high Re)."""
        factor = 1.0 + 0.1 * (reynolds / 500000.0 - 1.0)
        factor = max(0.8, min(1.2, factor))
        return round(self.stall_angle_ref * factor, 1)

    def get_drag_coefficient(self, c_l: float, reynolds: float) -> float:
        """Calculates CD based on CL and Reynolds number using a parabolic polar."""
        # Minimum drag decreases at higher Reynolds number due to thinner boundary layer
        # Cd0 = Cd0_ref * (Re_ref / Re)^0.2
        re_factor = (500000.0 / reynolds) ** 0.2
        re_factor = max(0.7, min(1.5, re_factor))
        c_d0 = self.c_d0_ref * re_factor

        # Parabolic increment Cd = Cd0 + K * (Cl - Cl_opt)^2
        c_d = c_d0 + self.k_factor * ((c_l - self.c_l_opt) ** 2)
        
        # Stall drag penalty: add penalty if Cl exceeds 90% of Cl_max
        c_l_max = self.get_max_lift_coefficient(reynolds)
        if abs(c_l) > 0.9 * c_l_max:
            excess = abs(c_l) - 0.9 * c_l_max
            c_d += 0.2 * (excess ** 2)

        return round(c_d, 5)


class AirfoilDatabase:
    """
    Central database library storing standard airfoils.
    """

    _db: Dict[str, AirfoilRecord] = {
        "Clark Y": AirfoilRecord(
            name="Clark Y",
            airfoil_type=AirfoilType.CAMBERED,
            thickness_ratio=0.117,
            camber_ratio=0.034,
            c_m0=-0.08,
            c_l_max_ref=1.35,
            stall_angle_ref=14.0,
            c_d0_ref=0.009,
            c_l_opt=0.35,
            k_factor=0.012,
        ),
        "NACA 4412": AirfoilRecord(
            name="NACA 4412",
            airfoil_type=AirfoilType.CAMBERED,
            thickness_ratio=0.120,
            camber_ratio=0.040,
            c_m0=-0.09,
            c_l_max_ref=1.40,
            stall_angle_ref=15.0,
            c_d0_ref=0.010,
            c_l_opt=0.40,
            k_factor=0.012,
        ),
        "NACA 0012": AirfoilRecord(
            name="NACA 0012",
            airfoil_type=AirfoilType.SYMMETRICAL,
            thickness_ratio=0.120,
            camber_ratio=0.000,
            c_m0=0.00,
            c_l_max_ref=1.10,
            stall_angle_ref=12.0,
            c_d0_ref=0.006,
            c_l_opt=0.00,
            k_factor=0.011,
        ),
        "Selig S1223": AirfoilRecord(
            name="Selig S1223",
            airfoil_type=AirfoilType.HIGH_LIFT,
            thickness_ratio=0.121,
            camber_ratio=0.081,
            c_m0=-0.142,
            c_l_max_ref=1.85,
            stall_angle_ref=16.0,
            c_d0_ref=0.018,
            c_l_opt=0.90,
            k_factor=0.018,
        ),
        "MH 32": AirfoilRecord(
            name="MH 32",
            airfoil_type=AirfoilType.LAMINAR_FLOW,
            thickness_ratio=0.087,
            camber_ratio=0.024,
            c_m0=-0.052,
            c_l_max_ref=1.15,
            stall_angle_ref=11.0,
            c_d0_ref=0.0055,
            c_l_opt=0.25,
            k_factor=0.009,
        ),
        "MH 45": AirfoilRecord(
            name="MH 45",
            airfoil_type=AirfoilType.REFLEXED,
            thickness_ratio=0.098,
            camber_ratio=0.018,
            c_m0=0.014,  # positive moment coefficient for tailless longitudinal stability!
            c_l_max_ref=0.95,
            stall_angle_ref=10.0,
            c_d0_ref=0.007,
            c_l_opt=0.18,
            k_factor=0.010,
        ),
        "SG6040": AirfoilRecord(
            name="SG6040",
            airfoil_type=AirfoilType.LAMINAR_FLOW,
            thickness_ratio=0.100,
            camber_ratio=0.020,
            c_m0=-0.065,
            c_l_max_ref=1.20,
            stall_angle_ref=12.0,
            c_d0_ref=0.006,
            c_l_opt=0.30,
            k_factor=0.010,
        )
    }

    @classmethod
    def get_airfoil(cls, name: str) -> AirfoilRecord | None:
        """Retrieves an airfoil record by name (case-insensitive)."""
        # Find exact case or case-insensitive match
        for key in cls._db:
            if key.lower() == name.lower():
                return cls._db[key]
        return None

    @classmethod
    def list_airfoils(cls) -> List[str]:
        return list(cls._db.keys())

    @classmethod
    def query_by_type(cls, airfoil_type: AirfoilType) -> List[AirfoilRecord]:
        return [record for record in cls._db.values() if record.airfoil_type == airfoil_type]
