# Phase 5: AI Aircraft Design Platform Development Guidelines

> **Document Status**: Mandatory Implementation Contract  
> **Target System**: Torq Wings Design Studio Backend  
> **Phase**: Phase 5.0 – Development Guidelines & Engineering Standards  
> **Blueprint Reference**: [`docs/architecture/phase5_ai_aircraft_design_platform.md`](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/docs/architecture/phase5_ai_aircraft_design_platform.md)  
> **Component Reference**: [`docs/architecture/phase5_component_specification.md`](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/docs/architecture/phase5_component_specification.md)  
> **Plan Reference**: [`docs/roadmap/phase5_implementation_plan.md`](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/docs/roadmap/phase5_implementation_plan.md)  
> **Author**: Torq Wings Core Engineering Team  
> **Version**: 1.0.0  

---

## Executive Summary

This document establishes the mandatory software engineering standards, architectural rules, code quality guidelines, and testing protocols for all future Phase 5 development within the Torq Wings AI-powered aircraft engineering backend. Compliance with this contract is mandatory for all human developers and AI coding agents.

---

## 1. Project Philosophy

Torq Wings is engineered to provide explainable, high-precision, physics-grounded aircraft design capabilities. Development prioritizes:

- **Safety & Rigor**: Physics calculations and rule evaluations are deterministic and non-negotiable.
- **Maintainability**: Clean Architecture and strict modularity prevent code decay over time.
- **Explainability**: Every sizing recommendation must expose human-interpretable trade-off rationales.

---

## 2. Coding Standards

- **Python Version**: Python 3.10+ compatible.
- **Code Style**: PEP 8 compliance enforced via automated linters (`flake8`, `black`, `isort`).
- **Line Length**: Maximum 120 characters per line.
- **Encoding**: UTF-8 source code files.

---

## 3. Clean Architecture Rules

Code must strictly conform to Clean Architecture boundaries:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLEAN ARCHITECTURE LAYERS                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Domain Models Layer (Entities & Value Objects)                          │
│     - Pure data structures, no external dependencies                        │
│  2. Domain Services Layer (Sizing & Calculation Engines)                    │
│     - Pure business physics logic, consumes models                          │
│  3. Application Layer (Studio Orchestrators & Router)                       │
│     - Coordinates workflow, manages state, delegates calculations           │
│  4. Infrastructure Layer (Loaders, File I/O, DB Adapters)                   │
│     - Outer boundary, strictly injected into application layer              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Rule**: Dependencies MUST ONLY point inward. Domain models MUST NOT depend on application services or infrastructure adapters.

---

## 4. SOLID Principles

1. **Single Responsibility Principle (SRP)**: Each class must have one, and only one, reason to change (e.g. `MotorSelectionEngine` sizes motors only; it does not compute wing aerodynamics).
2. **Open/Closed Principle (OCP)**: Software entities must be open for extension, but closed for modification.
3. **Liskov Substitution Principle (LSP)**: Subtypes must be completely substitutable for their base types.
4. **Interface Segregation Principle (ISP)**: Clients must not be forced to depend on methods they do not use.
5. **Dependency Inversion Principle (DIP)**: High-level modules must not depend on low-level modules; both must depend on abstractions.

---

## 5. Domain Driven Design Guidelines

- **Bounded Contexts**: Explicit isolation between `Common`, `Advisor`, `DroneStudio`, `FixedWingStudio`, `VTOLStudio`, and `SharedServices`.
- **Aggregate Roots**: `DroneDesign`, `FixedWingDesign`, and `VTOLDesign` act as aggregate roots managing internal component selections and mass properties.
- **Value Objects**: Immutability enforced via dataclasses (`@dataclass(slots=True)`).

---

## 6. Dependency Injection Rules

- **Constructor Injection**: Dependencies MUST be passed via `__init__`.
- **No Direct Instantiation**: High-level services MUST NOT instantiate their collaborators inside `__init__` or methods.
- **Type Annotations**: Inject abstractions or concrete classes using strict Python type hints.

```python
# CORRECT (Dependency Injection)
class RuleEngine:
    def __init__(self, repository: RuleRepository, evaluator: RuleEvaluator) -> None:
        self._repository = repository
        self._evaluator = evaluator

# INCORRECT (Hardcoded Collaborator Instantiation)
class RuleEngine:
    def __init__(self) -> None:
        self._repository = RuleRepository()  # VIOLATION!
        self._evaluator = RuleEvaluator()    # VIOLATION!
```

---

## 7. Folder Organization

All Phase 5 design modules reside strictly under `backend/design/`:

```text
backend/design/
├── models/       # Shared domain models & dataclasses
├── common/       # Requirement validation & baseline context
├── advisor/      # Mission analysis & vehicle category recommendations
├── router/       # Design engine router & studio dispatcher
├── drone/        # Drone (multirotor) design studio & sizing engines
├── fixed_wing/   # Fixed-wing UAV design studio & sizing engines
├── vtol/         # Hybrid VTOL design studio & sizing engines
├── shared/       # Shared physics, weight, aerodynamic, & rule services
└── reports/      # Engineering report generators
```

---

## 8. Module Responsibilities

Each module file must maintain a single, explicitly defined scope:
- `models/`: Dataclasses and enums only. No execution logic.
- `shared/`: Generic physics and rule bridges. No aircraft-category-specific logic.
- `drone/`, `fixed_wing/`, `vtol/`: Isolated sizing logic specific to that aircraft configuration.

