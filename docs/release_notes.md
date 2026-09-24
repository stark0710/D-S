# Release Notes — Torq Wings Design Studio V3
## Production Release Tag: v3.0.0-fixedwing

We are proud to announce the official production freeze and release of the **Fixed-Wing Design Studio** (v3.0.0-fixedwing) reference implementation. This release establishes a hardened, deterministic, and physically consistent sizing framework for fixed-wing UAV design.

---

## 1. Release Overview

Torq Wings V3 Fixed-Wing Design Studio is a complete aircraft synthesis engine. It iterates through vehicle configuration selection, geometry optimization, propulsion sizing, electrical routing, mass balances, CG tracking, and performance assessments. Sizing cycles terminate in a fully converged state (MTOW delta <= 1%) or fail gracefully with detailed diagnostic statuses.

### Key Highlights
- **100% Deterministic Execution**: Running the pipeline with identical input parameters yields mathematically identical designs.
- **Hardened Sizing Loop**: Solvers terminate within iteration limits, avoiding hangs, oscillations, or crashes.
- **Hardened Failure Taxonomy**: Sizing failures are mapped to 12 distinct failure categories to enable granular engineering diagnostics.
- **Robust Verification & Safety Gate**: Sized designs are audited by `VerificationEngine` checking structural clearances, stability limits, and flight margins before certification.

---

## 2. Version History

- **v1.0.0 — Basic Sizing**: Initial point-mass sizing equations and single-stage calculations.
- **v2.0.0 — Multistage Sizer**: Added configuration selection, propeller catalogs, and basic convergence loops.
- **v3.0.0-fixedwing (Current)**:
  - Consolidated 13-stage sizing pipeline under `FixedWingDesignPipeline`.
  - Added joint propulsion search (co-optimizing motor, propeller, and ESC).
  - Integrated `VerificationEngine` with Strategy Registry for automated certification checks.
  - Hardened error taxonomy for production freeze.
  - Successfully passed a 1000-mission validation campaign.

---

## 3. Known Limitations

- **Telemetry Catalog Limits**: The current catalog does not support communication ranges beyond 80 km (Silvus StreamCaster Lite limit). Requests for ranges > 80 km will fail with `Component Database Limitation`.
- **Vertical Takeoff/Landing (VTOL)**: This package is specialized for conventional fixed-wing aircraft (Runway, Catapult, Hand Launch takeoff / Runway, Belly landing, Parachute, Net landing). VTOL-hybrid configurations (e.g. QuadPlanes) are not supported in this release.
- **Payload Catalog Options**: Extremely strict weight margins (e.g., structural payload weight limit < 0.51 kg) can cause sizing failures for camera payloads as the lightest camera (RGB Camera) weighs exactly 0.51 kg.

---

## 4. Migration Notes

- **Pipeline Execution**: Migrated from calling `ConvergenceManager` directly to invoking the centralized `FixedWingDesignPipeline` facade class.
- **Exception Handling**: By default, `execute()` returns a `FixedWingDesignResult` with success/failure flags and status enums, preventing application crashes. Use `raise_on_failure=True` or `design_aircraft()` to raise exceptions.

---

## 5. Roadmap

- **Hybrid-VTOL Sizing Integration**: Integrate multi-rotor vertical lift system engines into the convergence loop.
- **CAD Query Automation**: Re-enable automatic CAD exports using updated step files generation.
- **Advanced Battery Models**: Incorporate battery thermal degradation and transient voltage drops under peak climbs.
