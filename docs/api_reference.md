# API Reference — Fixed-Wing Design Studio
## Frozen Class Interfaces, Methods, and Return Typings

This document catalogs the public interfaces, function parameters, and return structures frozen for the `v3.0.0-fixedwing` production release.

---

## 1. FixedWingDesignPipeline

Facade class acting as the primary entry point for Fixed-Wing aircraft sizing.

- **Import**: `from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline`
- **Constructor**:
  ```python
  def __init__(
      self,
      tolerance: float = 0.01,
      max_iterations: int = 25,
      raise_on_failure: bool = False
  ) -> None
  ```
  - `tolerance`: Relative change threshold below which MTOW sizing is considered converged.
  - `max_iterations`: Maximum loop counts before failing convergence.
  - `raise_on_failure`: If True, raises exceptions on validation failures instead of return status codes.
- **Methods**:
  - `execute(self, requirements: RequirementModel) -> FixedWingDesignResult`
    - Main runner method. Executes all 13 pipeline stages sequentially.
    - **Returns**: `FixedWingDesignResult` containing individual stage results, errors, warnings list, and success flags.
  - `design_aircraft(self, requirements: RequirementModel) -> PipelineFinalAircraftSpecification`
    - Clean certified design wrapper. Raises `SizingInfeasibleError` on failures.
    - **Returns**: Consolidated certified specification.

---

## 2. VehicleRecommendationEngine

Orchestrates vehicle category selection prior to studio sizing.

- **Import**: `from backend.design.advisor.recommendation import VehicleRecommendationEngine`
- **Methods**:
  - `process_recommendation(self, requirements: RequirementModel) -> RecommendationResult`
    - Selects category recommendation (Fixed-Wing, VTOL, Multi-Rotor) and assigns confidence scores.

---

## 3. Subsystem Sizing Engines

### WingEngine
- **Import**: `from backend.design.fixed_wing.wing.wing_engine import WingEngine`
- **Methods**:
  - `process_wing_design(self, requirements: WingRequirements) -> WingResult`
    - Runs genetic optimizer or analytical candidate selection for wing loading, aspect ratio, span, and chord geometry.

### TailEngine
- **Import**: `from backend.design.fixed_wing.tail.tail_engine import TailEngine`
- **Methods**:
  - `process_tail_design(self, requirements: TailRequirements) -> TailResult`
    - Calculates horizontal and vertical tail shapes, volume coefficients, and controls.

### PropulsionEngine
- **Import**: `from backend.design.fixed_wing.propulsion.propulsion_engine import PropulsionEngine`
- **Methods**:
  - `process_propulsion_design(self, requirements: PropulsionRequirements) -> PropulsionResult`
    - Runs co-optimization search pairing brushless motors with propeller pitches and ESC ratings.

---

## 4. VerificationEngine

Safety audit engine enforcing certification compliance strategies.

- **Import**: `from backend.design.fixed_wing.verification.verification_engine import VerificationEngine`
- **Methods**:
  - `process_verification(self, requirements: VerificationRequirements, profile: VerificationProfile | None = None) -> VerificationResult`
    - Checks stability margins, component clearances, and structural violations.
    - **Returns**: `VerificationResult` containing safety compliance percentages, warning messages, and mitigations.
