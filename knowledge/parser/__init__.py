"""
Parser package for Torq Wings Design Studio.
"""

from backend.knowledge.parser.parser import Parser
from backend.knowledge.parser.markdown_parser import MarkdownParser, UnsupportedDocumentTypeError
from backend.knowledge.parser.document_reader import (
    DocumentReader,
    DocumentReadError,
    DocumentNotFoundError,
    DocumentAccessError,
    EmptyDocumentError,
)
from backend.knowledge.parser.front_matter_parser import (
    FrontMatterParser,
    FrontMatterParseError,
    UnclosedFrontMatterError,
    MalformedYAMLError,
)
from backend.knowledge.parser.markdown_section_parser import MarkdownSectionParser
from backend.knowledge.parser.document_parsing_pipeline import DocumentParsingPipeline

__all__ = [
    "Parser",
    "MarkdownParser",
    "UnsupportedDocumentTypeError",
    "DocumentReader",
    "DocumentReadError",
    "DocumentNotFoundError",
    "DocumentAccessError",
    "EmptyDocumentError",
    "FrontMatterParser",
    "FrontMatterParseError",
    "UnclosedFrontMatterError",
    "MalformedYAMLError",
    "MarkdownSectionParser",
    "DocumentParsingPipeline",
]
