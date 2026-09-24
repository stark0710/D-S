# Torq Wings Design Engine Architecture Specification
## Phase 13 — Universal Entry Point, Pipeline Dispatch & Final Design Assembly

## Purpose

This document is the official software architecture specification for the Torq Wings Design Engine. It defines the approved system architecture, subsystem boundaries, entry point contracts, pipeline dispatch mechanisms, provenance framework, downstream handovers, and development principles established through Phase 13.

This document serves as the authoritative technical blueprint for engineers, system integrators, and AI agents. The Python implementation is authoritative; this specification documents the implemented architecture without fabrication or ungrounded assumptions.

---

## 1. System Architecture & End-to-End Workflow

The Torq Wings UAV synthesis and downstream pipeline is organized into distinct, decoupled agentic and engineering layers:

```text
RAW USER ENGLISH
        ↓
REQUIREMENT AGENT
        ↓
STRUCTURED TECHNICAL REQUIREMENTS
        ↓
TORQ WINGS DESIGN ENGINE
        ↓
AIRCRAFT-CLASS DISPATCH
        ├── Fixed-Wing Pipeline (Locked Engineering Implementation)
        ├── VTOL Pipeline (Authoritative Phases 1–11 Implementation)
        └── Multirotor Pipeline (Extension Point — Physics Deferred)
                ↓
        FINAL AIRCRAFT DESIGN SPECIFICATION
                ↓
             CAD AGENT
                ↓
             3D MODEL
                ↓
        SIMULATION AGENT
```

### Critical Architectural Boundary: No Architecture Selection Inside Design Engine

> [!IMPORTANT]
> **There is NO architecture selector inside the Torq Wings Design Engine.**
>
> The upstream **Requirement Agent** is exclusively responsible for converting raw user language into:
> 1. `aircraft_class` (`FIXED_WING`, `VTOL`, or `MULTIROTOR`)
> 2. `technical_requirements` (strongly-typed schema or dictionary)
>
> The Design Engine receives already-structured technical requirements and strictly dispatches to the explicitly requested aircraft-class pipeline.
>
> The universal Design Engine is therefore an **entry point, routing dispatcher, and final contract assembly layer**, NOT an architecture-selection or natural-language parsing system.
>
> If a raw string is passed to the Design Engine, execution immediately aborts with `InvalidTechnicalRequirementsError`. If `aircraft_class` is missing or unknown, execution aborts with `UnsupportedArchitectureError`.

---

## 2. Universal Programmatic Entry Point

The universal entry interface is implemented by `TorqWingsDesignEngine` (`backend/design/assembly/universal_engine.py`):

```python
TorqWingsDesignEngine.generate(
    aircraft_class: Union[str, AircraftClass, AircraftType],
    technical_requirements: Union[Dict[str, Any], RequirementModel, VTOLRequirementModel],
    output_dir: Optional[str] = None,
) -> FinalAircraftDesign
```

### Execution Lifecycle

When invoked, the universal engine executes an 8-step lifecycle:

1. **Class Resolution**: Canonicalizes `aircraft_class` to `AircraftClass` enum (`FIXED_WING`, `VTOL`, `MULTIROTOR`).
2. **Architecture Extension Check**: If `AircraftClass.MULTIROTOR` is requested, immediately raises `NotImplementedError` per Section 28 (extension point established, physics modules deferred to future phase).
3. **Structured Requirements Validation**: Validates schema and units. Rejects raw strings, missing required parameters (`payload_weight_kg` / `payload.mass_kg`), or undefined mission goals. Converts to canonical domain requirement models (`RequirementModel` or `VTOLRequirementModel`).
4. **Pipeline Dispatch**: Routes execution to the dedicated adapter:
   - `AircraftClass.FIXED_WING` → `FixedWingDesignAdapter`
   - `AircraftClass.VTOL` → `VTOLDesignAdapter`
5. **Engineering Pipeline Execution**: Executes the category-specific multidisciplinary synthesis loop (preserving locked Fixed-Wing physics and authoritative VTOL iterative convergence).
6. **Contract Normalization & Assembly**: The adapter maps the raw pipeline results into the strongly-typed `FinalAircraftDesign` master schema, resolving all 25 top-level contract sections, requirement traceability margins, and provenance tags.
7. **Final Contract Validation**: Enforces Section 11 integrity rules via `_validate_contract(design)`:
   - Non-empty `design_id`
   - Strictly positive MTOW (`mtow_kg > 0.0`)
   - Complete CAD handover specification present
   - Complete Simulation handover specification present
   - Requirement traceability items populated
   - Provenance records populated
   - **Mandatory Guardrail**: `validation_status.flight_validated` MUST be `False` (empirical flight testing is not validated).
