from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class Appendix:
    """
    Revision logs and references.
    """
    title: str
    references_list: List[str]
    revision_history_table: List[Dict[str, str]]
