"""
GeometryBuilder Subsystem

Purpose:
    Defines the `GeometryBuilder` class responsible for constructing parametric 3D CAD geometries for all subsystem components.

Role in Architecture:
    `GeometryBuilder` converts structural frame, propulsion, electrical, avionics, payload, and landing gear specs into `CADComponent` objects.
"""

from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.avionics.avionics_result import AvionicsResult
from backend.design.drone.payload.payload_result import PayloadResult
from backend.design.drone.cad.cad_component import CADComponent


class GeometryBuilder:
    """
    Parametric geometry construction service.

    Design Principles:
        - Single Responsibility Principle: Subsystem engineering data to 3D CAD parametric geometry conversion only.
    """

    def build_frame_geometry(self, structure_result: FrameResult) -> list[CADComponent]:
        """Builds frame center plate, arms, and landing gear CAD components."""
        comps: list[CADComponent] = []

        wb = structure_result.selected_frame.wheelbase_mm
        plate_side = wb * 0.25
        comps.append(
            CADComponent(
                name="Frame Center Plate Assembly",
                category="FRAME",
                bounding_box_mm=(plate_side, plate_side, 25.0),
                material="3K Carbon Fiber Plate 2.5mm",
                mass_g=structure_result.selected_frame.frame_weight_g * 0.40,
                position_mm=(0.0, 0.0, 0.0),
                cad_shape_type="BOX"
            )
        )

        gear = structure_result.landing_gear
        comps.append(
            CADComponent(
                name="Landing Gear Assembly",
                category="LANDING_GEAR",
                bounding_box_mm=(gear.height_mm * 1.2, gear.height_mm * 1.2, gear.height_mm),
                material="Carbon Fiber / Aluminum",
                mass_g=gear.weight_g,
                position_mm=(0.0, 0.0, -gear.height_mm / 2.0),
                cad_shape_type="BOX"
            )
        )

        return comps

    def build_propulsion_geometry(
        self,
        propulsion_result: PropulsionResult,
        structure_result: FrameResult
    ) -> list[CADComponent]:
        """Builds motor and propeller CAD components for all rotor positions."""
        comps: list[CADComponent] = []
        rotor_cnt = propulsion_result.selected_motors.get("rotor_count", 4)
        arm_len = structure_result.arm_geometry.arm_length_mm
        prop_diam = propulsion_result.selected_propellers.get("diameter_inch", 13.0) * 25.4

        import math
        for i in range(rotor_cnt):
            angle = (2.0 * math.pi * i) / (rotor_cnt // 2 if propulsion_result.selected_motors.get("coaxial", False) else rotor_cnt)
            mx = arm_len * math.cos(angle)
            my = arm_len * math.sin(angle)
            mz = 15.0 if (i % 2 == 0 or not propulsion_result.selected_motors.get("coaxial", False)) else -15.0

            comps.append(
                CADComponent(
                    name=f"BLDC Motor {i+1}",
                    category="MOTOR",
                    bounding_box_mm=(35.0, 35.0, 30.0),
                    material="Aluminum 7075 / Copper",
                    mass_g=propulsion_result.selected_motors.get("estimated_motor_weight_g", 55.0),
                    position_mm=(mx, my, mz),
                    cad_shape_type="CYLINDER"
                )
            )

            comps.append(
                CADComponent(
                    name=f"Propeller {i+1}",
                    category="PROPELLER",
                    bounding_box_mm=(prop_diam, 25.0, 15.0),
                    material="Carbon Fiber Reinforced Nylon",
                    mass_g=propulsion_result.selected_propellers.get("weight_per_prop_g", 10.0),
                    position_mm=(mx, my, mz + 20.0),
                    cad_shape_type="BOX"
                )
            )

        return comps

    def build_subsystem_geometry(
        self,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult,
        payload_result: PayloadResult
    ) -> list[CADComponent]:
        """Builds battery, ESC, avionics suite, and payload CAD components."""
        comps: list[CADComponent] = []

        # Battery
        bat_g = electrical_result.selected_battery.get("estimated_battery_weight_g", 600.0)
        comps.append(
            CADComponent(
                name="Main Battery Pack",
                category="BATTERY",
                bounding_box_mm=(150.0, 50.0, 45.0),
                material="LiPo / Li-Ion Pack",
                mass_g=bat_g,
                position_mm=(0.0, 0.0, -40.0),
                cad_shape_type="BOX"
            )
        )

        # Avionics FC
        comps.append(
            CADComponent(
                name="Flight Controller & GNSS Suite",
                category="FLIGHT_CONTROLLER",
                bounding_box_mm=(50.0, 50.0, 25.0),
                material="FR4 PCB / CNC Aluminum Case",
                mass_g=avionics_result.power_analysis.total_avionics_weight_g,
                position_mm=(0.0, 0.0, 20.0),
                cad_shape_type="BOX"
            )
        )

        # Payload
        pay_dims = payload_result.selected_payload.dimensions_mm
        pay_g = payload_result.selected_payload.mass_kg * 1000.0
        comps.append(
            CADComponent(
                name=payload_result.selected_payload.payload_name,
                category="PAYLOAD",
                bounding_box_mm=pay_dims,
                material="Optical / Aluminum Assembly",
                mass_g=pay_g,
                position_mm=(
                    payload_result.balance_analysis.cg_offset_x_mm,
                    payload_result.balance_analysis.cg_offset_y_mm,
                    -payload_result.balance_analysis.cg_offset_z_mm
                ),
                cad_shape_type="BOX"
            )
        )

        return comps
