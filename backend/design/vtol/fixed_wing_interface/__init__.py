"""
VTOL Fixed-Wing Engineering Interface Package

Exports the authoritative adapter connecting VTOL synthesis to locked Fixed-Wing engines.
"""

from backend.design.vtol.fixed_wing_interface.fixed_wing_adapter import (
    FixedWingEngineeringAdapter,
    FixedWingSubsystemResult,
)

__all__ = [
    "FixedWingEngineeringAdapter",
    "FixedWingSubsystemResult",
]
