"""
Unit tests for Component Selection and Compatibility Frameworks.
"""

import pytest
from backend.design.components import (
    ComponentCategory,
    ComponentSelectionRequest,
    ComponentRepository,
    DefaultComponentSelector,
    ComponentSelectionPipeline,
    CompatibilityStatus,
    CompatibilitySeverity,
    MotorESCCompatibilityRule,
    BatteryESCCompatibilityRule,
    FramePropellerCompatibilityRule,
    CompatibilityRegistry,
    CompatibilityPipeline,
    CompatibilityEngine,
)


def test_component_category_enum():
    """Verify ComponentCategory enum values."""
    assert ComponentCategory.MOTOR == "MOTOR"
    assert ComponentCategory.ESC == "ESC"
    assert ComponentCategory.BATTERY == "BATTERY"
    assert ComponentCategory.PROPELLER == "PROPELLER"
    assert ComponentCategory.FRAME == "FRAME"


def test_component_repository_and_pipeline():
    """Verify ComponentRepository registers items and ComponentSelectionPipeline evaluates requests."""
    repo = ComponentRepository()

    motor1 = {"name": "T-Motor 2207 1750KV", "max_current_a": 35, "weight_g": 32, "brand": "T-Motor"}
    motor2 = {"name": "Generic 2205 2300KV", "max_current_a": 25, "weight_g": 28, "brand": "Generic"}

    repo.register_component(ComponentCategory.MOTOR, motor1)
    repo.register_component(ComponentCategory.MOTOR, motor2)

    assert repo.count(ComponentCategory.MOTOR) == 2

    pipeline = ComponentSelectionPipeline(repository=repo)

    req = ComponentSelectionRequest(
        category=ComponentCategory.MOTOR,
        requirements={"max_current_a": 35},
        constraints={"max_weight_g": 40},
        filters={"brand": "T-Motor"}
    )

    result = pipeline.execute(req)

    assert result.selected_component is not None
    assert result.selected_component.component["name"] == "T-Motor 2207 1750KV"
    assert result.selected_component.score >= 0.80


def test_motor_esc_compatibility_critical():
    """Verify MotorESCCompatibilityRule generates CRITICAL issue when motor current exceeds ESC rating."""
    rule = MotorESCCompatibilityRule()

    components = {
        "motor": {"max_current_a": 45},
        "esc": {"continuous_current_a": 30}
    }

    issues = rule.evaluate(components)
    assert len(issues) == 1
    assert issues[0].severity == CompatibilitySeverity.CRITICAL
    assert "exceeds ESC continuous rating" in issues[0].message


def test_battery_esc_compatibility_critical():
    """Verify BatteryESCCompatibilityRule generates CRITICAL issue when battery cells exceed ESC max rating."""
    rule = BatteryESCCompatibilityRule()

    components = {
        "battery": {"cell_count_s": 6},
        "esc": {"max_cell_count_s": 4}
    }

    issues = rule.evaluate(components)
    assert len(issues) == 1
    assert issues[0].severity == CompatibilitySeverity.CRITICAL


def test_frame_propeller_compatibility_critical():
    """Verify FramePropellerCompatibilityRule generates CRITICAL issue when prop size exceeds frame max clearance."""
    rule = FramePropellerCompatibilityRule()

    components = {
        "frame": {"max_prop_size_inch": 5.0},
        "propeller": {"diameter_inch": 7.0}
    }

    issues = rule.evaluate(components)
    assert len(issues) == 1
    assert issues[0].severity == CompatibilitySeverity.CRITICAL


def test_compatibility_engine_execution():
    """Verify CompatibilityEngine returns COMPATIBLE for safe set and INCOMPATIBLE for unsafe set."""
    engine = CompatibilityEngine()

    safe_components = {
        "motor": {"max_current_a": 25, "kv": 1750, "max_cell_count_s": 6},
        "esc": {"continuous_current_a": 35, "max_cell_count_s": 6},
        "battery": {"cell_count_s": 4},
        "frame": {"max_prop_size_inch": 7.0},
        "propeller": {"diameter_inch": 5.1}
    }

    res_safe = engine.check_compatibility(safe_components)
    assert res_safe.status == CompatibilityStatus.COMPATIBLE
    assert res_safe.score == 1.0

    unsafe_components = {
        "motor": {"max_current_a": 50, "kv": 2500, "max_cell_count_s": 4},
        "esc": {"continuous_current_a": 30, "max_cell_count_s": 4},
        "battery": {"cell_count_s": 6},  # Overvoltage
        "frame": {"max_prop_size_inch": 5.0},
        "propeller": {"diameter_inch": 12.0}  # Overload + Strike
    }

    res_unsafe = engine.check_compatibility(unsafe_components)
    assert res_unsafe.status == CompatibilityStatus.INCOMPATIBLE
    assert res_unsafe.score < 0.50
    assert len(res_unsafe.issues) >= 2
