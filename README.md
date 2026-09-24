# Torq Wings Design Engine

A disciplined, multidisciplinary aerospace engineering software platform for mission-driven preliminary sizing, optimization, validation, assembly, and reporting of unmanned aerial vehicles (UAVs).

## Overview

Torq Wings Design Engine is an advanced Python-based UAV preliminary design synthesis and analysis platform. It translates structured mission requirements into fully converged, rule-verified aircraft design specifications conforming to the master `FinalAircraftDesign` contract.

The system sits inside an end-to-end autonomous engineering workflow:

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
        ├── Fixed-Wing Pipeline (Locked Implementation)
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

> [!IMPORTANT]
> **Architectural Boundary: No Architecture Selection Inside Design Engine**
>
> The Design Engine contains **no architecture selector**. The upstream **Requirement Agent** translates raw customer requirements into structured technical requirements and selects the target `aircraft_class`. The Design Engine acts as a universal entry point, dispatcher, multidisciplinary solver orchestrator, and master contract assembly layer.

## System Implementation Maturity

- **Universal Design Engine Entry Point & Assembly (Phase 13)**: **IMPLEMENTED & OPERATIONAL** (`backend/design/assembly/universal_engine.py`, 17 tests passed).
- **Fixed-Wing Design Pipeline**: **IMPLEMENTED & LOCKED** (`backend/design/fixed_wing/pipeline/`, 233 passed, 1 established known failure).
- **Hybrid VTOL Design Pipeline**: **IMPLEMENTED & LOCKED** (`backend/design/vtol/pipeline/`, 362 tests collected & passing with 0 regressions).
- **Multirotor Design Pipeline**: **EXTENSION POINT ESTABLISHED / PHYSICS DEFERRED** (`AircraftClass.MULTIROTOR` extension point in place; raises `NotImplementedError` per Phase 13 Section 28; forensic repository audit is next).
- **Master Design Contract (`FinalAircraftDesign`)**: **IMPLEMENTED & OPERATIONAL** (25 top-level typed sections).
- **Provenance Subsystem**: **IMPLEMENTED & OPERATIONAL** (10 provenance categories, 4 engineering statuses).
- **CAD & Simulation Handover**: **IMPLEMENTED & OPERATIONAL** (spatial geometries, coordinate systems, aero polars, 6-DOF stability/control derivatives; detailed solid-body inertia explicitly deferred to 3D CAD).
- **Universal CLI Runner**: **IMPLEMENTED & OPERATIONAL** (`scripts/run_design_pipeline.py`).
- **REST API Layer (`backend/api/`)**: Planned / Future Roadmap.
- **SQL Database Layer (`backend/database/`)**: Planned / Future Roadmap.
- **Frontend User Interface (`frontend/`)**: Planned / Future Roadmap.

## Current Capabilities

- **Universal Dispatch**: Accepts typed dictionaries or requirement models, verifies parameter completeness, and dispatches to class-specific adapters (`FixedWingDesignAdapter`, `VTOLDesignAdapter`).
- **Multidisciplinary Sizing Loops**: Continuous-variable and catalog-driven multidisciplinary convergence loops for MTOW, wing geometry, tail surfaces, lift propulsion, forward cruise propulsion, battery sizing, and electrical distribution.
- **Authoritative Mass & 3D CG Closure**: 3D component layout tracking, longitudinal balance, forward/aft CG envelope validation, and component mass rollups.
- **Flight Performance & Stability**: Cruise drag polars, stall speed, maximum speed, climb ceilings, hover endurance, transition corridors, neutral point calculation, static margin enforcement, and stability/control derivative matrices.
- **Commercial Hardware Matching & BOM**: Reconciles sized electrical and mechanical demands against verified commercial catalog components (motors, ESCs, propellers, batteries, servos, flight controllers).
- **Comprehensive Provenance Tracking**: Tracks origin metadata (`PROJECT_REQUIREMENT`, `CALCULATED`, `DERIVED`, `CONFIGURABLE_ASSUMPTION`, `COMMERCIAL_VERIFIED`, `PHYSICAL_GROUND_MEASUREMENT`, `PHYSICAL_BENCH_MEASUREMENT`, `DEFERRED`, `UNRESOLVED`, `NOT_APPLICABLE`) for all key engineering parameters.
- **Downstream Agent Handovers**: Prepares clean coordinate-referenced geometry packages for CAD Agents and aerodynamic/control derivatives for 6-DOF Simulation Agents.
- **Automated Dual-Artifact Reporting**: Exports deterministic `final_aircraft_design.json` and human-readable `final_aircraft_design.md` reports.

## Aircraft Design Domains

