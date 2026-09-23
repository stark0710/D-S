from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class ExportedDocument:
    """
    Generated file path metrics.
    """
    format_type: str  # PDF, HTML, Markdown
    file_path: str
    page_count: int
    file_size_bytes: int

class ReportExporter:
    """
    Generates multi-format file sheets.
    """
    @staticmethod
    def export_document(format_name: str, base_path: str) -> List[ExportedDocument]:
        formats = [format_name] if format_name else ["PDF", "HTML", "Markdown"]
        docs = []
        for fmt in formats:
            ext = f".{fmt.lower()}"
            docs.append(ExportedDocument(
                format_type=fmt,
                file_path=f"{base_path}{ext}",
                page_count=24 if fmt == "PDF" else 1,
                file_size_bytes=420000 if fmt == "PDF" else 95000
            ))
        return docs