8. **Deterministic File Export**: If `output_dir` is provided, writes deterministic `final_aircraft_design.json` and human-readable `final_aircraft_design.md` via `backend/design/assembly/report_generator.py`.

---

## 3. The Three Aircraft Pipelines

The Design Engine architecture defines three category pipeline slots:

```text
                           TORQ WINGS DESIGN ENGINE
                                       │
                ┌──────────────────────┼──────────────────────┐
                ▼                      ▼                      ▼
        FIXED-WING PIPELINE      VTOL PIPELINE       MULTIROTOR PIPELINE
        ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
        │ Status: LOCKED   │  │ Status: LOCKED   │  │ Status: DEFERRED │
        │ 13 Sizing Stages │  │ Phases 1-11 Loop │  │ Extension Point  │
        │ 233 Passed       │  │ 362 Passed       │  │ Awaiting Forensic│
        │ 1 Known Failure  │  │ 0 Regressions    │  │ Audit & Sizing   │
        └──────────────────┘  └──────────────────┘  └──────────────────┘
                │                      │                      │
        FixedWingDesignAdapter  VTOLDesignAdapter     [NotImplemented]
                │                      │                      │
                └──────────────────────┼──────────────────────┘
                                       ▼
                             FinalAircraftDesign
```

### A. Fixed-Wing Pipeline
- **Implementation**: Fully implemented in `backend/design/fixed_wing/` and orchestrated by `FixedWingDesignPipeline`.
- **Status**: Locked engineering baseline. Phase 13 does NOT rewrite, modify, or recalculate Fixed-Wing physics.
- **Integration**: Mapped through `FixedWingDesignAdapter` (`backend/design/assembly/fixed_wing_adapter.py`). VTOL-specific fields (`lift_propulsion`, `transition`) are explicitly assigned `EngineeringStatus.NOT_APPLICABLE`.
- **Test Baseline**: 233 passed tests, 1 established known failure (`test_performance_missed_results_in_verification_failure` in `tests/design/fixed_wing/pipeline/test_sprint44B_corrections.py`).

### B. VTOL Pipeline
- **Implementation**: Authoritative multidisciplinary sizing pipeline spanning Phases 1–11 in `backend/design/vtol/`.
- **Configuration**: Lift + Cruise (QuadPlane) architecture with 4 vertical lift motors and 1 forward pusher cruise motor.
- **Status**: Authoritative engineering modules locked. Fixed-point iterative MTOW/CG convergence (`tolerance=0.015, max_iterations=20, relaxation_alpha=0.70`).
- **Integration**: Mapped through `VTOLDesignAdapter` (`backend/design/assembly/vtol_adapter.py`). Enforces locked Phase 8/11 commercial hardware identities (`Spedix GS40A` lift ESCs, `Hobbywing Skywalker 40A V2` cruise ESC).
- **Validation State**: Bench and physical ground verified only. **No flight validation is claimed.**
- **Test Baseline**: 362 tests collected and passing with 0 regressions across `tests/design/vtol/`.

### C. Multirotor Pipeline
- **Implementation Status**: **DEFERRED / EXTENSION POINT ESTABLISHED**.
- **Architecture Role**: The slot exists conceptually and architecturally in `AircraftClass.MULTIROTOR`, `final_design_contract.py` (`MultirotorFrameGeometryContract(status=EngineeringStatus.DEFERRED)`), and `universal_engine.py`.
- **Guardrail**: Universal engine raises `NotImplementedError` if called with `MULTIROTOR`. Multirotor physics are **NOT** claimed as implemented in the universal engine. The next development step is a forensic repository audit before implementation.

---

## 4. Final Aircraft Design Contract

The master contract output by the Design Engine is `FinalAircraftDesign` (`backend/design/assembly/final_design_contract.py`). It provides a comprehensive, strongly-typed specification with 25 top-level sections:

