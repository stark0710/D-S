from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class FixtureItem:
    """
    assembly jigs or alignment templates.
    """
    fixture_id: str
    description: str
    coordinates_offset_mm: List[float]
    cost_usd: float

@dataclass(slots=True)
class FixturePlan:
    """
    Fixture jigs listing.
    """
    fixtures: List[FixtureItem]
    total_fixture_cost_usd: float
    metadata: Dict[str, Any] = field(default_factory=dict)
