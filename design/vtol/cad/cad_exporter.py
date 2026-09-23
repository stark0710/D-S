from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class ExportedFile:
    """
    Output CAD export files record.
    """
    file_format: str  # STEP, STL, DXF, IGES
    file_path: str
    file_size_bytes: int
    is_valid: bool

class CADExporter:
    """
    Generates structured export CAD output streams.
    """
    @staticmethod
    def export_assembly(format_name: str, base_path: str) -> List[ExportedFile]:
        # Formulate export files
        formats = [format_name] if format_name else ["STEP", "STL", "IGES"]
        outputs = []
        for fmt in formats:
            ext = f".{fmt.lower()}" if fmt != "Parasolid" else ".x_t"
            outputs.append(ExportedFile(
                file_format=fmt,
                file_path=f"{base_path}{ext}",
                file_size_bytes=1450000 if fmt == "STEP" else 650000,
                is_valid=True
            ))
        return outputs
