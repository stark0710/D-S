from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class AssemblyStep:
    """
    A single step in the build sequence.
    """
    step_number: int
    operation_title: str
    instructions: str
    estimated_time_min: float
    required_tools: List[str]

@dataclass(slots=True)
class AssemblyInstructions:
    """
    Full list of assembly steps.
    """
    steps: List[AssemblyStep]
    estimated_assembly_time_hours: float
    metadata: Dict[str, Any] = field(default_factory=dict)
