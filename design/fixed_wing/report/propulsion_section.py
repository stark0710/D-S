"""
Fixed-Wing Propulsion Section Compiler

Purpose:
    Defines the propulsion performance content generation.

Role in Architecture:
    `PropulsionSectionCompiler` writes motor, engine, and propeller parameters.
"""

from backend.design.fixed_wing.report.report_requirements import ReportRequirements


class PropulsionSectionCompiler:
    """
    Compiler for the Propulsion chapter.
    """

    def compile(self, requirements: ReportRequirements) -> str:
        prop = requirements.propulsion_result

        thrust_analysis = getattr(prop, "thrust_analysis", None)
        power_analysis = getattr(prop, "power_analysis", None)
        takeoff_analysis = getattr(prop, "takeoff_analysis", None)
        cruise_analysis = getattr(prop, "cruise_analysis", None)

        static_thrust = getattr(thrust_analysis, "estimated_static_thrust_n", None)
        tw_ratio = getattr(thrust_analysis, "thrust_to_weight_ratio", None)
        cruise_thrust = getattr(thrust_analysis, "required_cruise_thrust_n", None)

        cruise_power = getattr(power_analysis, "required_cruise_power_w", None)
        max_power = getattr(power_analysis, "maximum_power_w", None)
        current_draw = getattr(power_analysis, "current_draw_cruise_a", None)

        accel_force = getattr(takeoff_analysis, "acceleration_force_n", None)
        throttle = getattr(cruise_analysis, "throttle_setting_pct", None)

        content = (
            f"# Propulsion Powertrain\n\n"
            f"The sized propulsion system has the following features:\n"
            f"*   **Power Unit**: {prop.selected_motor_or_engine}\n"
            f"*   **Propeller**: {prop.selected_propeller}\n"
        )
        if static_thrust is not None:
            content += f"*   **Static Thrust**: {static_thrust:.2f} N\n"
        if tw_ratio is not None:
            content += f"*   **Thrust-to-Weight Ratio (T/W)**: {tw_ratio:.2f}\n"
        if cruise_thrust is not None:
            content += f"*   **Required Cruise Thrust**: {cruise_thrust:.2f} N\n"
        if cruise_power is not None:
            content += f"*   **Required Cruise Power**: {cruise_power:.1f} W\n"
        if max_power is not None:
            content += f"*   **Maximum Power**: {max_power:.1f} W\n"
        if accel_force is not None:
            content += f"*   **Takeoff Acceleration Force**: {accel_force:.1f} N\n"
        if current_draw is not None:
            content += f"*   **Cruise Current Draw**: {current_draw:.1f} A\n"
        if throttle is not None:
            content += f"*   **Estimated Cruise Throttle**: {throttle:.1f}%\n"

        return content
