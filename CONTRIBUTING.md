# Contributing Guidelines

Thank you for contributing to **Torq Wings Design Studio V3**.

To ensure that the platform maintains commercial-grade software quality, explainable engineering reasoning, and strict domain boundaries, all contributions must follow the guidelines outlined below.

## Overview

Torq Wings Design Studio V3 is an engineering-first aerospace software platform. Engineering correctness, physical traceability, and physical validation take precedence over presentation or convenience.

Before contributing, please review [PROJECT.md](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/PROJECT.md) and [ARCHITECTURE.md](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/ARCHITECTURE.md).

## Development Workflow

1. **Branching Strategy**: Create feature or bugfix branches off the `main` branch using descriptive names (`feature/wing-drag-polar`, `fix/motor-thermal-limit`).
2. **Local Verification**: Ensure all existing tests pass and any new engineering logic is covered by unit/integration tests before submitting a pull request.
3. **Pull Request Submission**: Describe the rationale, physical assumptions, and verification evidence supporting your changes.

## Coding Standards

All code written in this repository must comply with the following standards:

- **Python Version**: Python 3.10+
- **Code Style**: Follow PEP 8 guidelines.
- **Type Annotations**: Use explicit Python type hints (`typing.List`, `typing.Dict`, `Optional`, `Any`) on all function signatures, methods, and dataclass fields.
- **Docstrings**: Provide Google-style docstrings for all public classes, methods, modules, and engines, documenting parameters, return types, and physical units (e.g., `kg`, `N`, `m`, `W`, `V`, `km/h`).
- **SOLID Principles**: Keep sizers, selectors, validators, and analyzers decoupled with clear interfaces.
- **Engineering Traceability**: Avoid hardcoding unexplained physical magic numbers. References and engineering formulas must be linked to source references or explicit assumptions.

## Documentation Standards

- **Synchronized Documentation**: Any change to engine behavior, requirement models, or subsystem capabilities must be reflected in the corresponding documentation under `docs/` and root specification files.
- **Markdown Formatting**: Use clear, standard GitHub-Flavored Markdown formatting with appropriate heading hierarchies and table structures.

## Testing Standards

Testing is a MANDATORY requirement for all code contributions:

- **Framework**: All tests are written using `pytest`.
- **Test Placement**:
  - Unit tests: `tests/design/*/`
  - Pipeline integration tests: `tests/design/*/pipeline/`
  - Validation rule tests: `tests/validation/`
- **Execution**: Run tests locally using:
  ```bash
  pytest
  ```
- **Coverage**: Ensure that new sizers or calculation routines include test assertions verifying both standard operational inputs and boundary error handling (e.g., negative payload, zero endurance).

## Review Process

All pull requests undergo peer review evaluating:

1. **Engineering Accuracy**: Verification that physical equations, unit conversions, and aerodynamic/electrical assumptions are correct.
2. **Architecture Alignment**: Compliance with domain boundaries (e.g., keeping UI/API logic separate from core engineering engines).
3. **Test & Validation Evidence**: Automated test passes and clear validation logs.
