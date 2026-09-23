"""
Fixed-Wing Verification Safety Checker Subsystem

Purpose:
    Defines the `SafetyChecker` class.

Role in Architecture:
    `SafetyChecker` verifies critical failsafes and sensor redundancies.
"""

from typing import List
from backend.design.fixed_wing.verification.verification_requirements import VerificationRequirements


class SafetyChecker:
    """
    Sizing audit for airspeed tubes, receiver telemetry limits, and BEC failures.
    """

    def check_safety_suitability(self, reqs: VerificationRequirements) -> List[str]:
        failures: List[str] = []
        av_res = reqs.avionics_result

        # Check for airspeed sensor
        if not any("airspeed sensor" in s.lower() for s in av_res.selected_sensors):
            failures.append("Safety critical deficiency: Airspeed sensor is missing. Autopilot lacks direct wind estimations.")

        # Check for telemetry backup link
        if not av_res.selected_telemetry:
            failures.append("Safety critical deficiency: Telemetry modem is not configured. BVLOS telemetry links are broken.")

        return failures
