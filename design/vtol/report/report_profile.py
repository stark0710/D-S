"""
VTOL Report Profile parameters
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class ReportProfile:
    """
    Document formatting, page margins, fonts, and header styling.
    """
    page_margin_cm: float = 2.5
    font_family: str = "Inter"
    header_logo_url: str = "assets/logo.png"
    primary_color_hex: str = "#0F172A"  # Slate dark
    metadata: Dict[str, Any] = field(default_factory=dict)
