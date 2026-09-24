"""
VTOL Geometry Layout Generator Subsystem

Purpose:
    Defines the `LayoutGenerator` class, calculating physical placements (X, Y, Z)
    for rotors, control surfaces, and sensors relative to the aircraft CG.
"""

from typing import Dict, List, Any
from backend.design.vtol.mission.mission_requirements import VTOLType


class LayoutGenerator:
    """
    Generates spatial layouts, coordinate positions, and channel counts
    based on the selected VTOL type and target MTOW.
    """

    def generate_layout(
        self, vtol_type: VTOLType, mtow_kg: float, motor_override: int | None = None
    ) -> Dict[str, Any]:
        """
        Generates motor and actuator coordinates.

        Scale factor scales dimensions with aircraft weight.
        """
        # Baseline dimensions scaling with MTOW
        scale = max(0.6, min(2.5, (mtow_kg / 10.0) ** 0.33))

        motor_placements: List[Dict[str, Any]] = []
        actuator_placements: List[Dict[str, Any]] = []
        surf_actuators: List[str] = []
        prop_actuators: List[str] = []
        tilt_actuators: List[str] = []

        # Determine structural parameters based on layout type
        if vtol_type == VTOLType.QUADPLANE:
            # 4 Lift motors + 1 pusher/tractor forward motor
            lift_count = 4
            forward_count = 1
            esc_count = 5
            servo_count = 4  # 2 ailerons, 1 elevator, 1 rudder

            # Hover motors (X frame shape)
            motor_placements.extend([
                {"name": "Hover Motor 1 (FR)", "x_m": round(0.4 * scale, 3), "y_m": round(0.4 * scale, 3), "z_m": 0.0, "type": "lift"},
                {"name": "Hover Motor 2 (FL)", "x_m": round(0.4 * scale, 3), "y_m": round(-0.4 * scale, 3), "z_m": 0.0, "type": "lift"},
                {"name": "Hover Motor 3 (RL)", "x_m": round(-0.4 * scale, 3), "y_m": round(-0.4 * scale, 3), "z_m": 0.0, "type": "lift"},
                {"name": "Hover Motor 4 (RR)", "x_m": round(-0.4 * scale, 3), "y_m": round(0.4 * scale, 3), "z_m": 0.0, "type": "lift"},
            ])
            # Cruise motor (pusher)
            motor_placements.append(
                {"name": "Cruise Motor (Pusher)", "x_m": round(-0.6 * scale, 3), "y_m": 0.0, "z_m": 0.0, "type": "forward"}
            )

            # Surface servos
            actuator_placements.extend([
                {"name": "Left Aileron Servo", "x_m": 0.0, "y_m": round(-0.7 * scale, 3), "z_m": 0.0, "type": "surface"},
                {"name": "Right Aileron Servo", "x_m": 0.0, "y_m": round(0.7 * scale, 3), "z_m": 0.0, "type": "surface"},
                {"name": "Elevator Servo", "x_m": round(-1.1 * scale, 3), "y_m": 0.0, "z_m": 0.1, "type": "surface"},
                {"name": "Rudder Servo", "x_m": round(-1.1 * scale, 3), "y_m": 0.0, "z_m": 0.2, "type": "surface"},
            ])
            surf_actuators.extend(["Left Aileron", "Right Aileron", "Elevator", "Rudder"])
            prop_actuators.extend(["ESC Lift 1", "ESC Lift 2", "ESC Lift 3", "ESC Lift 4", "ESC Forward"])

        elif vtol_type in (VTOLType.TILT_ROTOR, VTOLType.TILT_WING):
            # 2 Tilt motors + 0 separate forward motors (rotors tilt)
            # Typically 2 or 4 motors tilting
            tilt_count = 2 if motor_override is None or motor_override <= 2 else 4
            lift_count = tilt_count
            forward_count = tilt_count
            esc_count = tilt_count
            servo_count = 2 + tilt_count  # 2 flight surfaces (elevons) + tilt mechanism servos

            # Tilt motors
            if tilt_count == 2:
                motor_placements.extend([
                    {"name": "Tilt Motor L", "x_m": 0.0, "y_m": round(-0.6 * scale, 3), "z_m": 0.0, "type": "tilt_rotor"},
                    {"name": "Tilt Motor R", "x_m": 0.0, "y_m": round(0.6 * scale, 3), "z_m": 0.0, "type": "tilt_rotor"},
                ])
                tilt_actuators.extend(["Left Tilt Servo", "Right Tilt Servo"])
                actuator_placements.extend([
                    {"name": "Left Tilt Servo", "x_m": 0.0, "y_m": round(-0.58 * scale, 3), "z_m": 0.0, "type": "tilt_servo"},
                    {"name": "Right Tilt Servo", "x_m": 0.0, "y_m": round(0.58 * scale, 3), "z_m": 0.0, "type": "tilt_servo"},
                ])
            else:
                motor_placements.extend([
                    {"name": "Tilt Motor FL", "x_m": round(0.3 * scale, 3), "y_m": round(-0.5 * scale, 3), "z_m": 0.0, "type": "tilt_rotor"},
                    {"name": "Tilt Motor FR", "x_m": round(0.3 * scale, 3), "y_m": round(0.5 * scale, 3), "z_m": 0.0, "type": "tilt_rotor"},
                    {"name": "Tilt Motor RL", "x_m": round(-0.3 * scale, 3), "y_m": round(-0.5 * scale, 3), "z_m": 0.0, "type": "tilt_rotor"},
                    {"name": "Tilt Motor RR", "x_m": round(-0.3 * scale, 3), "y_m": round(0.5 * scale, 3), "z_m": 0.0, "type": "tilt_rotor"},
                ])
                tilt_actuators.extend(["Front Tilt Servo", "Rear Tilt Servo"])
                actuator_placements.extend([
                    {"name": "Front Tilt Servo", "x_m": round(0.3 * scale, 3), "y_m": 0.0, "z_m": 0.0, "type": "tilt_servo"},
                    {"name": "Rear Tilt Servo", "x_m": round(-0.3 * scale, 3), "y_m": 0.0, "z_m": 0.0, "type": "tilt_servo"},
                ])

            # Aerodynamic surface servos (elevons)
            actuator_placements.extend([
                {"name": "Left Elevon Servo", "x_m": round(-0.2 * scale, 3), "y_m": round(-0.4 * scale, 3), "z_m": 0.0, "type": "surface"},
                {"name": "Right Elevon Servo", "x_m": round(-0.2 * scale, 3), "y_m": round(0.4 * scale, 3), "z_m": 0.0, "type": "surface"},
            ])
            surf_actuators.extend(["Left Elevon", "Right Elevon"])
            prop_actuators.extend([f"ESC Motor {i+1}" for i in range(tilt_count)])

        elif vtol_type == VTOLType.TAIL_SITTER:
            # 2 motors, diff thrust for hover attitude yaw/roll, large elevons for pitch/yaw
            lift_count = 2
            forward_count = 2
            esc_count = 2
            servo_count = 2  # 2 large elevons

            motor_placements.extend([
                {"name": "Wing Motor L", "x_m": 0.0, "y_m": round(-0.4 * scale, 3), "z_m": 0.0, "type": "dual_use"},
                {"name": "Wing Motor R", "x_m": 0.0, "y_m": round(0.4 * scale, 3), "z_m": 0.0, "type": "dual_use"},
            ])
            actuator_placements.extend([
                {"name": "Left Elevon Servo", "x_m": round(-0.15 * scale, 3), "y_m": round(-0.35 * scale, 3), "z_m": 0.0, "type": "surface"},
                {"name": "Right Elevon Servo", "x_m": round(-0.15 * scale, 3), "y_m": round(0.35 * scale, 3), "z_m": 0.0, "type": "surface"},
            ])
            surf_actuators.extend(["Left Elevon", "Right Elevon"])
            prop_actuators.extend(["ESC Motor L", "ESC Motor R"])

        else:
            # Lift + Cruise fallback (typically 4 lift + 1 cruise)
            # Default fallback for Twin Boom, Box Wing, Hybrid, Vectored Thrust etc.
            lift_count = motor_override or 4
            forward_count = 1
            esc_count = lift_count + forward_count
            servo_count = 4

            # Lift motors
            for i in range(lift_count):
                angle = (2.0 * 3.14159 * i) / lift_count
                r = 0.5 * scale
                mx = r * 0.8 * (-1.0 if i >= lift_count/2 else 1.0)
                my = r * (-0.7 if i % 2 == 0 else 0.7)
                motor_placements.append(
                    {"name": f"Lift Motor {i+1}", "x_m": round(mx, 3), "y_m": round(my, 3), "z_m": 0.0, "type": "lift"}
                )
            # Forward motor
            motor_placements.append(
                {"name": "Cruise Motor", "x_m": round(0.55 * scale, 3), "y_m": 0.0, "z_m": 0.0, "type": "forward"}
            )
            # Control surfaces
            actuator_placements.extend([
                {"name": "Left Aileron", "x_m": 0.0, "y_m": round(-0.6 * scale, 3), "z_m": 0.0, "type": "surface"},
                {"name": "Right Aileron", "x_m": 0.0, "y_m": round(0.6 * scale, 3), "z_m": 0.0, "type": "surface"},
                {"name": "Elevator", "x_m": round(-0.9 * scale, 3), "y_m": 0.0, "z_m": 0.0, "type": "surface"},
                {"name": "Rudder", "x_m": round(-0.9 * scale, 3), "y_m": 0.0, "z_m": 0.15, "type": "surface"},
            ])
            surf_actuators.extend(["Left Aileron", "Right Aileron", "Elevator", "Rudder"])
            prop_actuators.extend([f"ESC Lift {i+1}" for i in range(lift_count)] + ["ESC Cruise"])

        # Control channels count
        control_channels = esc_count + servo_count

        return {
            "lift_motor_count": lift_count,
            "forward_motor_count": forward_count,
            "motor_count": lift_count + (forward_count if vtol_type not in (VTOLType.TILT_ROTOR, VTOLType.TILT_WING, VTOLType.TAIL_SITTER) else 0),
            "motor_placements": motor_placements,
            "actuator_placements": actuator_placements,
            "servo_count": servo_count,
            "esc_count": esc_count,
            "control_channels_count": control_channels,
            "aerodynamic_surface_actuators": surf_actuators,
            "propulsion_actuators": prop_actuators,
            "tilt_actuators": tilt_actuators,
        }