| Aircraft Category | Implementation Status | Pipeline Adapter | Key Implemented Features |
| :--- | :--- | :--- | :--- |
| **Fixed-Wing** | **Implemented & Locked** | `FixedWingDesignAdapter` → `FixedWingDesignPipeline` | 13-stage sizing loop, wing & tail planform optimization, NACA airfoil polar lookup, fuselage cabin sizing, propulsion matching, performance envelope, static margin compliance. |
| **Hybrid VTOL** | **Implemented & Locked** | `VTOLDesignAdapter` → `VTOLDesignPipeline` | Lift + Cruise (QuadPlane) architecture, authoritative hover sizing, transition dynamics, mission energy ledger, multidisciplinary MTOW/CG convergence, stability/control mixing, commercial BOM, ground verification. |
| **Multirotor** | **Extension Point Established** | Raises `NotImplementedError` | Architectural extension slot established in `universal_engine.py` and `final_design_contract.py`. Physics modules deferred. Next step is forensic repository audit. |

## Engineering Workflow

The end-to-end design synthesis workflow follows a strict, traceable execution sequence:

```text
Structured Technical Requirements + Target Aircraft Class
                           ↓
              TorqWingsDesignEngine.generate()
                           ↓
             Requirement Schema & Unit Validation
                           ↓
            Pipeline Dispatch to Dedicated Adapter
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
FixedWingDesignAdapter               VTOLDesignAdapter
         │                                   │
FixedWingDesignPipeline               VTOLDesignPipeline
(13-Stage Sizing Loop)               (Phases 1-11 Multidisciplinary Loop)
         │                                   │
         └─────────────────┬─────────────────┘
                           ↓
       Contract Normalization & Provenance Tagging
                           ↓
              _validate_contract(design)
     (Enforces MTOW > 0, CAD/Sim Handovers, flight_validated=False)
                           ↓
             Deterministic Artifact Generation
            ├── final_aircraft_design.json
            └── final_aircraft_design.md
```

## Implemented Engineering Systems

- `backend/design/common/`: Shared requirement models, design context, validation rules, verification rule engines, and verification context models.
- `backend/design/router/`: Engine registry and router (`DesignEngineRouter`) dispatching design context to category-specific studios.
- `backend/design/studio/`: Workflow stage manager (`DesignStageManager`) and workflow orchestrator (`DesignWorkflow`).
- `backend/design/advisor/`: Vehicle recommendation engine (`RecommendationEngine`), feasibility assessor, and ranking strategies.
- `backend/design/components/`: Component repositories, candidate scoring, compatibility rules, and component selectors.
- `backend/design/multirotor/`: Multirotor mission strategy, frame optimizer, motor/propeller/ESC/battery optimizers, electrical engine, layout engine, mass properties engine, and synthesis pipeline.
- `backend/design/fixed_wing/`: Fixed-wing mission engine, configuration engine, wing engine, airfoil engine, tail engine, fuselage engine, propulsion engine, avionics engine, payload engine, mass properties engine, flight performance engine, verification engine, CAD engine, manufacturing engine, report engine, and synthesis pipeline.
- `backend/design/vtol/`: Hybrid VTOL mission engine, configuration engine, wing engine, airfoil engine, tail engine, fuselage engine, lift system engine, forward propulsion engine, electrical engine, avionics engine, payload engine, mass properties engine, hover performance engine, transition engine, cruise performance engine, CAD engine, manufacturing engine, report engine, and synthesis pipeline.
- `backend/knowledge/`: Knowledge engine (`KnowledgeEngine`), markdown document parser, graph builder, and entity repository.
- `backend/application/`: Root application container (`TorqWingsApplication`) managing backend lifecycle and knowledge loading.

## Validation & Testing

The repository contains an extensive test suite and validation campaign infrastructure:

- **Unit Tests**: Test suites covering individual sizers, selectors, models, and validators under `tests/design/`.
- **Integration & Pipeline Tests**: Full pipeline synthesis tests verifying convergence and output contracts for Multirotor, Fixed-Wing, and VTOL UAVs under `tests/design/*/pipeline/`.
- **Validation Campaigns**: Automated execution scripts under `scripts/` (e.g., `run_validation_campaign.py`, `export_all_600_cases.py`) that evaluate hundreds of design test cases, recording convergence metrics and engineering invariant compliance.

## CAD & Manufacturing

- **Parametric CAD Framework**: Generates feature trees, reference geometries, coordinate alignments, and code-driven CAD exports for fuselages, wings, tails, propulsion mounts, and internal packaging layouts.
- **Manufacturing Outputs**: Automatically produces itemized Bills of Materials (BOM), manufacturing cost breakdowns, laser/CNC cutting plans, 3D printing export settings, procurement lists, and step-by-step build specifications.

## Repository Structure

