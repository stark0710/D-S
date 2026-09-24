"""
Unit tests for DocumentParsingPipeline.
"""

from pathlib import Path
import pytest
from backend.models.repository_document import RepositoryDocument
from backend.models.parsed_document import ParsedDocument
from backend.knowledge.parser.document_reader import DocumentReader
from backend.knowledge.parser.front_matter_parser import FrontMatterParser
from backend.knowledge.parser.markdown_section_parser import MarkdownSectionParser
from backend.knowledge.parser.document_parsing_pipeline import DocumentParsingPipeline


def test_document_parsing_pipeline_orchestration(tmp_path: Path):
    """Verify DocumentParsingPipeline coordinates collaborators and returns ParsedDocument."""
    file_path = tmp_path / "EP-001.md"
    file_content = """---
id: EP-001
name: Payload Weight
unit: kg
---

# Payload Weight

Defines payload mass capacity.

## Specifications

Max 10kg.
"""
    file_path.write_text(file_content, encoding="utf-8")

    doc = RepositoryDocument(
        path=file_path,
        relative_path=Path("EP-001.md"),
        file_name="EP-001.md",
        document_type="engineering_parameter"
    )

    # Instantiate collaborators for dependency injection
    reader = DocumentReader()
    fm_parser = FrontMatterParser()
    sec_parser = MarkdownSectionParser()

    pipeline = DocumentParsingPipeline(
        reader=reader,
        front_matter_parser=fm_parser,
        section_parser=sec_parser
    )

    parsed_doc = pipeline.parse(doc)

    assert isinstance(parsed_doc, ParsedDocument)
    assert parsed_doc.repository_document == doc
    assert parsed_doc.metadata == {"id": "EP-001", "name": "Payload Weight", "unit": "kg"}
    assert len(parsed_doc.sections) == 2
    assert parsed_doc.sections[0].title == "Payload Weight"
    assert parsed_doc.sections[1].title == "Specifications"
    assert parsed_doc.raw_markdown == file_content
