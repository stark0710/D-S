"""
Fixed-Wing Manufacturing Quality Assurance Checklist

Purpose:
    Defines the `QualityChecklist` class.

Role in Architecture:
    `QualityChecklist` generates QA inspection checklists for physical validation.
"""

from typing import List


class QualityChecklist:
    """
    Service building quality control testing checklists.
    """

    def generate_checklist(self, inspection_level: str) -> List[str]:
        """
        Compiles quality assurance checks.

        Returns:
            List[str]: QA inspection instructions.
        """
        checklist = [
            "Verify central carbon rod spar slide joints fit without play.",
            "Verify control horns deflections are within tail design bounds.",
            "Verify CG location coordinates match calculated mass results.",
            "Perform propulsion brushless motor thrust test on safety stand.",
        ]

        if inspection_level.lower() == "aerospace":
            checklist.extend([
                "Perform wing structural spar load bending test to 2.5G limits.",
                "Perform telemetry RF range and link margin budget tests.",
            ])

        return checklist
