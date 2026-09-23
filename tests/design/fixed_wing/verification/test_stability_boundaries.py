import pytest
from unittest.mock import MagicMock
from backend.design.fixed_wing.verification.stability_checker import StabilityChecker
from backend.design.fixed_wing.mass_properties.mass_result import MassResult

@pytest.mark.parametrize("margin, expected_fail", [
    (0.049, True),   # 4.9% -> unstable, must fail
    (0.050, False),  # 5.0% -> min boundary, must pass
    (0.150, False),  # 15.0% -> normal region, must pass
    (0.250, False),  # 25.0% -> max boundary, must pass
    (0.251, True),   # 25.1% -> excessive stability, must fail
    (1.390, True),   # 139.0% -> nominal Phase 3 error, must fail
])
def test_stability_margin_boundaries(margin, expected_fail):
    """Verify that static margin boundaries are correctly failed or passed."""
    checker = StabilityChecker()
    
    # Mock MassResult with specific static margin
    mock_mass_res = MagicMock(spec=MassResult)
    mock_mass_res.static_margin = margin
    
    mock_reqs = MagicMock()
    mock_reqs.mass_result = mock_mass_res
    
    failures = checker.check_stability_suitability(mock_reqs)
    
    has_failures = len(failures) > 0
    assert has_failures == expected_fail, f"Failed for margin={margin*100:.1f}%. Expected fail={expected_fail}, got={has_failures} (failures: {failures})"
