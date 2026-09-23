# Torq Wings Design Studio V3 Roadmap

## Purpose

This document is the official development roadmap for Torq Wings Design Studio V3. It defines the approved phase sequence for building the platform from architecture foundation through final release.

The roadmap follows the approved Torq Wings V3 architecture and does not redefine system architecture, implementation details, or engineering methods.

## Roadmap Principles

- Preserve the approved architecture.
- Build engineering foundations before automation.
- Document assumptions before implementation.
- Keep phases modular and independently reviewable.
- Maintain traceability from mission definition to final UAV design.
- Treat validation, explainability, and reporting as core engineering outputs.

## Current Implementation Status Summary

| Phase | Phase Name | Status | Key Implemented Modules / Artifacts |
| :--- | :--- | :--- | :--- |
| **Fixed-Wing Baseline** | Fixed-Wing Sizing Pipeline | **LOCKED & VERIFIED** | 13-stage multidisciplinary sizing loop (`FixedWingDesignPipeline`, 233 passed, 1 known baseline failure) |
| **VTOL Phase 1** | Foundation & Architecture | **LOCKED & VERIFIED** | Typed VTOL requirements, Lift+Cruise (QuadPlane), mission profile, Fixed-Wing reuse adapter |
| **VTOL Phase 2** | Hover Performance | **LOCKED & VERIFIED** | Momentum theory, blade element lift sizing, rotor download factor, ground effect |
| **VTOL Phase 3** | Transition Flight Dynamics | **LOCKED & VERIFIED** | Transition speed $V_{trans} \ge 1.2 V_{stall}$, pitch acceleration, corridor scheduling, energy modeling |
| **VTOL Phase 4** | Energy Ledger & Battery Sizing| **LOCKED & VERIFIED** | Mission energy ledger (hover/transition/cruise/avionics), 20% reserve constraint, C-rating checks |
| **VTOL Phase 5** | Mass, CG & MTOW Closure | **LOCKED & VERIFIED** | Multidisciplinary iterative convergence ($\text{tol}=0.015$, $\text{relax}=0.70$), 3D component CG balance |
| **VTOL Phase 6** | Stability & Control Sizing | **LOCKED & VERIFIED** | Inverted V-tail projection, volume coefficients, ruddervator mixing, $5\% \le SM \le 25\%$ |
| **VTOL Phase 7** | Deterministic Optimization | **LOCKED & VERIFIED** | Multi-objective pareto-optimal trade studies, deterministic candidate scoring |
| **VTOL Phase 8** | Commercial Hardware & BOM | **LOCKED & VERIFIED** | Catalog matching, commercial motor/prop/ESC/battery specifications, itemized BOM |
| **VTOL Phase 9** | System Integration | **LOCKED & VERIFIED** | Bus topology (Paths A–G), I/O allocation, 10 mission states, 13 failure modes analysis |
| **VTOL Phase 10** | Flight Control Configuration | **LOCKED & VERIFIED** | Holybro Pixhawk 6X integration, ArduPlane QuadPlane parameters, mixer mapping |
| **VTOL Phase 11** | Physical Ground Verification | **LOCKED & VERIFIED** | 18 bench procedures, props-off commissioning, electrical bus validation (No flight claimed) |
| **VTOL Phase 12/12A**| Flight Test Framework | **FRAMEWORK ONLY** | Real-log ingestion readiness, schema models (No actual flight logs, no empirical flight validation) |
| **Phase 13** | Universal Design Engine Assembly| **LOCKED & VERIFIED** | Universal entry point (`TorqWingsDesignEngine`), master `FinalAircraftDesign` contract, provenance matrix, Fixed-Wing & VTOL adapters, dual JSON/MD reporting, CLI runner (17/17 passed) |
| **Multirotor** | Multirotor Pipeline | **NEXT ROADMAP TARGET**| Extension point established; physics deferred; forensic repository audit is immediate next step |

---

## Completed Engineering Progression (Phases 1 — 13)

### Fixed-Wing Baseline Pipeline
- **Scope**: Established a hardened, deterministic 13-stage multidisciplinary sizing loop (`backend/design/fixed_wing/pipeline/fixed_wing_pipeline.py`).
- **Core Capabilities**: Configuration selection, wing planform optimization, NACA polar database lookup, fuselage cabin sizing, payload packaging, tail volume sizing, propulsion co-optimization (motor/prop/ESC), electrical routing, mass buildup, CG balancing, and safety rule verification.
- **Verification Baseline**: 233 passed tests, 1 established known baseline failure (`test_performance_missed_results_in_verification_failure` in `test_sprint44B_corrections.py`).
- **Phase 13 Integration**: Wrapped by `FixedWingDesignAdapter` to feed the universal master design contract without modifying existing physics.