```text
torqwings studio v2/
├── ARCHITECTURE.md          # Architecture specification & subsystem boundaries
├── CONTRIBUTING.md            # Guidelines for code, documentation, and testing
├── LICENSE                    # Software license terms
├── PROJECT.md                 # Master project specification & single source of truth
├── README.md                  # Public-facing project documentation
├── ROADMAP.md                 # Phased development roadmap and milestone tracking
├── assets/                    # Project media, diagrams, and static assets
├── backend/                   # Core Python application & engineering engines
│   ├── api/                   # (Planned) REST API layer
│   ├── application/           # Application lifecycle container
│   ├── database/              # (Planned) Database persistence layer
│   ├── design/                # Engineering design studios & synthesis engines
│   │   ├── advisor/           # Vehicle recommendation & feasibility engine
│   │   ├── common/            # Shared requirements, context, validation, verification
│   │   ├── components/        # Component repository & selection engine
│   │   ├── drone/             # Drone performance & avionics subsystem adapters
│   │   ├── fixed_wing/        # Fixed-wing design engine (21+ subsystems)
│   │   ├── multirotor/        # Multirotor design engine (10+ subsystems)
│   │   ├── router/            # Design engine registry & router
│   │   ├── studio/            # Workflow stage orchestration & artifact management
│   │   └── vtol/              # Hybrid VTOL design engine (21+ subsystems)
│   ├── knowledge/             # Engineering knowledge base engine & parser
│   └── models/                # Domain entities & knowledge models
├── docs/                      # Technical documentation & engineering frameworks
├── exports/                   # Output directory for generated engineering artifacts
├── frontend/                  # (Planned) User interface application
├── reports/                   # Generated validation reports, CSV ledgers, and datasheets
├── scratch/                   # Scratch scripts and temporary analysis tools
├── scripts/                   # Runnable pipeline scripts, diagnostics, and campaign runners
└── tests/                     # Comprehensive unit, integration, and validation test suite
```

## Running the Project

### Prerequisites

- Python 3.10+
- `pytest` (for running tests)

### Executing the Universal Design Engine (CLI)

Use the universal entry runner `scripts/run_design_pipeline.py` to synthesize aircraft designs from structured requirements:

```bash
# Execute Fixed-Wing Synthesis Pipeline
python scripts/run_design_pipeline.py \
    --aircraft-type fixed_wing \
    --requirements examples/fixed_wing_requirements.json

# Execute VTOL Synthesis Pipeline
python scripts/run_design_pipeline.py \
    --aircraft-type vtol \
    --requirements examples/vtol_requirements.json

# Specify a custom export directory
python scripts/run_design_pipeline.py \
    --aircraft-type vtol \
    --requirements examples/vtol_requirements.json \
    --output-dir exports/custom_vtol/
```

### Running Test Suites & Verification Baseline

The repository enforces strict regression testing across all engineering pipelines:

```bash
# Run Phase 13 Universal Assembly & Contract Tests (17/17 passed)
pytest tests/design/test_phase13_final_assembly.py

# Run VTOL Regression Test Suite (362/362 passed, 0 regressions)
pytest tests/design/vtol/

# Run Fixed-Wing Baseline Test Suite (233 passed, 1 established known failure)
pytest tests/design/fixed_wing/
```

> [!NOTE]
> Fixed-Wing test suite maintains 233 passed tests and 1 pre-existing known baseline failure (`test_performance_missed_results_in_verification_failure` in `test_sprint44B_corrections.py`). This baseline is intentionally preserved untouched.

### Programmatic Python Usage

Execute the universal entry point directly via `TorqWingsDesignEngine.generate()`:

```python
from backend.design.assembly.universal_engine import TorqWingsDesignEngine

# 1. Define structured requirements (dictionary or typed model)
fw_requirements = {
    "payload_weight_kg": 0.5,
    "range_km": 35.0,
    "cruise_speed_kmh": 90.0,
    "endurance_min": 45.0,
}

# 2. Invoke Universal Design Engine
design = TorqWingsDesignEngine.generate(
    aircraft_class="FIXED_WING",
    technical_requirements=fw_requirements,
    output_dir="exports/fixed_wing_run/",
)

print(f"Design ID: {design.design_id}")
print(f"Status: {design.design_status.value}")
print(f"MTOW: {design.mass_properties.mtow_kg:.2f} kg")
print(f"Wing Span: {design.geometry.wing.span_m:.2f} m")
print(f"Cruise L/D: {design.aerodynamics.ld_cruise:.1f}")
print(f"Flight Validated: {design.validation_status.flight_validated}")  # Always False
```

## Documentation

Comprehensive project and engineering documentation is available at root and under `docs/`:

- [PROJECT.md](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/PROJECT.md): Master Project Specification
- [ARCHITECTURE.md](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/ARCHITECTURE.md): Software Architecture Blueprint
- [ROADMAP.md](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/ROADMAP.md): Development Phasing & Phased Milestones
- [CONTRIBUTING.md](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/CONTRIBUTING.md): Contribution & Development Guidelines
- [docs/](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/docs/): Engineering Frameworks, API References, and Domain Handbooks

## Development Status / Roadmap

Core engineering logic, multidisciplinary synthesis loops, verification engines, CAD generation frameworks, and report output generators are fully implemented in Python.

Future roadmap phases focus on:
1. REST API endpoint layer (`backend/api/`)
2. SQL Database persistence layer (`backend/database/`)
3. Web-based User Interface (`frontend/`)
4. Direct binary bindings for external solvers (OpenVSP / VSPAERO)

See [ROADMAP.md](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/ROADMAP.md) for full phase details.

## Contributing

See [CONTRIBUTING.md](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/CONTRIBUTING.md) for contribution rules, code standards, and PR workflows.

## License

Refer to the [LICENSE](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/LICENSE) file for licensing terms.
