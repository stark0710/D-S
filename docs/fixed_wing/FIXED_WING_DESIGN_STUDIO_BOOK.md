# FIXED-WING DESIGN STUDIO
## Engineering Architecture, Design Pipeline & Developer Handbook
### Subtitle: Complete Technical Documentation of the Fixed-Wing Aircraft Design Engine

---

## PART I — INTRODUCTION

### Chapter 1 — What is the Fixed-Wing Design Studio?
The Fixed-Wing Design Studio is a catalog-based, multi-disciplinary aircraft design optimization (MDO) system. It automates the generation of compliant, high-performance, fixed-wing unmanned aerial vehicles (UAVs) starting from high-level mission requirements.

### Chapter 2 — System Architecture
The system utilizes a sequential design pipeline wrapped in an iterative convergence loop. The core design steps size the lifting surfaces, fuselage compartment, tail control volume, and select catalog-compliant propulsion, electrical, and avionics components. The design is evaluated dynamically against aerodynamic, stability, structural, and performance constraints.

### Chapter 3 — Repository Structure
```
backend/design/fixed_wing/
├── airfoil/          # Airfoil selection, Reynolds and polar analysis
├── avionics/         # Avionics selection (FC, GPS, telemetry, companion)
├── cad/              # CAD model and parametric assembly export
├── cg/               # CG Optimization over internal coordinates
├── configuration/    # Layout configuration selection (taper, dihedral, sweep)
├── convergence/      # Convergence iteration controller and snaps
├── electrical/       # Electrical current budget, BEC and wire optimizer
├── flight_performance/# Aerodynamic, takeoff, landing, climb, glide cruise analysis
├── fuselage/         # Fuselage compartment sizing and layout
├── manufacturing/    # BOM, assembly guidelines and cost estimation
├── mass_properties/  # Structural and component mass buildup, static margin
├── mission/          # Mission category classification and physics estimation
├── optimization/     # Shared base optimizer interfaces
├── payload/          # Payload sensor packaging and placement
├── performance/      # Performance-aware optimizer
├── pipeline/         # Design pipeline executor and stage facade
└── tail/             # Stabilizer sizing and volume coefficients
```

### Chapter 4 — Design Philosophy
The design studio relies on physics-based sizing methods coupled with component database matching. It prioritizes realistic, manufacturable aircraft specifications over unconstrained theoretical optimums.

---

## PART II — THE PIPELINE

### Chapter 5 — From User Requirements to Aircraft
The pipeline takes a `RequirementModel` input, translates it to specific subsystem requirements, sizing constraints, executes design stages sequentially, wraps the sizing in a convergence manager to balance structural mass feedback, verifies compliance, and outputs a `FinalAircraftSpecification`.

### Chapter 6 — Request Routing
High-level design requests enter via `router.py` and are passed to the `design_studio.py` facade, which routes fixed-wing requests to `FixedWingDesignPipeline` in `fixed_wing_pipeline.py`.

### Chapter 7 — Mission Strategy Selection
The `MissionTranslationStage` classifies the mission category using `MissionClassifier` and loads the strategy from `MissionStrategyRegistry`. The strategy defines target payload fractions, L/D ratio targets, and aerodynamic limits.

### Chapter 8 — Fixed-Wing Orchestration
`FixedWingDesignPipeline` manages the execution of thirteen sequential stages:
1. `MissionTranslationStage`
2. `ConfigurationSelectionStage`
3. `WingPlanformOptimizationStage`
4. `FuselageOptimizationStage`
5. `PayloadPackagingStage`
6. `TailOptimizationStage`
7. `PropulsionOptimizationStage`
8. `ElectricalSystemIntegrationStage`
9. `MassPropertiesStage`
10. `CGOptimizerStage`
11. `FlightPerformanceStage`
12. `AircraftConvergenceStage`
13. `VerificationCertificationStage`

### Chapter 9 — Iterative Design Loop
Sizing and performance depends heavily on the Maximum Takeoff Weight (MTOW). Since structural weight depends on the wing area, which depends on the MTOW, an iterative feedback loop is managed by `ConvergenceManager` in `convergence_manager.py`.

### Chapter 10 — Convergence
The loop checks convergence on MTOW and wing area. The convergence snap is defined in `design_snapshot.py` and evaluated by `ConvergenceChecker` using configurable tolerances (default is `0.01` kg for weight, `0.005` m² for wing area).

---

## PART III — AIRCRAFT DESIGN MODULES

### Chapter 11 — Mission Requirements
`MissionRequirements` class in `mission_requirements.py` maps the user input parameters like payload weight, flight time, range, cruise speed, and takeoff/landing constraints.