| Contract Section | Model Class | Description & Key Fields |
|:---|:---|:---|
| **Design Identity** | `design_id: str` | Canonical identifier (e.g. `TW-FW-YYYYMMDD-HHMMSS` or `TW-VTOL-YYYYMMDD-HHMMSS`). |
| **Aircraft Class** | `aircraft_class: AircraftClass` | `FIXED_WING`, `VTOL`, or `MULTIROTOR`. |
| **Configuration** | `configuration: str` | Layout family description (e.g. `LIFT_CRUISE_QUADPLANE`, `CONVENTIONAL_HIGH_WING`). |
| **Mission** | `mission: Dict[str, Any]` | Operational profile: range, endurance, cruise speed, altitude, payload mass, environment. |
| **Technical Requirements** | `technical_requirements: Dict[str, Any]` | Input technical requirements captured for full upstream traceability. |
| **Coordinate System** | `coordinate_system: CoordinateSystemContract` | Aircraft reference datum (`X=0` Nose tip, `Y=0` Centerline, `Z=0` Waterline), standard aviation axes (+X Aft, +Y Right, +Z Down). |
| **Geometry** | `geometry: GeometryContract` | Subsystems: `wing` (`span_m`, `area_m2`, `ar`, `mac_m`, `taper_ratio`, airfoils), `fuselage` (`length_m`, bay dimensions), `booms` (count, length, spacing), `tail` (`total_area_m2`, V-tail angle, projected areas), `multirotor_frame` (`DEFERRED`). |
| **Aerodynamics** | `aerodynamics: AerodynamicsContract` | Cruise $C_L$, $C_{D0}$, $k_{induced}$, cruise $C_D$, $L/D_{cruise}$, $L/D_{max}$, stall speed, trim $\alpha$, polar drag breakdown. |
| **Propulsion** | `propulsion: PropulsionContract` | `cruise_propulsion` (`PropulsionUnitContract`) and `lift_propulsion` (`LiftPropulsionContract`), motor models, propeller sizes, ESC ratings, thrust, and electrical power. |
| **Transition** | `transition: TransitionContract` | VTOL-specific: $V_{stall}$, safe transition speed ($V_{trans}$), transition duration, thrust schedules, transition energy. `NOT_APPLICABLE` for Fixed-Wing. |
| **Energy** | `energy: EnergyContract` | Stored energy, mission energy requirement, reserve percentage, hover/cruise/transition/avionics energy breakdown. |
| **Battery** | `battery: BatteryContract` | Chemistry (LiPo), series cell count (6S), capacity (mAh), energy (Wh), mass, continuous C-rating, pack model. |
| **Mass Properties** | `mass_properties: MassPropertiesContract` | Authoritative MTOW, empty mass, payload, battery, structure, propulsion, avionics, wiring harness mass; 3D CG coordinates, forward/aft CG limits, travel margin, component mass breakdown (`ComponentMassItem`), and inertia tensor status (`InertiaTensorContract`). |
| **Stability** | `stability: StabilityContract` | Neutral point ($x_{NP}$), static margin (% MAC and meters), $C_{m\alpha}$, $C_{n\beta}$, $C_{l\beta}$, stability booleans. |
| **Controls** | `controls: ControlsContract` | Control derivatives ($C_{m\delta_e}$, $C_{n\delta_r}$, $C_{l\delta_a}$), pitch/yaw/roll authority, trim elevator deflection, trim feasibility boolean. |
| **Performance** | `performance: PerformanceContract` | Cruise speed, stall speed, maximum speed, ceiling, max climb rate, calculated range, cruise endurance, hover endurance. |
| **Avionics** | `avionics: AvionicsContract` | Hardware selections: flight controller, autopilot firmware, GNSS module, digital airspeed pitot, telemetry radio, RC receiver, companion SBC. |
| **Electrical** | `electrical: ElectricalContract` | Main bus voltage, avionics bus voltage, peak/continuous currents, PDB model, power module model. |
| **Commercial BOM** | `commercial_components: List[CommercialComponentItem]` | Authoritative catalog BOM: manufacturer, model, part number, quantity, unit mass, total mass, electrical ratings, verification status. |
| **Installation** | `installation: InstallationContract` | Mechanical mounting specs: battery tray, payload bay, avionics tray, cooling airflow ducting. |
| **Manufacturing** | `manufacturing: ManufacturingContract` | Materials and construction: wing composite layup, fuselage monocoque, spar tube specs, tail core material. |
| **Constraints** | `constraints: ConstraintsContract` | Design envelope boundaries: max MTOW, max span, min range, min endurance, 20% battery reserve, limit load factor (3.8g), ultimate factor (1.5x). |
| **Assumptions** | `assumptions: AssumptionsContract` | Physical constants and efficiencies: $\rho=1.225\text{ kg/m}^3$, $g=9.80665\text{ m/s}^2$, $\eta_{motor}=0.85$, $\eta_{esc}=0.95$, $\eta_{prop,cruise}=0.72$, $FM_{hover}=0.70$. |
| **Provenance** | `provenance: Dict[str, ProvenanceRecord]` | Traceable provenance matrix mapping engineering fields to categories, source modules, values, and units. |
| **Requirement Traceability** | `requirement_traceability: List[RequirementTraceabilityItem]` | Traceability ledger verifying requirements against design outcomes with calculated margins, limits, and PASS/FAIL status. |
| **CAD Handover** | `cad_handover: CADHandoverContract` | Data package for downstream CAD Agent (geometry, coordinates, airfoils, component envelopes, mounting locations, CG vector). |
| **Simulation Handover** | `simulation_handover: SimulationHandoverContract` | Data package for downstream Simulation Agent (mass, CG, aero polars, 6-DOF stability/control derivatives, trim points, deferred inertia). |
| **Validation Status** | `validation_status: ValidationStatusContract` | Design validated, commercial component verified, physical ground validated, **flight validated: False**. |
| **Overall Status** | `design_status: OverallDesignStatus` | High-level status: `DESIGN_VALIDATED`, `DESIGN_VALIDATED_WITH_DEFERRED_ITEMS`, `DESIGN_PARTIAL`, or `DESIGN_FAILED`. |