### VTOL Engineering Progression (Phases 1 — 12A)
- **Phase 1 (Foundation & Architecture)**: Established `VTOLRequirementModel`, QuadPlane Lift+Cruise layout, 10-phase mission profile, and pipeline infrastructure.
- **Phase 2 (Hover Performance)**: Sized vertical lift propulsion using actuator disk momentum theory, blade element theory, figure of merit ($FM=0.70$), and wing download penalties.
- **Phase 3 (Transition Dynamics)**: Established physical transition equations, transition speed corridor ($V_{trans} \ge 1.2 V_{stall}$), transition acceleration, and transition energy consumption.
- **Phase 4 (Energy Model & Battery Sizing)**: Formulated the authoritative mission energy ledger covering hover climb/descent, acceleration/deceleration transition, wing-borne cruise, and constant avionics draw; enforced a mandatory 20% usable reserve margin and discharge C-rating limits.
- **Phase 5 (Mass/CG/MTOW Multidisciplinary Closure)**: Implemented fixed-point multidisciplinary iteration with relaxation ($\alpha=0.70$, tolerance $0.015$, max 20 iterations) coupling battery mass, lift motors, cruise propulsion, and structure back into MTOW; enforced 3D component coordinate tracking and static margin constraints.
- **Phase 6 (Stability & Control Sizing)**: Sized inverted V-tail stabilizers using dihedral angle projections, tail volume coefficients ($V_h \ge 0.05, V_v \ge 0.02$), ruddervator control mixing, and 6-DOF stability derivatives ($C_{m\alpha}, C_{n\beta}, C_{l\beta}$).
- **Phase 7 (Deterministic Optimization)**: Formulated multi-objective genetic/grid search algorithms optimizing wing area, aspect ratio, and battery capacity while strictly penalizing infeasible candidates.
- **Phase 8 (Commercial Hardware Selection & BOM)**: Matched continuous engineering demands to verified off-the-shelf components: Sunnysky V4008 380KV lift motors, Spedix GS40A lift ESCs, Sunnysky X2820 800KV cruise motor, Hobbywing Skywalker 40A V2 cruise ESC, APC props, Tattu 6S 16000mAh LiPo, and Holybro Pixhawk 6X.
- **Phase 9 (System Integration)**: Formulated electrical bus topology (Paths A through G), power distribution board (Matek PDB-HEX), I/O channel allocation, 10-phase mission state machine, and 13 failure mode safety analyses.
- **Phase 10 (Flight Control Configuration)**: Built parameter trees for ArduPlane 4.5.4 QuadPlane integration, sensor orientation, and PWM mixer assignment.
- **Phase 11 (Physical Ground Verification)**: Executed 18 bench testing and physical commissioning procedures with propellers removed, validating bus voltages, ESC calibration, sensor telemetry, and transition logic. No flight was performed.
- **Phase 12 / 12A (Flight-Test Framework)**: Established data schemas and ingestion parsers for ArduPilot `.bin` flight data. No actual flight-log evidence exists, no empirical flight envelope is established, and flight validation is NEVER claimed.

---

## Phase 13: Final Design Engine Assembly & Universal Entry Pipeline

### Objective
Establish the universal programmatic entry point, master contract schemas, provenance subsystem, class-specific adapters, report generators, CLI execution tools, and comprehensive integration tests that unify all Torq Wings design capabilities under a single entry point.

### Architecture & Key Subsystems

1. **Universal Entry Point (`TorqWingsDesignEngine`)**:
   - Programmatic method: `TorqWingsDesignEngine.generate(aircraft_class, technical_requirements, output_dir=None)`.
   - Rejects raw unstructured text; validates schema and units of structured requirements.
   - Routes to class-specific adapter based strictly on `aircraft_class`.
   - Enforces the strict rule: **There is NO architecture selector inside the Design Engine.** Architecture selection is performed upstream by the Requirement Agent.

