# Knowledge Layer

## Purpose

The Knowledge Layer serves as the single software gateway and interface between the Markdown-based Engineering Knowledge Base (EKB) and the backend codebase.

It is responsible for exposing structured engineering parameters, mission domains, libraries, and their relationships to downstream systems without implementing business rules or engineering reasoning itself.

Downstream backend components, including:
- Future Rule Engines
- Recommendation Engines
- AI Modules
- Sizing Engines
- Optimization Engines
- CAD Generators

shall consume engineering knowledge exclusively through this layer.

---

## Architectural Principles

1. **Passive Gateway**: The Knowledge Layer is responsible for discovery, parsing, and structuring EKB documentation. It shall **never** perform engineering reasoning, recommendation logic, recommendations, sizing, optimization, or AI operations.
2. **Exclusivity**: EKB markdown files must not be loaded or parsed directly by other backend subsystems. All access must proceed through this package.
3. **Immutability**: Loaded EKB constructs are treated as read-only objects reflecting the state of the knowledge repository.

---

## Module Overview

The Knowledge Layer is organized into the following modules:

- **`loader/`**: Locates and loads EKB markdown documents. Responsible for repository traversal, document discovery, and raw file loading. No document parsing occurs here.
- **`parser/`**: Converts Markdown documents into structured Python objects. Responsible for section extraction, metadata/EPDS table parsing, constraints parsing, and relationships extraction. Performs no engineering validation or reasoning.
- **`resolver/`**: Resolves EKB structural relationships (e.g., matching a Mission Category to its associated Engineering Parameter IDs, and tracing them back to their respective Parameter Documents). Contains no recommendation logic.
- **`graph/`**: Constructs an in-memory Engineering Knowledge Graph mapping out the nodes (Missions, Parameters, Libraries) and edges (Dependencies, Relationships) discovered in the repository. Does not perform inference or graph reasoning.
- **`cache/`**: (Placeholder) Handles caching of parsed parameters, files, and graphs to optimize traversal times.
- **`schemas/`**: (Placeholder) Houses Pydantic schemas, data models, and Type definitions representing the parsed EKB components.
