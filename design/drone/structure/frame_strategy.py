"""
FrameStrategy Subsystem

Purpose:
    Defines the abstract `FrameStrategy` interface and concrete structural design strategies.

Role in Architecture:
    `FrameStrategy` implements the Strategy Pattern to generate structural frame specifications (Lightweight, Heavy Lift,
    Long Endurance, Compact, Industrial, Balanced).
"""

from abc import ABC, abstractmethod
from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.structure.arm_geometry import ArmGeometry
from backend.design.drone.structure.landing_gear import LandingGear
from backend.design.drone.structure.mounting_layout import MountingLayout
from backend.design.drone.structure.frame_profile import FrameProfile
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.structure.frame_analysis import FrameAnalysis


class FrameStrategy(ABC):
    """
    Abstract interface for multirotor structural design strategies.
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Unique identifier name of the strategy."""
        pass

    @abstractmethod
    def calculate_structure(
        self,
        mission: DroneMissionProfile,
        config_type: str,
        rotor_count: int,
        coaxial: bool,
        estimated_auw_kg: float
    ) -> FrameResult:
        """
        Calculates complete FrameResult for a multirotor airframe.

        Args:
            mission (DroneMissionProfile): Mission profile.
            config_type (str): Selected configuration ('QUAD_X', 'HEXACOPTER', 'OCTOCOPTER', etc.).
            rotor_count (int): Total rotor count.
            coaxial (bool): True if coaxial frame.
            estimated_auw_kg (float): Estimated All-Up Weight in kg.

        Returns:
            FrameResult: Completed structural frame engineering result.
        """
        pass


class BalancedFrameStrategy(FrameStrategy):
    """Standard balanced multirotor structural design strategy."""

    @property
    def strategy_name(self) -> str:
        return "BalancedFrameStrategy"

    def calculate_structure(
        self,
        mission: DroneMissionProfile,
        config_type: str,
        rotor_count: int,
        coaxial: bool,
        estimated_auw_kg: float
    ) -> FrameResult:
        analysis = FrameAnalysis()
        wb = analysis.calculate_wheelbase(rotor_count, estimated_auw_kg, coaxial)
        arm_len = analysis.calculate_arm_length(wb, rotor_count, coaxial)
        max_prop = analysis.calculate_max_propeller_inch(wb, rotor_count, coaxial)
        fw = analysis.estimate_frame_weight(wb, rotor_count, heavy_duty=False)

        profile = FrameProfile(
            frame_name=f"Standard {config_type} {wb:.0f}mm Frame",
            wheelbase_mm=wb,
            frame_weight_g=fw,
            max_propeller_diameter_inch=max_prop,
            material="Carbon Fiber 3K Composite",
            stiffness_rating="HIGH"
        )

        arm_geo = ArmGeometry(
            arm_length_mm=arm_len,
            arm_tube_outer_diameter_mm=25.0,
            arm_tube_inner_diameter_mm=23.0,
            folding_mechanism=False
        )

        gear = LandingGear(
            gear_type="FIXED_SKID",
            ground_clearance_mm=160.0,
            height_mm=220.0,
            weight_g=190.0
        )

        layout = MountingLayout(
            flight_controller_pattern_mm="30.5x30.5",
            battery_mount_type="SLIDING_TRAY",
            payload_mount_type="QUICK_RELEASE_RAIL"
        )

        return FrameResult(
            selected_frame=profile,
            frame_dimensions={"wheelbase_mm": wb, "arm_length_mm": arm_len, "height_mm": 220.0},
            arm_geometry=arm_geo,
            mounting_layout=layout,
            landing_gear=gear,
            estimated_structure_weight_g=fw + gear.weight_g,
            engineering_notes=f"Balanced structural design with {wb:.0f}mm wheelbase supporting up to {max_prop:.1f}\" propellers."
        )