2. **Master Design Contract (`FinalAircraftDesign`)**:
   - Unified master output schema containing 25 top-level typed dataclass sections.
   - Standardizes spatial coordinate system (Nose tip datum, aviation axes).
   - Generates dedicated downstream data packages: `CADHandoverContract` and `SimulationHandoverContract`.
   - Formulates requirement traceability ledger with explicit design margins.

3. **Provenance Subsystem (`provenance.py`)**:
   - Enforces engineering transparency using 10 strict categories (`PROJECT_REQUIREMENT`, `CALCULATED`, `DERIVED`, `CONFIGURABLE_ASSUMPTION`, `COMMERCIAL_VERIFIED`, `PHYSICAL_GROUND_MEASUREMENT`, `PHYSICAL_BENCH_MEASUREMENT`, `DEFERRED`, `UNRESOLVED`, `NOT_APPLICABLE`).
   - Prevents preliminary assumptions or deferred values from masquerading as verified measurements.

4. **Pipeline Adapters**:
   - `FixedWingDesignAdapter`: Integrates locked 13-stage Fixed-Wing pipeline; tags non-applicable VTOL fields with `EngineeringStatus.NOT_APPLICABLE`.
   - `VTOLDesignAdapter`: Integrates authoritative Phases 1–11 VTOL pipeline; locks commercial ESC identities (`Spedix GS40A`, `Hobbywing Skywalker 40A V2`); enforces physical ground validation bounds.

5. **Universal CLI Runner (`scripts/run_design_pipeline.py`)**:
   - Provides standardized terminal access:
     `python scripts/run_design_pipeline.py --aircraft-type [fixed_wing|vtol] --requirements <path.json>`
   - Emits formatted console banners, stage progress, and summary metrics.

6. **Dual-Artifact Exporter (`report_generator.py`)**:
   - `final_aircraft_design.json`: Machine-readable, deterministic JSON with floats rounded to 4 decimals.
   - `final_aircraft_design.md`: Human-readable engineering markdown report.

7. **Contract Integrity Enforcement (`_validate_contract`)**:
   - Validates MTOW $> 0.0$, non-empty design ID, CAD/Sim handover blocks, and requirement traceability.
   - Strictly enforces `validation_status.flight_validated == False`.

### Test Status & Verification Baseline
- **Phase 13 Assembly Test Suite**: **17 / 17 passed** (`tests/design/test_phase13_final_assembly.py`).
- **VTOL Regression Test Suite**: **362 / 362 passed, 0 regressions** (`tests/design/vtol/`).
- **Fixed-Wing Baseline Test Suite**: **233 passed, 1 established known failure** (`tests/design/fixed_wing/`).


## Phase 0: Software Architecture [Status: DONE / IMPLEMENTED]

### Objective

Establish the software architecture, repository standards, documentation structure, and development boundaries for the platform.

### Deliverables

- Approved architecture documentation
- Repository structure baseline
- Project specification alignment
- Initial development standards
- Initial documentation standards

### Major Modules

- `docs/architecture/`
- `docs/developer_guides/`
- `backend/`
- `frontend/`
- `shared/`
- `tests/`

### Dependencies

- Project specification
- Approved repository structure

### Expected Output

A stable architectural foundation that future phases can follow without redesigning the project structure.

### Completion Criteria

- Architecture boundaries are documented.
- Repository structure is accepted.
- Development and documentation expectations are defined.
- No engineering implementation has begun before architecture approval.

## Phase 0.5: Engineering Knowledge Base [Status: DONE / IMPLEMENTED]

### Objective

Create the controlled knowledge base structure for approved aerospace engineering references, assumptions, terminology, constraints, and validation notes.

### Deliverables

- Engineering knowledge base documentation structure
- Knowledge entry standards
- Source and assumption traceability rules
- Review expectations for engineering references

### Major Modules

- `docs/engineering_knowledge_base/`
- `backend/validators/`
- `shared/`

### Dependencies

- Phase 0: Software Architecture
- Project specification

### Expected Output

A governed documentation foundation for future engineering methods and validation references.

### Completion Criteria

- Knowledge base organization is documented.
- Entry format and review requirements are defined.
- Engineering references are separated from implementation code.
- Traceability expectations are clear.

## Phase 0.75: Engineering Database [Status: PARTIAL / IN PROGRESS]

### Objective

Define the database philosophy, data ownership boundaries, schema documentation approach, and future data model areas.

### Deliverables

- Database documentation structure
- Data domain boundaries
- Initial schema planning standards
- Database versioning expectations
- Data traceability principles

