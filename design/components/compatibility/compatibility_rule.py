"""
CompatibilityRule Subsystem

Purpose:
    Defines the abstract `CompatibilityRule` interface and concrete engineering compatibility rules.

Role in Architecture:
    `CompatibilityRule` encapsulates a single engineering compatibility validation check between two or more components
    (e.g., Motor vs ESC, Battery vs ESC, Frame vs Propeller).
"""

from abc import ABC, abstractmethod
from typing import Any
from backend.design.components.compatibility.compatibility_severity import CompatibilitySeverity
from backend.design.components.compatibility.compatibility_issue import CompatibilityIssue


class CompatibilityRule(ABC):
    """
    Abstract interface for component compatibility rules.
    """

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Unique identifier name of the compatibility rule."""
        pass

    @abstractmethod
    def evaluate(self, components: dict[str, Any]) -> list[CompatibilityIssue]:
        """
        Evaluates compatibility across the provided component dictionary.

        Args:
            components (dict[str, Any]): Dictionary of components keyed by component type/name.

        Returns:
            list[CompatibilityIssue]: Identified compatibility issues.
        """
        pass


class MotorESCCompatibilityRule(CompatibilityRule):
    """Validates electrical current compatibility between Motor and ESC."""

    @property
    def rule_name(self) -> str:
        return "MotorESCCompatibilityRule"

    def evaluate(self, components: dict[str, Any]) -> list[CompatibilityIssue]:
        issues: list[CompatibilityIssue] = []
        motor = components.get("motor")
        esc = components.get("esc")

        if not motor or not esc:
            return issues

        motor_current = float(motor.get("max_current_a", 0))
        esc_current = float(esc.get("continuous_current_a", 0))

        if motor_current > 0 and esc_current > 0:
            if motor_current > esc_current:
                issues.append(
                    CompatibilityIssue(
                        rule_name=self.rule_name,
                        severity=CompatibilitySeverity.CRITICAL,
                        message=f"Motor peak current ({motor_current}A) exceeds ESC continuous rating ({esc_current}A).",
                        recommendation="Select an ESC rated for higher continuous current or choose a lower-current motor."
                    )
                )
            elif motor_current > 0.85 * esc_current:
                issues.append(
                    CompatibilityIssue(
                        rule_name=self.rule_name,
                        severity=CompatibilitySeverity.WARNING,
                        message=f"Motor peak current ({motor_current}A) operates close to ESC current limit ({esc_current}A).",
                        recommendation="Consider an ESC with higher thermal headroom for sustained full-throttle operations."
                    )
                )

        return issues


class MotorPropellerCompatibilityRule(CompatibilityRule):
    """Validates motor KV rating compatibility with propeller diameter."""

    @property
    def rule_name(self) -> str:
        return "MotorPropellerCompatibilityRule"

    def evaluate(self, components: dict[str, Any]) -> list[CompatibilityIssue]:
        issues: list[CompatibilityIssue] = []
        motor = components.get("motor")
        prop = components.get("propeller")

        if not motor or not prop:
            return issues

        kv = float(motor.get("kv", 0))
        diameter_inch = float(prop.get("diameter_inch", 0))

        if kv > 2000 and diameter_inch > 10.0:
            issues.append(
                CompatibilityIssue(
                    rule_name=self.rule_name,
                    severity=CompatibilitySeverity.CRITICAL,
                    message=f"High KV motor ({kv} KV) combined with large propeller ({diameter_inch}\") causes extreme torque overload.",
                    recommendation="Use a lower KV motor (< 1000 KV) for large propellers or reduce propeller size."
                )
            )

        return issues


class BatteryESCCompatibilityRule(CompatibilityRule):
    """Validates battery cell count / voltage compatibility with ESC maximum voltage rating."""

    @property
    def rule_name(self) -> str:
        return "BatteryESCCompatibilityRule"

    def evaluate(self, components: dict[str, Any]) -> list[CompatibilityIssue]:
        issues: list[CompatibilityIssue] = []
        battery = components.get("battery")
        esc = components.get("esc")

        if not battery or not esc:
            return issues

        cell_count = int(battery.get("cell_count_s", 0))
        esc_max_s = int(esc.get("max_cell_count_s", 0))

        if cell_count > 0 and esc_max_s > 0:
            if cell_count > esc_max_s:
                issues.append(
                    CompatibilityIssue(
                        rule_name=self.rule_name,
                        severity=CompatibilitySeverity.CRITICAL,
                        message=f"Battery voltage ({cell_count}S) exceeds ESC max voltage rating ({esc_max_s}S). Risk of overvoltage damage.",
                        recommendation="Select an ESC rated for higher cell count or reduce battery cell count."
                    )
                )

        return issues


class BatteryMotorCompatibilityRule(CompatibilityRule):
    """Validates battery voltage compatibility with motor maximum voltage rating."""

    @property
    def rule_name(self) -> str:
        return "BatteryMotorCompatibilityRule"

    def evaluate(self, components: dict[str, Any]) -> list[CompatibilityIssue]:
        issues: list[CompatibilityIssue] = []
        battery = components.get("battery")
        motor = components.get("motor")

        if not battery or not motor:
            return issues

        cell_count = int(battery.get("cell_count_s", 0))
        motor_max_s = int(motor.get("max_cell_count_s", 0))

        if cell_count > 0 and motor_max_s > 0:
            if cell_count > motor_max_s:
                issues.append(
                    CompatibilityIssue(
                        rule_name=self.rule_name,
                        severity=CompatibilitySeverity.CRITICAL,
                        message=f"Battery voltage ({cell_count}S) exceeds motor max voltage rating ({motor_max_s}S).",
                        recommendation="Select a motor rated for higher operating voltage or reduce battery cell count."
                    )
                )

        return issues


class FramePropellerCompatibilityRule(CompatibilityRule):
    """Validates propeller diameter clearance relative to frame maximum propeller size."""

    @property
    def rule_name(self) -> str:
        return "FramePropellerCompatibilityRule"

    def evaluate(self, components: dict[str, Any]) -> list[CompatibilityIssue]:
        issues: list[CompatibilityIssue] = []
        frame = components.get("frame")
        prop = components.get("propeller")

        if not frame or not prop:
            return issues

        prop_diameter = float(prop.get("diameter_inch", 0))
        max_frame_prop = float(frame.get("max_prop_size_inch", 0))

        if prop_diameter > 0 and max_frame_prop > 0:
            if prop_diameter > max_frame_prop:
                issues.append(
                    CompatibilityIssue(
                        rule_name=self.rule_name,
                        severity=CompatibilitySeverity.CRITICAL,
                        message=f"Propeller diameter ({prop_diameter}\") exceeds frame max propeller clearance ({max_frame_prop}\"). Risk of prop strike.",
                        recommendation="Select a larger airframe or use smaller diameter propellers."
                    )
                )

        return issues
