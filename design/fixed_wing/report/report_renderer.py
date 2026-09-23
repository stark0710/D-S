"""
Fixed-Wing Report Renderer Subsystem

Purpose:
    Defines the `ReportRenderer` class that compiles all chapter strings into a single document body.

Role in Architecture:
    `ReportRenderer` concatenates section markdown texts and wraps them with a document header.
"""

from typing import Dict, List
from datetime import datetime


class ReportRenderer:
    """
    Service rendering compiled section text into a unified report document.
    """

    def render_full_document(
        self,
        sections: Dict[str, str],
        author: str,
        title: str,
    ) -> str:
        """
        Concatenates all section texts into a unified document string.

        Returns:
            str: Full document content string.
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        header = (
            f"---\n"
            f"title: \"{title}\"\n"
            f"author: \"{author}\"\n"
            f"date: \"{timestamp}\"\n"
            f"---\n\n"
        )

        body = ""
        for section_name, content in sections.items():
            body += content + "\n\n---\n\n"

        return header + body