### Major Modules

- `docs/database_schemas/`
- `backend/database/`
- `backend/models/`
- `shared/`

### Dependencies

- Phase 0: Software Architecture
- Phase 0.5: Engineering Knowledge Base

### Expected Output

A documented database foundation ready to support future mission, platform, component, analysis, optimization, validation, and reporting data.

### Completion Criteria

- Database domains are identified.
- Schema documentation expectations are defined.
- Data ownership boundaries are documented.
- No database implementation begins without approved schemas.

## Phase 1: Mission Intelligence Engine [Status: DONE / IMPLEMENTED]

### Objective

Define and later implement the capability area for representing mission intent, mission constraints, operational profiles, payload needs, endurance expectations, range expectations, and mission-level requirements.

### Deliverables

- Mission data definitions
- Mission requirement categories
- Mission validation boundaries
- Mission intelligence documentation
- Mission output contract for downstream phases

### Major Modules

- `backend/engines/`
- `backend/models/`
- `backend/services/`
- `backend/validators/`
- `docs/engineering_knowledge_base/`

### Dependencies

- Phase 0: Software Architecture
- Phase 0.5: Engineering Knowledge Base
- Phase 0.75: Engineering Database

### Expected Output

A structured mission definition that can guide platform, configuration, component, sizing, analysis, optimization, validation, and reporting workflows.

### Completion Criteria

- Mission inputs and outputs are documented.
- Mission constraints are traceable.
- Mission intelligence boundaries are clear.
- Downstream dependency requirements are defined.

## Phase 2: Platform Intelligence Engine [Status: DONE / IMPLEMENTED]

### Objective

Define and later implement the capability area for evaluating platform-level suitability across multirotor UAVs, fixed-wing UAVs, and hybrid VTOL UAVs.

### Deliverables

- Platform type definitions
- Platform selection criteria
- Platform constraint documentation
- Platform intelligence output contract
- Traceability from mission requirements to platform decisions

### Major Modules

- `backend/engines/`
- `backend/models/`
- `backend/services/`
- `backend/validators/`
- `docs/engineering_knowledge_base/`

### Dependencies

- Phase 1: Mission Intelligence Engine
- Engineering knowledge base
- Engineering database definitions

### Expected Output

A platform recommendation or platform suitability result that remains traceable to mission requirements and documented constraints.

### Completion Criteria

- Supported platform categories are documented.
- Platform decision boundaries are defined.
- Mission-to-platform traceability is established.
- Outputs are ready for configuration and platform design phases.

## Phase 3: Platform Design Engines [Status: DONE / IMPLEMENTED]

### Objective

Define and later implement aircraft-type-specific design engine areas for multirotor UAVs, fixed-wing UAVs, and hybrid VTOL UAVs.

### Deliverables

- Multirotor design engine scope
- Fixed-wing design engine scope
- Hybrid VTOL design engine scope
- Shared platform design boundaries
- Aircraft-type-specific output contracts

### Major Modules

- `backend/engines/`
- `backend/models/`
- `backend/services/`
- `backend/validators/`
- `backend/analysis/`
- `docs/engineering_knowledge_base/`

### Dependencies

- Phase 1: Mission Intelligence Engine
- Phase 2: Platform Intelligence Engine
- Engineering knowledge base
- Engineering database definitions

### Expected Output

Aircraft-type-specific design structures that can support later configuration, component, sizing, geometry, analysis, and validation work.

### Completion Criteria

- Multirotor Design Engine boundaries are documented.
- Fixed-Wing Design Engine boundaries are documented.
- Hybrid VTOL Design Engine boundaries are documented.
- Shared and aircraft-specific responsibilities are separated.

## Phase 4: Component Intelligence Engine [Status: DONE / IMPLEMENTED]

### Objective

Define and later implement the capability area for structured component data, component compatibility, component constraints, and component-level design evidence.

### Deliverables

- Component data categories
- Component compatibility rules
- Component validation boundaries
- Component database relationships
- Component intelligence output contract

### Major Modules

- `backend/engines/`
- `backend/models/`
- `backend/database/`
- `backend/services/`
- `backend/validators/`
- `docs/database_schemas/`

### Dependencies

- Phase 0.75: Engineering Database
- Phase 1: Mission Intelligence Engine
- Phase 2: Platform Intelligence Engine
- Phase 3: Platform Design Engines

### Expected Output