### Chapter 12 — Weight Estimation
The initial weight estimate is generated in `BaseMissionStrategy._estimate_mtow(req)` by dividing the payload weight by the target payload fraction.

### Chapter 13 — Wing Design
`WingSizer` sizes the reference area using the wing loading constraint:
$$S = \frac{W}{Typical\_Wing\_Loading}$$
The planform geometry (span, chords, taper) is calculated by `PlanformGeometryService`.

### Chapter 14 — Fuselage Design
`FuselageSizer` estimates the internal volume based on payload and battery dimensions plus a clearance margin. The fineness ratio controls the fuselage drag profile.

### Chapter 15 — Tail Design
`TailSizer` sizes the horizontal and vertical stabilizers using stability volume coefficients:
$$S_h = \frac{V_h \cdot S \cdot \overline{c}}{L_t}$$
$$S_v = \frac{V_v \cdot S \cdot b}{L_t}$$

### Chapter 16 — Payload Integration
`PayloadSelector` matches the mission type to concrete sensors in the database. `PayloadLayout` handles coordinate offsets.

### Chapter 17 — Propulsion
`PropulsionEngine` matches the climb and cruise power targets against the catalog database of motors, ESCs, and propellers using `GridSearchPropulsionCandidateGenerator`.

### Chapter 18 — Electrical System
`ElectricalOptimizer` selects wiring gauges, power modules, and BECs, enforcing current limits and voltage compatibility constraints.

### Chapter 19 — Mass Properties
`MassPropertiesEngine` builds up the empty weight, structural mass, component masses, and calculates the inertia matrix.

### Chapter 20 — Center of Gravity
`CGOptimizer` optimizes component placement coordinates along the longitudinal axis ($X$) to align the CG within the stable static margin envelope.

---

## PART IV — AEROSPACE ANALYSIS

### Chapter 21 — Aerodynamics
The aerodynamic polar is defined by:
$$C_d = C_{d0} + \frac{C_l^2}{\pi \cdot AR \cdot e}$$
Where $C_{d0} = 0.023$ and Oswald efficiency $e = 0.82$.

### Chapter 22 — Performance
Calculates speed envelopes, climb angles, and turning performance at operational altitudes.

### Chapter 23 — Takeoff
 take-off ground roll distance is given by:
$$S_{to} = \frac{2 \cdot (W/S)}{\rho \cdot (T/W) \cdot C_{L,to} \cdot g}$$

### Chapter 24 — Landing
Landing braking roll distance:
$$S_{landing} = \frac{0.48 \cdot (W/S)}{\rho \cdot C_{L,max,landing} \cdot \mu_b \cdot g}$$

### Chapter 25 — Climb
Rate of climb is calculated from excess power:
$$ROC = \frac{P_{excess}}{W} = \frac{(P_{max} \cdot \eta) - (D \cdot V)}{W}$$

### Chapter 26 — Cruise
Cruise drag balances thrust ($T_{cruise} = D_{cruise}$) and cruise power is:
$$P_{cruise} = \frac{T_{cruise} \cdot V_{cruise}}{\eta}$$

### Chapter 27 — Glide
The glide ratio matches the lift-to-drag ratio:
$$Glide\_Ratio = \frac{L}{D} = \frac{C_l}{C_d}$$

### Chapter 28 — Range
Flight range is cruise range:
$$Range = \frac{Endurance}{60} \cdot V_{cruise}$$

### Chapter 29 — Endurance
Battery-powered endurance (minutes):
$$Endurance = \frac{E_{battery}}{P_{continuous}} \cdot 60.0$$
Where $P_{continuous} = P_{cruise} + P_{avionics} + P_{payload}$.

### Chapter 30 — Ceiling
Absolute ceiling:
$$Altitude_{ceiling} = Altitude_{operational} + \frac{ROC}{0.00078}$$

### Chapter 31 — Turning Performance
Turn radius at 30 degrees bank angle:
$$R = \frac{V^2}{g \cdot \tan(\theta)}$$

### Chapter 32 — Stability
Static margin is defined as:
$$Static\_Margin = \frac{X_{np} - X_{cg}}{\overline{c}}$$

---

## PART V — SOFTWARE ENGINEERING

### Chapter 33 — Data Models
All design outputs conform to strictly-typed schemas defined in the module `models.py` files.

### Chapter 34 — Module Dependencies
The stages are orchestrated sequentially. A complete Mermaid dependency graph is provided in the Appendix.

