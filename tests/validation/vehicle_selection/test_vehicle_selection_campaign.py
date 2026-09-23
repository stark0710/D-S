"""
Pytest Test Suite for Vehicle Selection Engine Post-Refactor & Freeze Campaign.
"""

import os
import pytest
from tests.validation.vehicle_selection.validation_harness import ValidationHarness


def test_post_refactor_campaign_execution_and_freeze():
    """Execute full 700+ case campaign, verify metrics, acceptance rules, and deliverables."""
    harness = ValidationHarness()
    summary = harness.run_campaign()

    # Total suite count check (600 original + 100 stress cases)
    assert summary["total_cases"] == 700
    assert summary["original_600_cases"] == 600
    assert summary["new_stress_cases"] == 100

    # Agreement rate check
    assert summary["overall_agreement_pct"] == 100.0

    # Infeasible trapping check
    assert summary["infeasible_trapped_pct"] == 100.0

    # Critical violations check
    assert summary["critical_violations_count"] == 0

    # Freeze verdict check
    assert summary["final_verdict"] == "A — READY TO FREEZE"

    # Deliverable files existence check
    csv_path = os.path.join(".", "reports", "vehicle_selection_post_refactor_cases.csv")
    report_path = os.path.join(".", "docs", "validation", "VEHICLE_SELECTION_POST_REFACTOR_REPORT.md")
    assert os.path.exists(csv_path)
    assert os.path.exists(report_path)
    assert os.path.getsize(csv_path) > 0
    assert os.path.getsize(report_path) > 0