Structured component intelligence that can support configuration decisions, aircraft sizing, optimization, validation, and reporting.

### Completion Criteria

- Component data boundaries are documented.
- Compatibility and constraint categories are defined.
- Component records are traceable to source and validation expectations.
- Component outputs are ready for configuration and sizing phases.

## Phase 5: Configuration Intelligence Engine [Status: DONE / IMPLEMENTED]

### Objective

Define and later implement the capability area for organizing aircraft configuration decisions and configuration-level trade spaces.

### Deliverables

- Configuration categories
- Configuration decision boundaries
- Configuration compatibility expectations
- Configuration output contract
- Traceability to mission, platform, and component decisions

### Major Modules

- `backend/engines/`
- `backend/models/`
- `backend/services/`
- `backend/validators/`
- `shared/`

### Dependencies

- Phase 1: Mission Intelligence Engine
- Phase 2: Platform Intelligence Engine
- Phase 3: Platform Design Engines
- Phase 4: Component Intelligence Engine

### Expected Output

A structured aircraft configuration definition suitable for aircraft sizing, geometry generation, analysis, optimization, validation, and reporting.

### Completion Criteria

- Configuration inputs and outputs are documented.
- Compatibility rules are identified.
- Configuration decisions are traceable.
- Configuration outputs are ready for sizing.

## Phase 6: Aircraft Sizing Engine [Status: DONE / IMPLEMENTED]

### Objective

Define and later implement aircraft sizing workflows based on approved engineering methods, assumptions, mission requirements, platform decisions, configuration decisions, and component constraints.

### Deliverables

- Aircraft sizing scope
- Sizing input and output definitions
- Sizing assumption documentation
- Sizing validation expectations
- Sizing output contract

### Major Modules

- `backend/engines/`
- `backend/analysis/`
- `backend/models/`
- `backend/validators/`
- `docs/engineering_knowledge_base/`

### Dependencies

- Phase 1: Mission Intelligence Engine
- Phase 2: Platform Intelligence Engine
- Phase 4: Component Intelligence Engine
- Phase 5: Configuration Intelligence Engine

### Expected Output

A traceable aircraft sizing result that can support geometry generation, engineering analysis, optimization, validation, explainability, and reporting.

### Completion Criteria

- Sizing inputs and outputs are documented.
- Engineering assumptions are traceable.
- Validation expectations are defined.
- Sizing output is ready for geometry generation.

## Phase 7: Geometry Generation Engine (OpenVSP Integration Boundary) [Status: PARTIAL / IN PROGRESS]

### Objective

Define and later implement geometry generation workflows and OpenVSP integration boundaries for aircraft geometry representation.

### Deliverables

- Geometry generation scope
- OpenVSP integration boundary documentation
- Geometry input and output definitions
- Geometry validation expectations
- Geometry artifact management approach

### Major Modules

- `backend/engines/`
- `backend/services/`
- `backend/models/`
- `backend/validators/`
- `assets/`

### Dependencies

- Phase 3: Platform Design Engines
- Phase 5: Configuration Intelligence Engine
- Phase 6: Aircraft Sizing Engine

### Expected Output

A geometry representation suitable for engineering analysis, validation, visualization, reporting, and future export workflows.

### Completion Criteria

- Geometry requirements are documented.
- OpenVSP integration boundaries are defined.
- Geometry artifacts are traceable to aircraft sizing and configuration inputs.
- Geometry outputs are ready for analysis.

## Phase 8: Engineering Analysis Engine (VSPAERO Integration Boundary) [Status: PARTIAL / IN PROGRESS]

### Objective

Define and later implement engineering analysis workflows and VSPAERO integration boundaries for approved analysis domains.

### Deliverables

- Engineering analysis scope
- VSPAERO integration boundary documentation
- Analysis input and output definitions
- Analysis result traceability standards
- Analysis validation expectations

### Major Modules

- `backend/analysis/`
- `backend/engines/`
- `backend/services/`
- `backend/models/`
- `backend/validators/`
- `docs/engineering_knowledge_base/`

### Dependencies

- Phase 6: Aircraft Sizing Engine
- Phase 7: Geometry Generation Engine
- Engineering knowledge base

### Expected Output

Structured engineering analysis results that can support optimization, validation, explainability, and report generation.

### Completion Criteria

- Analysis boundaries are documented.
- VSPAERO integration boundaries are defined.
- Analysis outputs are traceable to geometry, sizing, configuration, and mission inputs.
- Analysis results are ready for optimization and validation.