---

## 5. Provenance Subsystem

The provenance subsystem (`backend/design/assembly/provenance.py`) enforces engineering rigor. It prevents assumptions, preliminary estimates, or deferred parameters from being misconstrued as authoritative measurements:

### Provenance Categories

| Provenance Category | Meaning & Usage |
|:---|:---|
| `PROJECT_REQUIREMENT` | Invariable parameter explicitly supplied by the customer or upstream Requirement Agent (e.g. payload mass, minimum range). |
| `CALCULATED` | Direct deterministic result of a physical governing equation, aerodynamic formula, or numerical solver (e.g. MTOW, wing area, hover thrust). |
| `DERIVED` | Secondary engineering value computed from multiple primary calculated values (e.g. cruise electrical power from thrust and efficiencies). |
| `CONFIGURABLE_ASSUMPTION` | Engineering coefficient or environmental constant selected by engineering baseline (e.g. motor efficiency $\eta=0.85$, air density $\rho=1.225$). |
| `COMMERCIAL_VERIFIED` | Specification obtained from manufacturer datasheets or laboratory-measured commercial hardware (e.g. motor KV, ESC continuous current rating). |
| `PHYSICAL_GROUND_MEASUREMENT` | Value physically measured on calibrated ground test equipment (e.g. 3-point scale MTOW, Fluke multimeter bus voltage). |
| `PHYSICAL_BENCH_MEASUREMENT` | Dynamic value measured during bench testing with propellers removed (e.g. DShot rise time, pitot airspeed response). |
| `DEFERRED` | Engineering quantity intentionally postponed to downstream CAD/simulation or subsequent testing phases (e.g. detailed solid-body inertia tensor). |
| `UNRESOLVED` | Parameter that failed convergence or lacks a verified source. |
| `NOT_APPLICABLE` | Parameter belonging to an aircraft architecture not active in the current design (e.g. lift motor thrust on a Fixed-Wing UAV). |

### Engineering Status Flags

- `VALID`: Authoritative and fully verified within design tolerance.
- `DEFERRED`: Sizing completed; detailed extraction deferred downstream (e.g. moments of inertia deferred to 3D CAD).
- `UNRESOLVED`: Incomplete or missing verification data.
- `NOT_APPLICABLE`: Field does not apply to this aircraft class.

---

## 6. Downstream Agent Handovers

The Design Engine generates structured engineering handover contracts for two downstream AI agents:

