"""
Fixed-Wing Avionics Validator Subsystem

Purpose:
    Defines the `AvionicsValidator` class to validate autopilot, navigation, and telemetry setups.

Role in Architecture:
    `AvionicsValidator` enforces checks for airspeed sensors presence (critical for fixed-wing),
    GNSS redundancy counts, communications ranges, and flight controller UART/Ethernet connections.
"""

from typing import List
from backend.design.fixed_wing.avionics.avionics_requirements import AvionicsRequirements, GNSSConfiguration
from backend.design.fixed_wing.avionics.avionics_constraints import AvionicsConstraints
from backend.design.fixed_wing.avionics.navigation_analysis import NavigationAnalysis
from backend.design.fixed_wing.avionics.communication_analysis import CommunicationAnalysis
from backend.design.fixed_wing.avionics.power_analysis import PowerAnalysis


class AvionicsValidationError(ValueError):
    """Exception raised when sized avionics parameters fail safety constraints."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class AvionicsValidator:
    """
    Validator enforcing safety and connectivity guidelines on autopilot payloads.
    """

    def validate(
        self,
        requirements: AvionicsRequirements,
        constraints: AvionicsConstraints,
        selected_fc: str,
        selected_sensors: List[str],
        selected_comp: str,
        nav_anal: NavigationAnalysis,
        comm_anal: CommunicationAnalysis,
        pow_anal: PowerAnalysis,
    ) -> List[str]:
        """
        Validates the sized avionics system.

        Args:
            requirements (AvionicsRequirements): Sizing requirements context.
            constraints (AvionicsConstraints): Sizing bounds.
            selected_fc (str): Sized flight controller name.
            selected_sensors (List[str]): Sized sensors names list.
            selected_comp (str): Sized companion computer name.
            nav_anal (NavigationAnalysis): Navigation stability.
            comm_anal (CommunicationAnalysis): Radio link.
            pow_anal (PowerAnalysis): Power loads.

        Returns:
            List[str]: A list of non-fatal warnings (compromises).

        Raises:
            AvionicsValidationError: If critical constraints are violated.
        """
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Critical Fixed-Wing Rule: MUST have an Airspeed sensor to prevent aerodynamic stall!
        has_airspeed = False
        for sensor in selected_sensors:
            if "Airspeed" in sensor:
                has_airspeed = True
                break

        if not has_airspeed:
            errors.append(
                "Critical safety violation: Fixed-wing aircraft require an active Airspeed sensor "
                "to prevent aerodynamic stall during autonomous flights."
            )

        # 2. GNSS redundancy check
        if nav_anal.redundancy_level < constraints.required_gnss_count:
            errors.append(
                f"Sized GNSS receiver count ({nav_anal.redundancy_level}) is below the required "
                f"redundancy level constraint ({constraints.required_gnss_count})."
            )

        # 3. Telemetry communication range
        if comm_anal.max_range_km < constraints.min_comms_range_km:
            errors.append(
                f"Telemetry data link range ({comm_anal.max_range_km:.2f} km) is below the "
                f"minimum required communication range constraint ({constraints.min_comms_range_km:.2f} km)."
            )

        # 4. Companion computer ethernet connection warning
        if "Jetson" in selected_comp or "Intel NUC" in selected_comp:
            if "Matek" in selected_fc:
                warnings.append(
                    f"Flight controller '{selected_fc}' lacks high-speed Ethernet interfaces. "
                    f"Connection to companion computer '{selected_comp}' is restricted to UART serial, "
                    "which limits high-bandwidth video data streaming."
                )

        # 5. Volumetric power heating check
        if pow_anal.continuous_power_w > 15.0:
            warnings.append(
                f"High avionics power draw ({pow_anal.continuous_power_w:.1f} W). "
                "Ensure the main BEC has an external heat-sink to prevent thermal shutdown in closed bays."
            )

        if errors:
            raise AvionicsValidationError(errors)

        return warnings