## Phase 9A: Component Optimization Engine [Status: DONE / IMPLEMENTED]

### Objective

Define and later implement controlled optimization workflows for component selection or component-level alternatives within approved engineering and validation boundaries.

### Deliverables

- Component optimization scope
- Optimization input and output definitions
- Constraint documentation
- Objective documentation
- Optimization traceability expectations

### Major Modules

- `backend/optimization/`
- `backend/engines/`
- `backend/services/`
- `backend/models/`
- `backend/validators/`

### Dependencies

- Phase 4: Component Intelligence Engine
- Phase 6: Aircraft Sizing Engine
- Phase 8: Engineering Analysis Engine

### Expected Output

Traceable component optimization results that can be evaluated against mission, platform, configuration, sizing, analysis, and validation constraints.

### Completion Criteria

- Optimization boundaries are documented.
- Inputs, objectives, and constraints are defined.
- Results are explainable and traceable.
- Outputs are ready for whole aircraft optimization and validation.

## Phase 9B: Whole Aircraft Optimization Engine [Status: DONE / IMPLEMENTED]

### Objective

Define and later implement controlled optimization workflows across the aircraft-level design state while preserving traceability to mission requirements and engineering constraints.

### Deliverables

- Whole aircraft optimization scope
- Aircraft-level objective definitions
- Aircraft-level constraint documentation
- Optimization result structure
- Optimization validation expectations

### Major Modules

- `backend/optimization/`
- `backend/analysis/`
- `backend/engines/`
- `backend/services/`
- `backend/models/`
- `backend/validators/`

### Dependencies

- Phase 5: Configuration Intelligence Engine
- Phase 6: Aircraft Sizing Engine
- Phase 7: Geometry Generation Engine
- Phase 8: Engineering Analysis Engine
- Phase 9A: Component Optimization Engine

### Expected Output

A traceable optimized aircraft design state that can proceed to validation, explainability, and report generation.

### Completion Criteria

- Aircraft-level optimization scope is documented.
- Objective and constraint definitions are approved.
- Optimization results remain traceable.
- Outputs are ready for design validation.

## Phase 10: Design Validation Engine [Status: DONE / IMPLEMENTED]

### Objective

Define and later implement validation workflows for mission inputs, platform decisions, configuration decisions, component selections, sizing outputs, geometry, analysis results, and optimization outcomes.

### Deliverables

- Validation scope
- Validation rule categories
- Validation evidence structure
- Validation output contract
- Validation documentation standards

### Major Modules

- `backend/validators/`
- `backend/engines/`
- `backend/models/`
- `backend/services/`
- `tests/validation/`
- `docs/engineering_knowledge_base/`

### Dependencies

- Phase 1 through Phase 9B
- Engineering knowledge base
- Engineering database definitions

### Expected Output

A documented validation result that identifies whether a design state satisfies approved requirements, assumptions, constraints, and engineering checks.

### Completion Criteria

- Validation boundaries are documented.
- Validation evidence is traceable.
- Validation outputs are structured.
- Design states can be approved, rejected, or flagged for review.

## Phase 11: Explainability Engine [Status: DONE / IMPLEMENTED]

### Objective

Define and later implement explainability workflows that expose the reasoning, assumptions, constraints, data sources, and decision paths behind engineering outputs.

### Deliverables

- Explainability scope
- Explanation output structure
- Decision traceability model
- Assumption and source reference standards
- User-facing explanation boundaries

### Major Modules

- `backend/engines/`
- `backend/services/`
- `backend/models/`
- `shared/`
- `docs/engineering_knowledge_base/`

### Dependencies

- Phase 1 through Phase 10
- Engineering knowledge base
- Validation outputs

### Expected Output

Structured explanations for mission decisions, platform recommendations, configuration decisions, component choices, sizing results, analysis outputs, optimization outcomes, and validation results.

### Completion Criteria

- Explanation boundaries are documented.
- Decision paths are traceable.
- Assumptions and sources are referenced.
- Outputs are ready for report generation.

## Phase 12: Report Generation Engine [Status: DONE / IMPLEMENTED]

### Objective

Define and later implement report generation workflows for structured design reports, analysis summaries, validation records, and engineering documentation.

### Deliverables

- Report generation scope
- Report content structure
- Report data source mapping
- Report validation expectations
- Report output contract

### Major Modules

