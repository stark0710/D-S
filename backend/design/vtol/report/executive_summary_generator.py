from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class ExecutiveSummary:
    """
    High level summary block.
    """
    summary_text: str
    key_metrics_table: Dict[str, str]
    overall_compliance_status: str