---

## 9. Class Design Guidelines

- **Slots Optimization**: Use `@dataclass(slots=True)` for memory efficiency and attribute safety.
- **Encapsulation**: Mark internal helper methods with a leading underscore (`_parse_condition`, `_evaluate_batch`).
- **Immutability**: Avoid mutating state on shared domain models; return new instances when transforming.

---

## 10. Interface Design

- Define clean, minimal public API surfaces for all service classes.
- Use explicit argument names and typed return values for every method.

---

## 11. Domain Model Rules

- Every domain model inherits from `KnowledgeEntity` or uses `@dataclass(slots=True)`.
- Use `field(default_factory=dict)` or `field(default_factory=list)` for mutable defaults.
- Models represent state, not processing workflows.

---

## 12. Error Handling Strategy

- **Custom Exception Hierarchy**: Inherit from `ValueError` or `KeyError` with descriptive base exception classes per module.
- **No Silent Error Swallowing**: Never wrap blocks in `try...except: pass`.
- **Descriptive Error Messages**: Include entity IDs, parameter names, and invalid values in exception strings.

```python
class DesignEngineError(ValueError):
    """Base exception for design platform errors."""
    pass

class InvalidRequirementError(DesignEngineError):
    """Raised when input requirements fail validation."""
    pass
```

---

## 13. Validation Strategy

- Sanitize all external inputs using dedicated validator classes (`RequirementValidator`).
- Validate boundaries at system entry points before passing objects to domain services.

---

## 14. Logging Guidelines

- Use Python's standard `logging` module.
- Log operational events at `INFO` level and diagnostic details at `DEBUG` level.
- Never write `print()` statements in backend production code.

---

## 15. Testing Strategy

- **Framework**: `pytest` for all unit and integration tests.
- **Test File Location**: All tests reside under `tests/unit/` or `tests/integration/`.
- **Code Coverage**: Minimum **95% line coverage** required for all Phase 5 packages.
- **Test Naming**: `test_<module_name>_<feature_description>()`.

---

## 16. Documentation Standards

Every module, class, and method must contain comprehensive Google/NumPy-style docstrings:

```python
"""
Module Title & Overview

Purpose:
    High-level explanation of what this file accomplishes.

Role in Architecture:
    Architectural context and relationships to other subsystems.
"""

class SizingEngine:
    """
    Class summary explanation.

    Attributes:
        attribute_name (type): Description of attribute.
    """

    def size(self, req: ValidatedRequirements) -> SizingResult:
        """
        Method summary.

        Args:
            req (ValidatedRequirements): Input parameters.

        Returns:
            SizingResult: Output parameters.

        Raises:
            SizingError: Explanation of error conditions.
        """
```

---

## 17. Type Hint Requirements

- **100% Strict Type Annotations**: All function signatures, arguments, and return types must be fully annotated.
- **Standard Library Typing**: Use `typing` module abstractions (`list[T]`, `dict[K, V]`, `Type[T]`, `Callable`).
- Enforced via `mypy` strict type checking.

---

## 18. Naming Conventions

- **Classes**: `PascalCase` (e.g. `RequirementValidator`, `DroneDesignStudio`).
- **Functions & Methods**: `snake_case` (e.g. `evaluate_all`, `get_by_category`).
- **Variables & Attributes**: `snake_case` (e.g. `payload_capacity_kg`, `max_current`).
- **Constants**: `UPPER_SNAKE_CASE` (e.g. `GRAVITY_M_S2 = 9.80665`).
- **Enums**: `PascalCase` for enum class, `UPPER_SNAKE_CASE` for members (`RuleSeverity.CRITICAL`).

---

## 19. Performance Considerations

- Time Complexity Targets: $O(1)$ for lookups, $O(V + E)$ for traversals, $O(N)$ for rule evaluation batches.
- Memory: `@dataclass(slots=True)` minimizes object overhead.

---

## 20. Future Extensibility

- Design studios must implement common interface protocols (`BaseDesignStudio`) to allow seamless addition of future studios (Helicopter, Swarm, Amphibious).

---

## 21. AI Coding Agent Instructions

For AI coding assistants implementing Phase 5 code:

1. **NEVER** redesign system architecture or modify finalized architecture blueprints.
2. **NEVER** change public API signatures or contracts without explicit user approval.
3. **NEVER** move responsibilities between engines (e.g., do not add motor sizing into `RequirementValidator`).
4. **NEVER** introduce hidden dependencies or internal collaborator instantiations.
5. **ALWAYS** follow Clean Architecture, SOLID, and strict type hints.
6. **ALWAYS** write corresponding unit tests in `tests/unit/` for every created module.

---

## 22. Code Review Checklist

Before submitting code for Phase 5 integration, verify:

- [ ] All methods have complete type annotations.
- [ ] Dependencies are injected via `__init__`.
- [ ] Custom exceptions are defined and raised appropriately.
- [ ] Complete docstrings present (Purpose, Role, Args, Returns, Raises).
- [ ] No `print()` statements present.
- [ ] `pytest` passes with 100% success rate across all unit tests.

---

## 23. Definition of Done

A Phase 5 task is considered **Done** when:

1. Code is fully implemented according to component specifications.
2. 100% type hinting verified.
3. Module, class, and method docstrings are written.
4. Unit tests are added to `tests/unit/` and passing cleanly.
5. No regressions introduced to existing Phase 1–4 tests.