- `backend/engines/`
- `backend/services/`
- `backend/models/`
- `backend/validators/`
- `assets/`

### Dependencies

- Phase 1 through Phase 11
- Validation outputs
- Explainability outputs

### Expected Output

A structured engineering report that summarizes the design state, assumptions, analyses, optimizations, validation evidence, and explanations.

### Completion Criteria

- Report structure is documented.
- Report sources are traceable.
- Validation and explainability outputs are included.
- Report output is suitable for review and release workflows.

## Phase 13: AI Intelligence Layer [Status: PLANNED]

### Objective

Define and later implement AI-assisted workflows only after the engineering architecture, data model, validation system, explainability system, and report generation system are established.

### Deliverables

- AI scope and boundaries
- AI governance expectations
- AI prompt and workflow documentation
- AI traceability requirements
- AI safety and review expectations

### Major Modules

- `prompts/`
- `backend/services/`
- `backend/engines/`
- `shared/`
- `docs/developer_guides/`

### Dependencies

- Phase 1 through Phase 12
- Engineering knowledge base
- Validation engine
- Explainability engine
- Report generation engine

### Expected Output

AI-assisted engineering workflows that support, but do not replace, documented engineering methods, validation procedures, explainability, or human review.

### Completion Criteria

- AI boundaries are documented.
- AI outputs are traceable.
- AI workflows preserve engineering-first decision-making.
- AI assistance is integrated only where it supports approved platform workflows.

## Development Workflow

```text
Mission
↓
Mission Intelligence
↓
Platform Intelligence
↓
Configuration Intelligence
↓
Component Intelligence
↓
Aircraft Sizing
↓
Geometry Generation
↓
Engineering Analysis
↓
Optimization
↓
Validation
↓
Explainability
↓
Report Generation
↓
Final UAV Design
```

## Development Roadmap & Status Summary

### COMPLETED
- **Fixed-Wing Engineering Pipeline**: 13-stage deterministic sizing loop, configuration scoring, wing/tail/fuselage sizing, propulsion matching, mass/CG tracking, safety verification (233 passed, 1 known baseline failure).
- **VTOL Engineering Pipeline**: Comprehensive Lift+Cruise multidisciplinary synthesis spanning hover, transition, energy ledger, battery sizing, MTOW/CG convergence, stability/control derivatives, commercial hardware BOM, and bench testing (362 passed, 0 regressions).
- **Universal Final-Design Assembly (Phase 13)**: `TorqWingsDesignEngine` universal programmatic entry point and dispatcher (17 passed).
- **Fixed-Wing Adapter**: `FixedWingDesignAdapter` mapping existing pipeline outputs into the master contract without physics modifications.
- **VTOL Adapter**: `VTOLDesignAdapter` mapping authoritative VTOL outputs into the master contract and locking hardware identities.
- **Provenance Subsystem**: 10-category provenance tracking matrix enforcing engineering transparency and auditability.
- **Final Design Contract**: Strongly-typed `FinalAircraftDesign` master schema covering 25 comprehensive subsystems.
- **CAD Handover**: Complete 3D spatial definitions, datum origin, component bounding boxes, and mounting coordinates for downstream CAD Agents.
- **Simulation Handover**: Complete mass properties, aerodynamic drag polars, 6-DOF stability/control derivatives, and trim conditions for downstream Simulation Agents (inertia explicitly deferred to 3D CAD).
- **Universal CLI Runner**: `scripts/run_design_pipeline.py` supporting unified batch and interactive execution across aircraft classes.

### NEXT
- **Multirotor Forensic Repository Audit**: Comprehensive inspection of legacy multirotor files, candidate components, and sizing scripts to establish an authoritative baseline before implementation.
- **Multirotor Engineering Pipeline Development**: Implementation of authoritative multirotor physics modules (hover aerodynamics, rotor sizing, frame geometry, mass buildup, dynamic battery discharge).
- **Multirotor Validation**: Development of dedicated test suites and validation campaigns for multirotor convergence and safety boundaries.
- **Multirotor Integration into Universal Engine**: Removal of `NotImplementedError` in `universal_engine.py` and integration of `MultirotorDesignAdapter` conforming to `FinalAircraftDesign`.

> [!IMPORTANT]
> **Multirotor Physics Status**
> Multirotor engineering physics are **NOT** implemented in the universal engine. The extension point is established architecturally. The immediate next engineering step is a forensic repository audit before implementation.