### CAD Agent Handover (`CADHandoverContract`)
Exposes all spatial and physical packaging data required for parametric 3D CAD modeling:
- **Reference Datum & Origin**: Coordinate origin at nose tip (`X=0, Y=0, Z=0`), standard aviation orientation.
- **Major Geometry**: Wingspan, chords, aspect ratio, sweep, dihedral, fuselage length/width/height, tail surfaces, boom geometry.
- **Airfoils**: Explicit root and tip airfoil designations (e.g. `NACA 4412`, `NACA 0012`).
- **Control Surfaces**: Spans, chord percentages, and deflection angle limits for ailerons, elevators, rudders, or ruddervators.
- **Component Envelopes**: Physical 3D bounding boxes `[length, width, height]` for payload bay, battery bay, and avionics deck.
- **Mounting Coordinates**: Explicit 3D installation positions `[x, y, z]` for cruise motor, lift motors, battery, avionics, GNSS antenna, and pitot probe.
- **Center of Gravity**: Authoritative 3D CG coordinates `[cg_x, cg_y, cg_z]` in meters.
- **Manufacturing Parameters**: Layup and material specifications (carbon composite skin, foam cores, pultruded spars).

### Simulation Agent Handover (`SimulationHandoverContract`)
Exposes the mathematical and aerodynamic model required for 6-DOF flight dynamics simulation:
- **Mass & CG**: Converged MTOW, empty mass, payload mass, battery mass, and 3D CG position vector.
- **Inertia Tensor**: Explicitly marked with `status = EngineeringStatus.DEFERRED` and `reason = "Detailed solid-body inertia tensor deferred to 3D CAD mass properties compilation"`.
- **Aerodynamics Polar**: Clean drag polar breakdown ($C_L$, $C_{D0}$, $k_{induced}$, cruise $L/D$).
- **Stability Derivatives**: Non-dimensional stability derivatives ($C_{m\alpha}$, $C_{n\beta}$, $C_{l\beta}$).
- **Control Derivatives**: Control surface effectiveness derivatives ($C_{m\delta_e}$, $C_{n\delta_r}$, $C_{l\delta_a}$).
- **Control Limits**: Angular deflection limits for all control surfaces.
- **Propulsion Parameters**: Installed power, voltage, maximum thrust, cruise thrust, and throttle trim settings.
- **Trim Conditions**: Equilibrium cruise trim airspeed, angle of attack ($\alpha_{trim}$), and elevator deflection ($\delta_{e,trim}$).

---

## 7. Validation Status & Flight Boundaries

The Design Engine enforces clear distinctions between validation stages:

```text
[1. DESIGN VALIDATION]
    └── Iterative multidisciplinary convergence, constraint compliance, safety rules: PASS

[2. COMMERCIAL COMPONENT VERIFICATION]
    └── Catalog specs reconciled against manufacturer datasheets & Phase 8 BOM: VERIFIED

[3. PHYSICAL GROUND VALIDATION]
    └── Bench testing, power bus measurements, sensor checks, motor mapping (Props OFF): PASS

[4. FLIGHT VALIDATION]
    └── Empirical flight envelope expansion, flight logs, pitot calibration: NEVER CLAIMED
```

> [!WARNING]
> **STRICT FLIGHT VALIDATION BOUNDARY**
>
> `FinalAircraftDesign.validation_status.flight_validated` is hardcoded to **`False`**.
>
> The contract validation logic (`_validate_contract`) explicitly raises `ContractValidationError` if `flight_validated` is ever set to `True`.
>
> Phase 11 established bench ground verification with propellers removed. Phase 12/12A established flight-test framework models and log ingestion readiness, but **no real flight-log evidence exists, no empirical flight envelope is established, and flight validation is NEVER claimed.** Sizing calculations and simulation readiness must never be described as flight validation.

---

## 8. CLI Runner & Output Artifacts

The Design Engine provides a unified command-line interface (`scripts/run_design_pipeline.py`):

```bash
# Execute Fixed-Wing design pipeline
python scripts/run_design_pipeline.py \
    --aircraft-type fixed_wing \
    --requirements examples/fixed_wing_requirements.json

# Execute VTOL design pipeline
python scripts/run_design_pipeline.py \
    --aircraft-type vtol \
    --requirements examples/vtol_requirements.json

# Custom output directory execution
python scripts/run_design_pipeline.py \
    --aircraft-type vtol \
    --requirements examples/vtol_requirements.json \
    --output-dir custom_outputs/
```