class LightweightFrameStrategy(FrameStrategy):
    """Minimizes airframe weight using thin-wall carbon fiber tubing and skeletonized center plates."""

    @property
    def strategy_name(self) -> str:
        return "LightweightFrameStrategy"

    def calculate_structure(
        self,
        mission: DroneMissionProfile,
        config_type: str,
        rotor_count: int,
        coaxial: bool,
        estimated_auw_kg: float
    ) -> FrameResult:
        analysis = FrameAnalysis()
        wb = analysis.calculate_wheelbase(rotor_count, estimated_auw_kg, coaxial)
        arm_len = analysis.calculate_arm_length(wb, rotor_count, coaxial)
        max_prop = analysis.calculate_max_propeller_inch(wb, rotor_count, coaxial)
        fw = round(analysis.estimate_frame_weight(wb, rotor_count, heavy_duty=False) * 0.78, 1)

        profile = FrameProfile(
            frame_name=f"Lightweight Ultralight {config_type} {wb:.0f}mm Frame",
            wheelbase_mm=wb,
            frame_weight_g=fw,
            max_propeller_diameter_inch=max_prop,
            material="Ultralight Carbon Fiber Skeleton",
            stiffness_rating="STANDARD"
        )

        arm_geo = ArmGeometry(
            arm_length_mm=arm_len,
            arm_tube_outer_diameter_mm=16.0,
            arm_tube_inner_diameter_mm=14.5,
            folding_mechanism=False
        )

        gear = LandingGear(
            gear_type="INTEGRATED_LEG",
            ground_clearance_mm=120.0,
            height_mm=150.0,
            weight_g=80.0
        )

        layout = MountingLayout(
            flight_controller_pattern_mm="20x20",
            battery_mount_type="BOTTOM_STRAP",
            payload_mount_type="BOTTOM_PLATE_BOLTS"
        )

        return FrameResult(
            selected_frame=profile,
            frame_dimensions={"wheelbase_mm": wb, "arm_length_mm": arm_len, "height_mm": 150.0},
            arm_geometry=arm_geo,
            mounting_layout=layout,
            landing_gear=gear,
            estimated_structure_weight_g=fw + gear.weight_g,
            engineering_notes="Lightweight structural frame optimization for maximum endurance."
        )


class HeavyLiftFrameStrategy(FrameStrategy):
    """Heavy-duty structural frame with 30mm carbon tubes and reinforced center plates."""

    @property
    def strategy_name(self) -> str:
        return "HeavyLiftFrameStrategy"

    def calculate_structure(
        self,
        mission: DroneMissionProfile,
        config_type: str,
        rotor_count: int,
        coaxial: bool,
        estimated_auw_kg: float
    ) -> FrameResult:
        analysis = FrameAnalysis()
        wb = analysis.calculate_wheelbase(rotor_count, estimated_auw_kg, coaxial)
        arm_len = analysis.calculate_arm_length(wb, rotor_count, coaxial)
        max_prop = analysis.calculate_max_propeller_inch(wb, rotor_count, coaxial)
        fw = analysis.estimate_frame_weight(wb, rotor_count, heavy_duty=True)

        profile = FrameProfile(
            frame_name=f"Heavy-Duty Heavy-Lift {config_type} {wb:.0f}mm Frame",
            wheelbase_mm=wb,
            frame_weight_g=fw,
            max_propeller_diameter_inch=max_prop,
            material="High-Modulus Carbon Fiber & CNC T6 Aluminum",
            stiffness_rating="ULTRA_RIGID"
        )

        arm_geo = ArmGeometry(
            arm_length_mm=arm_len,
            arm_tube_outer_diameter_mm=30.0,
            arm_tube_inner_diameter_mm=27.0,
            folding_mechanism=True
        )

        gear = LandingGear(
            gear_type="RETRACTABLE",
            ground_clearance_mm=250.0,
            height_mm=320.0,
            weight_g=450.0
        )

        layout = MountingLayout(
            flight_controller_pattern_mm="45x45",
            battery_mount_type="DUAL_SLIDING_TRAY",
            payload_mount_type="QUICK_RELEASE_RAIL",
            center_plate_dimensions_mm=(280.0, 280.0)
        )

        return FrameResult(
            selected_frame=profile,
            frame_dimensions={"wheelbase_mm": wb, "arm_length_mm": arm_len, "height_mm": 320.0},
            arm_geometry=arm_geo,
            mounting_layout=layout,
            landing_gear=gear,
            estimated_structure_weight_g=fw + gear.weight_g,
            engineering_notes="Reinforced heavy-lift structural frame with folding arms and retractable landing gear."
        )