### Chapter 35 — Validation
Every module contains a `Validator` (e.g. `WingValidator`) checking limits before returning results.

### Chapter 36 — Error Handling
Validation failures raise module-specific exceptions inheriting from `FixedWingPipelineError` (e.g., `SizingInfeasibleError`).

### Chapter 37 — Optimization
Components are chosen using grid search selectors evaluated against multi-objective functions.

### Chapter 38 — Testing
Tests are placed in `tests/design/fixed_wing/pipeline/` and run using Pytest.

---

## PART VI — REAL AIRCRAFT EXAMPLE (SURVEY MISSION)

### Chapter 39 — Survey Aircraft Design
Walkthrough of a mapping UAV designed for photogrammetry grid flights.

### Chapter 40 — Input Requirements
- Payload: `0.5` kg
- Endurance: `45` min
- Cruise speed: `95` km/h

### Chapter 41 — Design Execution
The request is routed to `FixedWingDesignPipeline`.

### Chapter 42 — Wing Results
- Span: `2.583` m
- Area: `0.667` m²
- aspect ratio: `10`

### Chapter 43 — Fuselage Results
- Length: `1.3` m
- Width: `0.2` m
- Height: `0.1` m

### Chapter 44 — Tail Results
- Conventional layout
- $S_h = 0.116$ m²
- $S_v = 0.052$ m²

### Chapter 45 — Payload Results
Sony RX1R II RGB camera, weighing `0.510` kg.

### Chapter 46 — Propulsion Results
- Motor: T-Motor AT3520
- Propeller: APC 11x7
- Battery: 6S 10000mAh

### Chapter 47 — Mass Properties
- Empty Weight: `6.74` kg
- Useful Load: `2.24` kg
- MTOW: `8.98` kg

### Chapter 48 — Performance Results
- Max Speed: `132.1` km/h
- Range: `83.9` km
- Endurance: `52.99` min

### Chapter 49 — Convergence History
Design converged in 7 iterations:
`8.989 kg -> 7.167 kg -> 8.441 kg -> 8.824 kg -> 8.940 kg -> 8.975 kg -> 8.987 kg -> 8.989 kg`

### Chapter 50 — Final Aircraft Specification
JSON output format compiles all parameters.

---

## PART VII — ENGINEERING AUDIT

### Chapter 51 — Consistency Audit
Refer to `docs/fixed_wing/audit/ENGINEERING_CONSISTENCY_AUDIT.md`.

### Chapter 52 — Suspicious/Conflicting Calculations
- Structural mass feedback loops can run out of bounds if structural factor bounds are set too high.
- Avionics and payload power calculations are static averages and do not simulate dynamic telemetry transmissions.

### Chapter 53 — Missing Features
- Detailed wing structural layout (ribs, spars, skins).
- Aerodynamic center shift with flaps deflection.

### Chapter 54 — Engineering Risks
Catalog limits constrain propeller diameters, which can result in low-pitch props running in inefficient high-speed regimes.

### Chapter 55 — Recommended Improvements
- Add custom high-pitch propellers to the database.
- Transition to a multi-point aerodynamic solver.

---

## PART VIII — DEVELOPER HANDBOOK

### Chapter 56 — Adding New Components
Add records to `motors`, `props` or `chemistries` arrays in `candidate_generator.py`.

### Chapter 57 — Adding New Mission Strategies
Implement `MissionStrategy` subclass and register in `MissionStrategyRegistry`.

### Chapter 58 — Adding New Calculations
Add to `flight_performance_engine.py` and map inside `FlightPerformanceSpecification`.

### Chapter 59 — Adding New Validation
Add constraint check functions to `optimization/constraints.py`.

### Chapter 60 — Testing New Features
Create unit tests in `tests/design/fixed_wing/` and execute `pytest`.

---

## APPENDICES

### Appendix A — Complete Folder Tree
See Chapter 3 for structure.

### Appendix B — Complete Module Index
Lists all modules within `backend/design/fixed_wing`.

### Appendix C — Function/Class Index
Lists all classes and methods generated from the AST parser in the inspection log.

### Appendix D — Data Schemas
See `models.py` in each module.

### Appendix E — Engineering Equations
Refer to Part IV for complete listing of equations.

### Appendix F — Constants and Assumptions
Gravity $g = 9.81$, air density $\rho = 1.225$ kg/m³ (at sea level).

### Appendix G — Glossary
- **AR**: Aspect Ratio
- **MTOW**: Maximum Takeoff Weight

### Appendix H — Acronyms
- **UAV**: Unmanned Aerial Vehicle
- **MDO**: Multidisciplinary Design Optimization