### Deterministic Output Artifacts
Every pipeline run produces two complementary output files:
1. `final_aircraft_design.json`: Complete, machine-readable JSON specification containing all 25 contract sections, deterministic rounded floats (4 decimals), and complete provenance and handover blocks.
2. `final_aircraft_design.md`: Formatted, human-readable Markdown engineering design report containing executive summaries, component mass tables, aerodynamic polar breakdowns, BOM details, and handover summaries.


The backend architecture follows a layered structure:

```text
API Layer                        [PLANNED / IN DEVELOPMENT]
↓
Service Layer                    [IMPLEMENTED - Internal Python Services]
↓
Engineering Engines & Pipelines   [IMPLEMENTED & OPERATIONAL]
↓
Database Layer                   [PLANNED / IN DEVELOPMENT]
↓
Knowledge Base Engine & Parser   [IMPLEMENTED & OPERATIONAL]
```

### API Layer

The API Layer is the external access boundary for backend capabilities. It should expose controlled interfaces for frontend workflows, future integrations, and internal tools.

The API Layer should validate request shape, delegate business activity to services, and avoid embedding engineering logic directly.

### Service Layer

The Service Layer coordinates workflows across engines, databases, validation, reporting, and user-facing operations.

Services should orchestrate subsystem interactions while preserving clean boundaries between engineering engines and data access.

### Engineering Engines

Engineering Engines are responsible for domain-specific engineering workflows. Each engine should have clear inputs, outputs, assumptions, and validation expectations.

Engines should not own database persistence directly unless the architecture explicitly defines that boundary through services or repositories.

### Database Layer

The Database Layer manages structured project data, mission data, engineering data, component data, rules, compatibility records, formula records, analysis outputs, validation evidence, and report metadata.

The Database Layer should support traceability and reproducibility.

### Knowledge Base

The Knowledge Base is the controlled source for engineering rules, assumptions, methods, references, terminology, and validation knowledge.

Engineering engines should consume approved knowledge from the Knowledge Base rather than hardcoding engineering rules.

## 4. Frontend Architecture

The frontend should provide professional engineering workflows that reflect the approved backend architecture and engineering process.

### Dashboard

The Dashboard provides the project-level entry point, design status, workflow progress, validation state, and access to major platform areas.

### Mission Wizard

The Mission Wizard guides users through mission definition and requirement capture. It is the user-facing entry point for Mission Intelligence.

### Design Studio

The Design Studio provides the main workspace for platform, configuration, component, sizing, geometry, and design-state workflows.

### Optimization View

The Optimization View presents component optimization and whole-aircraft optimization workflows, candidate comparisons, objective progress, and constraint status.

### Validation View

The Validation View presents validation checks, validation evidence, warnings, failures, and review status.

### Engineering Report

The Engineering Report view presents structured report outputs generated from mission, design, analysis, optimization, validation, and explainability data.

### Component Database

The Component Database view provides access to approved component data, categories, compatibility information, and component evidence.

### Settings

Settings provide project configuration, user preferences, environment configuration, and future administrative controls within approved architecture boundaries.

## 5. Engineering Knowledge Base

The Engineering Knowledge Base exists to make engineering behavior controlled, auditable, and explainable.

Its purpose is to store approved:

- Engineering rules
- Assumptions
- Formula references
- Validation rules
- Compatibility rules
- Domain terminology
- Source references
- Method boundaries

Engineering rules are never hardcoded as isolated logic. The software must read approved engineering knowledge from the Knowledge Base or documented data sources designed for that purpose.

The Knowledge Base supports:

- Traceable engineering decisions
- Reproducible analysis
- Controlled validation
- Explainable outputs
- Reviewable engineering assumptions

## 6. Database Architecture

The database architecture is organized around engineering traceability and controlled data ownership.

### Mission Database

The Mission Database stores mission definitions, mission categories, operational context, constraints, payload requirements, endurance expectations, range expectations, and mission-level records.

### Engineering Database

The Engineering Database stores engineering data required by sizing, geometry, analysis, optimization, validation, explainability, and reporting workflows.

### Component Databases

Component Databases store structured component records, component categories, specifications, evidence, constraints, and source metadata.

### Rule Database

The Rule Database stores approved engineering, validation, compatibility, and workflow rules in a structured and reviewable form.

### Compatibility Database

The Compatibility Database stores relationships between missions, platform types, configurations, components, constraints, and validation requirements.

### Formula Database

The Formula Database stores approved formula references, formula metadata, assumptions, applicability boundaries, and source traceability.

