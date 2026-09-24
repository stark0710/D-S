"""
FrontMatterParser Subsystem

Purpose:
    Defines the `FrontMatterParser` class responsible for extracting and parsing YAML front matter
    from raw Markdown text using PyYAML (`yaml.safe_load`) with a fallback scalar parser.

Role in Architecture:
    `FrontMatterParser` serves as the initial metadata extraction layer for the Markdown Parsing Engine.
    It separates YAML metadata parsing from Markdown body and heading extraction.
"""

from typing import Any

try:
    import yaml
    HAS_PYYAML = True
except ImportError:
    HAS_PYYAML = False


class FrontMatterParseError(ValueError):
    """Base exception class for front matter parsing failures."""
    pass


class UnclosedFrontMatterError(FrontMatterParseError):
    """Raised when an opening '---' delimiter exists without a matching closing '---'."""
    pass


class MalformedYAMLError(FrontMatterParseError):
    """Raised when the extracted front matter YAML block cannot be parsed."""
    pass


class FrontMatterParser:
    """
    Parser for extracting and deserializing YAML front matter from Markdown documents.

    Responsibilities:
        - Detect YAML front matter delimited by opening and closing `---` markers.
        - Safely parse YAML content into a Python dictionary (`dict[str, Any]`).
        - Return an empty dictionary `{}` if no front matter block is present.
        - Raise descriptive exceptions (`UnclosedFrontMatterError`, `MalformedYAMLError`) on failure.

    Limitations:
        - Front Matter Only: Does not parse Markdown headings, body text, or section blocks.
        - Pure Data Deserializer: Free of domain entity rules or engineering calculations.
    """

    def parse(self, markdown_text: str) -> dict[str, Any]:
        """
        Parses YAML front matter from a Markdown string.

        Args:
            markdown_text (str): Raw Markdown string content.

        Returns:
            dict[str, Any]: Extracted metadata dictionary, or `{}` if no front matter exists.

        Raises:
            UnclosedFrontMatterError: If an opening '---' exists without a closing '---'.
            MalformedYAMLError: If YAML fails to parse or is malformed.
        """
        if not markdown_text:
            return {}

        stripped_text = markdown_text.lstrip()

        # Front matter must start with '---'
        if not stripped_text.startswith("---"):
            return {}

        # Remove the leading '---' marker
        content_after_first_delimiter = stripped_text[3:]

        # Search for closing '---'
        end_delimiter_index = content_after_first_delimiter.find("\n---")
        if end_delimiter_index == -1:
            if content_after_first_delimiter.strip() == "---":
                return {}
            raise UnclosedFrontMatterError(
                "Unclosed YAML front matter block: opening '---' found but no matching closing '---' delimiter."
            )

        yaml_content = content_after_first_delimiter[:end_delimiter_index].strip()

        if not yaml_content:
            return {}

        if HAS_PYYAML:
            try:
                parsed_data = yaml.safe_load(yaml_content)
            except yaml.YAMLError as ye:
                raise MalformedYAMLError(
                    f"Failed to parse YAML front matter block: {ye}"
                ) from ye
        else:
            parsed_data = self._fallback_parse_yaml(yaml_content)

        if parsed_data is None:
            return {}

        if not isinstance(parsed_data, dict):
            raise MalformedYAMLError(
                f"YAML front matter must parse to a dictionary, but got '{type(parsed_data).__name__}'."
            )

        return parsed_data

    def _fallback_parse_yaml(self, yaml_content: str) -> dict[str, Any]:
        """Fallback lightweight YAML key-value and list parser when PyYAML is unavailable."""
        result: dict[str, Any] = {}
        current_list_key: str | None = None

        for line in yaml_content.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue

            if line_str.startswith("- ") and current_list_key:
                item_val = line_str[2:].strip().strip('"').strip("'")
                item_parsed = self._parse_scalar_value(item_val)
                result[current_list_key].append(item_parsed)
                continue

            if ":" in line_str:
                parts = line_str.split(":", 1)
                key = parts[0].strip()
                val_str = parts[1].strip()

                if not val_str:
                    current_list_key = key
                    result[key] = []
                else:
                    current_list_key = None
                    clean_val = val_str.strip('"').strip("'")
                    result[key] = self._parse_scalar_value(clean_val)
            else:
                raise MalformedYAMLError(f"Malformed YAML line: '{line_str}'")

        return result

    @staticmethod
    def _parse_scalar_value(val: str) -> Any:
        """Parses scalar strings into int, float, bool, or string."""
        if val.lower() == "true":
            return True
        if val.lower() == "false":
            return False
        try:
            return int(val)
        except ValueError:
            pass
        try:
            return float(val)
        except ValueError:
            pass
        return val
