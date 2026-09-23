from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class CADSection:
    """
    part counts and clearances.
    """
    title: str
    parts_hierarchy_list: List[str]
    clearances_report_summary: str