### Relationships

Mission records drive platform, configuration, component, sizing, analysis, optimization, validation, and reporting workflows.

Engineering records must remain connected to mission context, platform decisions, configuration decisions, component choices, assumptions, rules, formulas, validation evidence, and report outputs.

Component data must be connected to compatibility records and validation rules before it can be used in selection or optimization workflows.

Formula records must be connected to engineering assumptions, applicability boundaries, and validation expectations.

## 7. Component Intelligence Architecture

All component selection must follow the approved component intelligence flow:

```text
Mission
↓
Mission Category
↓
Filtered Candidate Pool
↓
Optimization
↓
Validation
↓
Selected Component
```

No selector should search the entire component database directly.

The Component Intelligence Engine must first interpret the mission and mission category, then create a filtered candidate pool using approved compatibility rules and mission constraints.

Optimization should operate only on the filtered candidate pool. Validation must verify that selected components satisfy mission, platform, configuration, compatibility, safety, and performance constraints.

## 8. Optimization Architecture

Optimization is divided into component optimization and whole-aircraft optimization.

### Component Optimization

Component Optimization evaluates component candidates within mission-specific, platform-specific, configuration-specific, and compatibility-constrained candidate pools.

It must use approved objectives, constraints, and validation checks.

### Whole Aircraft Optimization

Whole Aircraft Optimization evaluates aircraft-level design states after mission, platform, configuration, component, sizing, geometry, and analysis information is available.

It must preserve full traceability from optimized outputs back to mission requirements and engineering assumptions.

### Candidate Generation

Candidate generation must be controlled by mission requirements, database records, compatibility constraints, configuration boundaries, and engineering knowledge.

Generated candidates must remain reviewable and traceable.

### Iterative Optimization

Iterative optimization should refine candidate designs through controlled feedback from analysis and validation outputs.

Iterations must not bypass validation or override engineering rules.

### Mission-Based Scoring

Optimization scoring must be based on mission requirements and approved objective definitions.

Scores should remain explainable and connected to the mission definition.

### Validation

Optimization outputs must pass validation before they can be promoted to selected or recommended design states.

## 9. Validation Architecture

Validation is a first-class subsystem. It verifies that design states, decisions, inputs, and outputs comply with approved engineering expectations.

Validation categories include:

- Electrical
- Mechanical
- Structural
- Mission
- Safety
- Performance
- Compatibility

Validation results should identify pass, fail, warning, and review-required states where appropriate. Validation evidence must remain traceable to rules, assumptions, data sources, and design records.

## 10. Explainability Architecture

Every engineering decision must be traceable.

The Explainability Engine provides an Engineering Decision Trace that records how a decision was produced, which inputs were used, which rules were applied, which assumptions were active, which candidates were considered, which constraints affected the result, and which validation checks were performed.

An Engineering Decision Trace should connect:

- Mission requirement
- Platform decision
- Configuration decision
- Component decision
- Sizing result
- Geometry artifact
- Analysis output
- Optimization result
- Validation evidence
- Report section

Explainability is required for engineering confidence, review, debugging, compliance, and future AI-assisted workflows.

## 11. AI Layer

The AI Intelligence Layer assists engineering. It never replaces engineering rules.

AI may support:

- Developer assistance
- Documentation assistance
- Workflow guidance
- Report drafting support
- Explanation summarization
- Review assistance

AI must operate within the approved architecture, engineering knowledge base, validation engine, explainability engine, and reporting workflow.

AI-generated outputs must remain reviewable, traceable, and subordinate to approved engineering data, rules, and validation procedures.

## 12. Development Principles

### Engineering First

Engineering correctness, traceability, and validation take priority over automation, presentation, or convenience.

### Database Driven

Structured data should guide platform behavior. Important engineering decisions should be supported by explicit records, schemas, relationships, and evidence.

### Knowledge Base Driven

Engineering rules, formulas, assumptions, compatibility knowledge, and validation expectations should come from the approved Knowledge Base and related structured records.

### Modular

Each subsystem should have clear responsibilities, inputs, outputs, and boundaries.

### Scalable

The architecture should support growth from early prototypes to commercial-grade aerospace software without requiring disruptive redesign.

### Explainable

Every engineering decision should be understandable, traceable, and reviewable.

### Production Ready

Future implementation should be maintainable, testable, documented, observable, and suitable for commercial aerospace software development.
