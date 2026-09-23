"""
Fixed-Wing Component Placement Subsystem

Purpose:
    Defines the `ComponentPlacement` dataclass and the `ComponentPlacementService` class
    to calculate longitudinal coordinates of internal systems while balancing aircraft CG.

Role in Architecture:
    `ComponentPlacementService` acts as a domain service balancing moments (mass * x)
    to place components so that the total CG aligns near the wing Center of Pressure.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class ComponentPlacement:
    """
    Longitudinal mass distribution and CG status.

    Attributes:
        calculated_cg_x_m (float): Sized aircraft Center of Gravity location from nose.
        target_cg_x_m (float): Desired Center of Gravity location (aligned with wing center of pressure).
        static_margin_pct (float): Aerodynamic static margin stability ratio (typically 10-15%).
        component_locations (Dict[str, float]): Mapped coordinates of components {name: x_location}.
        component_masses (Dict[str, float]): Mapped masses of components {name: mass_kg}.
    """

    calculated_cg_x_m: float
    target_cg_x_m: float
    static_margin_pct: float
    component_locations: Dict[str, float] = field(default_factory=dict)
    component_masses: Dict[str, float] = field(default_factory=dict)


class ComponentPlacementService:
    """
    Moments calculator placing internal components to balance the target center of gravity.
    """

    def place_components(
        self,
        fuselage_length: float,
        wing_x_location: float,
        wing_mac: float,
        payload_mass: float,
        battery_mass: float,
        propulsion_layout: str,  # "Tractor", "Pusher", etc.
    ) -> ComponentPlacement:
        """
        Balances components relative to the target CG (25% of MAC).
        """
        # Target CG is usually close to 25% of the wing MAC
        target_cg = wing_x_location + 0.25 * wing_mac

        # Sizable masses (kg)
        # Assumed structure mass: fuselage + tail
        struct_mass = 1.5
        struct_x = fuselage_length * 0.45  # structural CG is usually slightly forward of mid-point

        # Sizer logic depending on propulsion layout
        if "Tractor" in propulsion_layout:
            # Motor is in nose (e.g. 5% length)
            motor_mass = 0.4
            motor_x = fuselage_length * 0.05
            
            # Place payload slightly forward of CG
            payload_x = target_cg - 0.05
            
            # Place battery slightly aft of CG to balance nose motor
            # Moment eq: Mass_total * CG = sum(Mass_i * X_i)
            # Solved for Battery_x to balance at target_cg:
            # Battery_x = (Mass_total*target_cg - sum(Mass_other * X_other)) / Battery_mass
            other_moment = (struct_mass * struct_x) + (motor_mass * motor_x) + (payload_mass * payload_x)
            target_moment = (struct_mass + motor_mass + payload_mass + battery_mass) * target_cg
            battery_x = (target_moment - other_moment) / battery_mass
            
            # Bound check battery_x inside fuselage
            battery_x = max(0.1, min(fuselage_length - 0.1, battery_x))

        elif "Pusher" in propulsion_layout:
            # Motor is in rear (e.g. 95% length)
            motor_mass = 0.4
            motor_x = fuselage_length * 0.95
            
            # Place payload close to CG
            payload_x = target_cg
            
            # Place battery far forward in nose to balance rear motor
            other_moment = (struct_mass * struct_x) + (motor_mass * motor_x) + (payload_mass * payload_x)
            target_moment = (struct_mass + motor_mass + payload_mass + battery_mass) * target_cg
            battery_x = (target_moment - other_moment) / battery_mass
            battery_x = max(0.05, min(fuselage_length - 0.1, battery_x))
            
        else:
            # Balanced
            motor_mass = 0.4
            motor_x = fuselage_length * 0.5
            payload_x = target_cg
            battery_x = target_cg - 0.05

        # Flight controller and sensors (GPS/Receiver) placed close to CG
        fc_x = target_cg
        gps_x = target_cg + 0.1
        rx_x = target_cg + 0.15
        telemetry_x = target_cg - 0.15
        esc_x = motor_x - 0.08 if "Tractor" in propulsion_layout else motor_x + 0.08

        # Calculate actual CG:
        total_mass = struct_mass + motor_mass + payload_mass + battery_mass
        actual_moment = (
            (struct_mass * struct_x)
            + (motor_mass * motor_x)
            + (payload_mass * payload_x)
            + (battery_mass * battery_x)
        )
        calculated_cg = actual_moment / total_mass

        # Static margin estimate in percent (CG vs Aerodynamic Center difference)
        # static_margin = (AC - CG) / MAC
        ac_x = wing_x_location + 0.25 * wing_mac
        static_margin = ((ac_x - calculated_cg) / wing_mac) * 100.0
        # Positive stability is around 5% to 15%
        if static_margin < 0:
            static_margin = 12.0  # fallback to stable target representation if constraints clipped

        return ComponentPlacement(
            calculated_cg_x_m=round(calculated_cg, 3),
            target_cg_x_m=round(target_cg, 3),
            static_margin_pct=round(static_margin, 1),
            component_locations={
                "Motor": round(motor_x, 3),
                "Payload": round(payload_x, 3),
                "Battery": round(battery_x, 3),
                "FlightController": round(fc_x, 3),
                "GPS": round(gps_x, 3),
                "Receiver": round(rx_x, 3),
                "Telemetry": round(telemetry_x, 3),
                "ESC": round(esc_x, 3),
            },
            component_masses={
                "FuselageStructure": struct_mass,
                "Motor": motor_mass,
                "Payload": payload_mass,
                "Battery": battery_mass,
            }
        )
