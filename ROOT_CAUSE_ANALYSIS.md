# Forensic Root-Cause Analysis: Fixed-Wing Design Pipeline Validation

**Status**: Analysis Complete (Zero Code/Database/Equation Modifications Made)  
**Date**: September 13, 2026  
**Scope**: TorqWings Studio v2 — Fixed-Wing Backend Pipeline  
**Regression Baselines**: Run 182503 (SURVEY 0.5 kg), Run 192340 (SURVEY 1.0 kg), Run 191330 (AGRICULTURE 2.0 kg)

---

## 1. Executive Summary

A comprehensive forensic audit of the Fixed-Wing design pipeline was conducted across 10 manual validation runs executed on September 13, 2026. The test cases covered diverse operational envelopes including Survey, Military, Delivery, Security, Agriculture, Inspection, Research, and Training.

The investigation revealed that the failures and inconsistencies observed across the validation suite are **not** due to unsolvable aerodynamic physics or genuine UAV infeasibility. Rather, they stem from a combination of:
1. **Misaligned Requirement Mapping & Strategy Selection**: Tactical low-altitude surveillance missions (Security, Inspection, Military) are routed into an extreme sailplane `Long Endurance` strategy, enforcing aspect ratios ($AR = 16$) and elliptical planforms that cause wing chords to shrink below physical fuselage clearance limits.
2. **Catalog vs. Custom Payload Modeling**: A hardcoded 7-item payload catalog lacks intermediate sensor/cargo records and lacks generic payload synthesis, rejecting valid user requirements (Training, Research, Delivery).
3. **Stale Data Propagation in Convergence**: `IterationController` fails to update `context.requirements.payload_result` during convergence, causing downstream verification to clash converged fuselages against pre-convergence 25 kg airframe bays (producing 88% compliance and contradictory verdicts).
4. **Uncoordinated Dual-Engine Verification**: `VerificationCertificationStage` uses one verifier for gating (`CommonVerificationEngine`) and another for reporting (`FWVerificationEngine`), allowing an aircraft with failed clearance to report `SUCCESS` and `PASS`.
5. **MTOW Variable Overwriting**: Continuous mutation and relaxation of MTOW constraints across pipeline stages creates artificial verification bounds that contradict user inputs.
6. **Additive Payload Mass Accounting**: An in-loop hardcoded 0.500 kg "Mission Equipment" component is unconditionally added to `installed_payload_mass_kg`, inflating payload weight by 50% on a 1.0 kg specification.
7. **Flat-vs-Nested Attribute Serialization**: Reporting utilities look for propulsion metrics (`static_thrust_n`, `thrust_to_weight_ratio`) on top-level objects rather than within nested `thrust_analysis` containers, resulting in `N/A` outputs.
8. **Static Configuration Rationale**: Strategies return hardcoded text describing default archetypes (e.g. Twin-Boom Pusher) even when fallback candidate selection chooses a Single Tractor layout.
9. **Multi-Variable Convergence Lag**: Iteration continues after MTOW stabilizes because `ConvergenceChecker` enforces a 10-dimensional vector (requiring flight range to stabilize within 0.2 km), while the output table only displays MTOW.

---

## 2. Master Issue Table

| Issue | Test Case(s) | Severity | Responsible Module | File | Function | Root Cause | Proposed Smallest Safe Correction |
|---|---|---|---|---|---|---|---|
| **A. Wing Chord Infeasibility** | SECURITY (0.5 kg), INSPECTION (0.5 kg), MILITARY (2.0 kg) | **CRITICAL (Blocker)** | Wing & Mission Strategies | `backend/design/fixed_wing/mission/mission_registry.py`<br>`backend/design/fixed_wing/wing/wing_strategy.py`<br>`backend/design/fixed_wing/wing/wing_sizer.py` | `MissionStrategyRegistry.get`<br>`LongEnduranceWingStrategy.get_target_aspect_ratio`<br>`WingSizer.size_wing` | Tactical surveillance mapped to $AR=16$ glider with elliptical planform; root chord shrinks below payload width floor ($0.11\text{ m} < 0.12\text{ m}$). | Register `SurveillanceWingStrategy` with tactical $AR \approx 8.0\text{--}9.0$ tapered planform; enforce geometric root chord floor against fuselage clearance. |
| **B. Payload Catalog Limitations** | RESEARCH (0.8 kg), TRAINING (0.2 kg), DELIVERY (1.0 kg) | **HIGH (Blocker)** | Payload Engine | `backend/design/fixed_wing/payload/payload_selector.py`<br>`backend/design/fixed_wing/payload/payload_engine.py` | `PayloadSelector.select_payload`<br>`PayloadEngine.process_payload_design` | Hardcoded 7-item catalog lacks lightweight sensors; cargo forces discrete item lookup rather than user payload mass. | Add lightweight catalog items (FPV cameras, research probes, cargo sizes); support generic/custom synthesized payload when no discrete item fits. |
| **C1. Delivery 88% Compliance Failure** | DELIVERY (3.0 kg, Run 185803) | **HIGH (Pipeline Halt)** | Convergence & Verification | `backend/design/fixed_wing/convergence/iteration_controller.py`<br>`backend/design/fixed_wing/verification/component_checker.py`<br>`backend/design/fixed_wing/pipeline/fixed_wing_pipeline.py` | `IterationController.run_iteration`<br>`ComponentChecker.check_subsystem_compatibility`<br>`FixedWingDesignPipeline.execute` | `IterationController` does not update `context.requirements.payload_result`; verification checks converged fuselage against pre-loop 25 kg bay. | Update `derived_variables["payload_result"]` in in-loop payload optimizer; map `VerificationValidationError` to `VERIFICATION_FAILED` instead of `INTERNAL_EXCEPTION`. |
| **C2. Operating Environment Mismatch** | DELIVERY, MILITARY (Requested COASTAL) | **MEDIUM (Correctness)** | Pipeline Mission Translation | `backend/design/fixed_wing/pipeline/pipeline_stage.py` | `MissionTranslationStage.execute` | `env_map` lacks `OperatingEnvironment.COASTAL`, falling back silently to `EnvironmentType.RURAL`. | Add `OperatingEnvironment.COASTAL: EnvironmentType.MARINE` to `env_map`. |
| **D. Contradictory Statuses** | AGRICULTURE (2.0 kg, Run 191330) | **HIGH (Integrity)** | Pipeline Stage & Reporting | `backend/design/fixed_wing/pipeline/pipeline_stage.py`<br>`scripts/run_fixed_wing_pipeline.py` | `VerificationCertificationStage.execute`<br>`save_markdown_report` | Gating checks `CommonVerificationEngine` (PASS), while reporting displays `FWVerificationEngine` (FAILED); verdict ignores domain verifier status. | Require both verifiers to pass; resolve underlying stale component clash; gate final PASS verdict on domain verification. |
| **E. MTOW Discrepancies** | All cases with unspecified MTOW | **MEDIUM (Consistency)** | Mission Translation & Convergence | `backend/design/fixed_wing/pipeline/pipeline_stage.py`<br>`backend/design/common/verification/rules/mass_properties_rule.py` | `MissionTranslationStage.execute`<br>`AircraftConvergenceStage.execute`<br>`MassPropertiesRule.evaluate` | Loose MTOW overrides ($25\text{ kg}$) and heuristic seeds ($2.5 \times \text{payload}$) overwrite requirements; verification enforces synthetic bounds. | Keep user requirement unpolluted; store sizing seeds in dedicated attributes; only enforce MTOW limits if explicitly set by user. |
| **F. Additive Payload Mass Accounting** | All cases (e.g. SURVEY 1.0 kg $\to$ 1.5 kg) | **MEDIUM (Mass Accounting)** | Mass Properties Optimization | `backend/design/fixed_wing/mass_properties/optimization/candidate_evaluator.py` | `MassCandidateEvaluator.evaluate` | Hardcoded 0.500 kg "Mission Equipment" added unconditionally on top of `installed_payload_mass_kg`. | Allocate mission equipment within total payload allowance or do not add separate mass if already accounted. |
| **G. Lost Propulsion Outputs** | All reports & terminal output | **LOW (Reporting)** | Pipeline Runner / Serializer | `scripts/run_fixed_wing_pipeline.py` | `print_terminal_summary`<br>`save_markdown_report` | Lookup checks `pr.static_thrust_n` instead of nested `pr.thrust_analysis.estimated_static_thrust_n`. | Inspect `pr.thrust_analysis` for thrust and T/W ratio before falling back to top-level attributes. |
| **H. Configuration Rationale Mismatch** | Cases with fallback layout (e.g. Tractor chosen) | **LOW (Reporting)** | Configuration Strategy | `backend/design/fixed_wing/configuration/configuration_strategy.py` | `get_engineering_rationale` | Strategy returns hardcoded string describing preferred archetype (Twin-Boom Pusher) regardless of actual layout. | Parameterize rationale generation using actual keys in `selected_configuration`. |
| **I. Convergence Iteration Lag** | Converged cases (SURVEY 0.5 kg, SURVEY 1.0 kg) | **LOW (Clarity)** | Convergence Checker & Stage | `backend/design/fixed_wing/convergence/convergence_checker.py`<br>`backend/design/fixed_wing/pipeline/pipeline_stage.py` | `ConvergenceChecker.check_convergence`<br>`AircraftConvergenceStage.execute` | Engine checks 10 variables (range lags mass by 1-2 steps); report only prints MTOW and uses 1D MTOW evaluator for table. | Reconstruct iteration table with multi-variable metrics or clarify performance convergence settling in report. |

---

## 3. Detailed Forensic Trace for Every Issue

### Issue A: Wing Root Chord Infeasibility (SECURITY / INSPECTION / MILITARY)

#### 1. Pipeline Stages Responsible
- `MissionTranslationStage` (Stage 1)
- `MissionEngine` / `MissionStrategyRegistry` (Mission Analysis)
- `WingPlanformOptimizationStage` (Stage 4)
- `FuselageOptimizationStage` (Stage 5)

#### 2. Exact Files and Functions Responsible
- `backend/design/fixed_wing/pipeline/pipeline_stage.py`: [MissionTranslationStage.execute](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/pipeline/pipeline_stage.py#L72-L137)
- `backend/design/fixed_wing/mission/mission_registry.py`: [MissionStrategyRegistry](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/mission/mission_registry.py#L57-L68)
- `backend/design/fixed_wing/mission/mission_analyzer.py`: [MissionAnalyzer.analyze_mission](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/mission/mission_analyzer.py#L64-L67)
- `backend/design/fixed_wing/wing/wing_strategy.py`: [LongEnduranceWingStrategy](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/wing/wing_strategy.py#L75-L96)
- `backend/design/fixed_wing/wing/wing_planform.py`: [PlanformGeometryService.calculate_planform_dimensions](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/wing/wing_planform.py#L75-L83)
- `backend/design/fixed_wing/fuselage/fuselage_sizer.py`: [FuselageSizer.size_fuselage_envelope](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/fuselage/fuselage_sizer.py#L57-L63)
- `backend/design/fixed_wing/fuselage/fuselage_validator.py`: [FuselageValidator.validate](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/fuselage/fuselage_validator.py#L69-L75)

#### 3. Complete Trace
1. **Input**: `RequirementModel(mission_type=MissionType.SECURITY, payload_weight_kg=0.5, cruise_speed_kmh=80.0, target_flight_time_min=30.0, target_range_km=30.0)`
2. **Translation**: `cat_map` maps `MissionType.SECURITY` $\to$ `MissionCategory.SURVEILLANCE`.
3. **Mission Strategy Selection**: `MissionStrategyRegistry.get(MissionCategory.SURVEILLANCE)` has no dedicated surveillance strategy; it aliases `MissionCategory.SURVEILLANCE` to `LongEnduranceMissionStrategy`.
4. **Category Mutation**: In `MissionAnalyzer.analyze_mission` (line 66), `profile = MissionProfile(mission_category=strategy.category, ...)` overwrites the mission category from `SURVEILLANCE` to `LONG_ENDURANCE`.
5. **Wing Sizing**:
   - `WingEngine` retrieves strategy for `"long endurance"` $\to$ `LongEnduranceWingStrategy`.
   - `LongEnduranceWingStrategy.get_target_aspect_ratio()` enforces $AR = 16.0$ (sailplane glider ratio).
   - `LongEnduranceWingStrategy.get_planform_type()` enforces `PlanformType.ELLIPTICAL`.
   - Initial MTOW: $m_{\text{est}} = \max(1.5, 0.5 \times 2.5) = 1.50\text{ kg}$.
   - Wing loading at $V_{\text{stall}} = 45\text{ km/h}$: $W/S = 13.46\text{ kg/m}^2$.
   - Reference area: $S = 1.50 / 13.46 = 0.1114\text{ m}^2$.
   - Wingspan: $b = \sqrt{S \cdot AR} = \sqrt{0.1114 \times 16} = 1.335\text{ m}$.
   - Elliptical root chord formula: $c_{\text{root}} = \frac{4 S}{\pi b} = \frac{4 \times 0.1114}{\pi \times 1.335} = 0.1062\text{ m} \approx 0.11\text{ m}$.
6. **Fuselage Sizing**:
   - `FuselageSizer.size_fuselage_envelope`:
     $$\text{min\_payload\_width} = 0.08 + 0.005 \times 0.5 = 0.0825\text{ m}$$
     $$\text{min\_width} = \text{min\_payload\_width} + 2 \times \text{clearance\_margin} = 0.0825 + 2 \times 0.02 = 0.1225\text{ m} \approx 0.12\text{ m}$$
     $$w_{\text{fuse}} = \max(0.1225, \dots) = 0.12\text{ m}$$
7. **Feasibility Validation**:
   - `FuselageValidator.validate`:
     `if geometry.width_m (0.12 m) > wing_geom.root_chord_m (0.11 m):`
     Raises `FuselageValidationError`:
     `"Sized fuselage width (0.12 m) exceeds wing root chord (0.11 m), which causes extreme aerodynamic blockage and drag. Select a more slender fuselage profile."`
8. **Result**: `FixedWingDesignPipeline.execute` catches `SizingInfeasibleError`, sets `status = SIZING_INFEASIBLE`, `success = False`, `converged = False`.

#### 4. Problem Classification
- **Incorrect Requirement Propagation & Strategy Aliasing**: Short-range tactical security/inspection (30 min endurance) is improperly treated as a high-altitude, long-endurance sailplane ($AR = 16$).
- **Lack of Multi-Disciplinary Geometric Coupling**: The wing planform optimizer has no geometric awareness of the physical clearance floor demanded by internal fuselage payload bays.

#### 5. Relevant Code Snippets
```python
# backend/design/fixed_wing/mission/mission_registry.py:61
MissionStrategyRegistry.register(MissionCategory.SURVEILLANCE, LongEnduranceMissionStrategy)  # Endurance handles Surveillance

# backend/design/fixed_wing/wing/wing_strategy.py:83, 91
def get_target_aspect_ratio(self) -> float:
    return 16.0  # High AR glider wings

def get_planform_type(self, requirements: WingRequirements) -> PlanformType:
    return PlanformType.ELLIPTICAL  # Minimizes induced drag

# backend/design/fixed_wing/fuselage/fuselage_validator.py:70-74
if geometry.width_m > wing_geom.root_chord_m:
    errors.append(
        f"Sized fuselage width ({geometry.width_m:.2f} m) exceeds wing root chord ({wing_geom.root_chord_m:.2f} m), "
        "which causes extreme aerodynamic blockage and drag. Select a more slender fuselage profile."
    )
```

#### 6. Proposed Safe Correction
1. **Mission/Wing Strategy Separation**: In `MissionStrategyRegistry` and `WingStrategyRegistry`, decouple `SURVEILLANCE` from `LongEnduranceMissionStrategy`. Register a dedicated `SurveillanceMissionStrategy` and `SurveillanceWingStrategy` characterized by tactical surveillance parameters ($AR \approx 8.0\text{--}9.5$, `PlanformType.TAPERED`, $\lambda = 0.6$). For $S = 0.1114\text{ m}^2$ and $AR = 8.5$:
   $$b = \sqrt{0.1114 \times 8.5} = 0.973\text{ m}$$
   $$c_{\text{root}} = \frac{2 S}{b (1 + \lambda)} = \frac{2 \times 0.1114}{0.973 \times 1.6} = 0.143\text{ m} > 0.12\text{ m}$$
   This completely clears the fuselage width boundary with healthy margin.
2. **Geometric Chord Coupling**: In `WingSizer.size_wing`, add an aerodynamic clearance coupling rule: when $S$ is small, cap aspect ratio such that $c_{\text{root}} \ge w_{\text{fuse,min}} \times 1.15$.
3. **Do NOT disable the check in `FuselageValidator`**: The physical rule that a fuselage cannot be wider than the wing root chord is structurally and aerodynamically sound.

#### 7. Invariants to Preserve
- True high-altitude long-endurance platforms with large wing areas ($S > 0.6\text{ m}^2$) must retain $AR = 16$ gliders.
- Baseline SURVEY and AGRICULTURE wing geometries must remain unchanged.

---

### Issue B: Payload Catalog Limitations (RESEARCH / TRAINING / DELIVERY)

#### 1. Pipeline Stages Responsible
- `PayloadPackagingStage` (Stage 6)

#### 2. Exact Files and Functions Responsible
- `backend/design/fixed_wing/payload/payload_selector.py`: [PayloadSelector.select_payload](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/payload/payload_selector.py#L40-L72)
- `backend/design/fixed_wing/payload/payload_engine.py`: [PayloadEngine.process_payload_design](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/payload/payload_engine.py#L74-L87)

#### 3. Complete Trace
1. **Input**:
   - RESEARCH: `payload_weight_kg = 0.8 kg`
   - TRAINING: `payload_weight_kg = 0.2 kg`
   - DELIVERY: `payload_weight_kg = 1.0 kg`
2. **Constraint Formulation**:
   In `PayloadEngine`:
   $$\text{max\_payload\_weight\_kg} = m_{\text{profile.payload\_kg}} \times 1.05$$
   - Research: $0.80 \times 1.05 = 0.84\text{ kg}$
   - Training: $0.20 \times 1.05 = 0.21\text{ kg}$
   - Delivery: $1.00 \times 1.05 = 1.05\text{ kg}$
3. **Type Selection**:
   - `ResearchPayloadStrategy` selects `PayloadType.SCIENTIFIC`.
   - `TrainingPayloadStrategy` selects `PayloadType.RGB_CAMERA`.
   - `CargoPayloadStrategy` selects `PayloadType.CARGO`.
4. **Database Query**:
   `PayloadSelector._payloads` contains only 7 items:
   - `SCIENTIFIC`: "Agricultural Spray Tank System" ($1.80\text{ kg}$)
   - `RGB_CAMERA`: "Sony RX1R II" ($0.51\text{ kg}$)
   - `CARGO`: "Standard Cargo Box Package" ($2.00\text{ kg}$)
5. **Rejection**:
   In `PayloadSelector.select_payload`:
   ```python
   candidates = [p for p in self._payloads if p.payload_type == target_type and p.weight_kg <= max_weight_kg]
   ```
   For all three runs, `candidates` is empty. The function queries `all_of_type`, finds the single entry, and raises:
   - Research: `COMPONENT_DATABASE_LIMITATION: Lightest available component of type 'Scientific Instruments' in database weighs 1.80 kg, which exceeds the maximum allowed structural payload limit of 0.84 kg.`
   - Training: `COMPONENT_DATABASE_LIMITATION: Lightest available component of type 'RGB Camera' in database weighs 0.51 kg, which exceeds the maximum allowed structural payload limit of 0.21 kg.`
   - Delivery: `COMPONENT_DATABASE_LIMITATION: Lightest available component of type 'Cargo' in database weighs 2.00 kg, which exceeds the maximum allowed structural payload limit of 1.05 kg.`
6. **Result**: Caught in `fixed_wing_pipeline.py` and mapped to `PipelineStatus.COMPONENT_DATABASE_LIMITATION`.

#### 4. Problem Classification
- **Database Limitation**: The hardcoded catalog has zero lightweight sub-components ($< 0.5\text{ kg}$ cameras, $< 1.8\text{ kg}$ scientific sensors, $< 2.0\text{ kg}$ cargo).
- **Incorrect Constraint Handling**: Cargo missions represent user parcel weight, not a discrete avionics sensor; requiring a pre-existing catalog item for arbitrary delivery masses violates cargo domain principles.

#### 5. Relevant Code Snippets
```python
# backend/design/fixed_wing/payload/payload_selector.py:40-48
_payloads: List[PayloadRecord] = [
    PayloadRecord("Sony RX1R II (RGB)", PayloadType.RGB_CAMERA, 0.51, 15.0, 5.0, [113, 72, 74]),
    PayloadRecord("MicaSense RedEdge (Multispectral)", PayloadType.MULTISPECTRAL, 0.35, 8.0, 2.0, [87, 59, 45.4]),
    PayloadRecord("FLIR Duo Pro R (Thermal)", PayloadType.THERMAL, 0.22, 12.0, 4.0, [87, 82, 69]),
    PayloadRecord("Velodyne VLP-16 (LiDAR)", PayloadType.LIDAR, 0.83, 10.0, 8.0, [103, 103, 72]),
    PayloadRecord("Agricultural Spray Tank System", PayloadType.SCIENTIFIC, 1.8, 12.0, 0.5, [250, 120, 120]),
    PayloadRecord("Standard Cargo Box Package", PayloadType.CARGO, 2.0, 0.0, 0.0, [180, 100, 100]),
    PayloadRecord("MetSens Environmental Probe", PayloadType.ENV_SENSORS, 0.15, 2.0, 0.1, [60, 40, 30]),
]
```

#### 6. Proposed Safe Correction
1. **Catalog Expansion**: Enrich `_payloads` with standard UAV payload items:
   - `RGB_CAMERA`: Micro FPV/Action Cam ($0.08\text{ kg}$, $3\text{ W}$), Compact Mapping Cam ($0.20\text{ kg}$, $6\text{ W}$).
   - `SCIENTIFIC`: Atmospheric Mini-Sonde ($0.30\text{ kg}$, $4\text{ W}$), Compact Spectrometer ($0.75\text{ kg}$, $8\text{ W}$).
   - `CARGO`: Modular Courier Pack ($0.50\text{ kg}$, $1.00\text{ kg}$).
2. **Generic / User-Defined Cargo Synthesis**: For `PayloadType.CARGO` (or when user specifies explicit non-catalog payload masses), `PayloadSelector` should synthesize a generic payload item scaled to `m_profile.payload_kg` with standard courier box density ($150\text{ kg/m}^3$) when no exact catalog match exists.
3. **Do NOT remove the validation check**: If a user mission requires LiDAR ($0.83\text{ kg}$) on a $0.3\text{ kg}$ payload UAV, the database limit check must still catch and reject it.

#### 7. Invariants to Preserve
- Existing runs matching Sony RX1R II (0.51 kg), MicaSense RedEdge (0.35 kg), or Spray Tank (1.8 kg) must retain their exact component selections.

---

### Issue C: DELIVERY 88% Compliance Failure & Environment Mismatch

#### 1. Pipeline Stages Responsible
- Part 1 (88% Failure): `AircraftConvergenceStage` (Stage 13), `VerificationCertificationStage` (Stage 14)
- Part 2 (Environment): `MissionTranslationStage` (Stage 1)

#### 2. Exact Files and Functions Responsible
- Part 1 (88% Failure):
  - `backend/design/fixed_wing/pipeline/pipeline_stage.py`: [AircraftConvergenceStage.execute](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/pipeline/pipeline_stage.py#L683-L703)
  - `backend/design/fixed_wing/convergence/iteration_controller.py`: [IterationController.run_iteration](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/convergence/iteration_controller.py#L59-L69)
  - `backend/design/fixed_wing/payload/optimization/candidate_evaluator.py`: `CandidateEvaluator.evaluate` (omits `payload_result`)
  - `backend/design/fixed_wing/verification/component_checker.py`: [ComponentChecker.check_subsystem_compatibility](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/verification/component_checker.py#L26-L30)
  - `backend/design/fixed_wing/verification/verification_validator.py`: [VerificationValidator.validate](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/verification/verification_validator.py#L46-L50)
  - `backend/design/fixed_wing/pipeline/fixed_wing_pipeline.py`: [FixedWingDesignPipeline.execute](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/pipeline/fixed_wing_pipeline.py#L309-L311)
- Part 2 (Environment):
  - `backend/design/fixed_wing/pipeline/pipeline_stage.py`: [MissionTranslationStage.execute](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/pipeline/pipeline_stage.py#L104-L113)

#### 3. Complete Trace
##### Part 1: The 88.0% Compliance Crash
1. **Input**: `RequirementModel(mission_type=DELIVERY, payload_weight_kg=3.0, cruise_speed_kmh=80.0, target_flight_time_min=30.0, target_range_km=30.0)`
2. **Pre-Convergence Stages**:
   - In `MissionTranslationStage`, MTOW constraint is set to `25.0 kg`.
   - Pre-loop `WingPlanformOptimizationStage` and `FuselageOptimizationStage` size an airframe assuming $25.0\text{ kg}$ MTOW:
     Fuselage length $= 2.6\text{ m}$, width $= 0.298\text{ m}$, payload bay width $= 0.278\text{ m}$.
   - Pre-loop `PayloadPackagingStage` sizes `payload_result.payload_layout`:
     `compartment_width_m = 0.278 m` (stored in `context.payload_result`).
3. **Convergence Loop Execution**:
   - `AircraftConvergenceStage` executes `ConvergenceManager`.
   - `IterationController.run_iteration` executes the 9 subsystem optimizers.
   - `FuselageOptimizer` resizes the fuselage for the actual converged MTOW ($7.5\text{ kg}$):
     Fuselage width shrinks to $w = 0.150\text{ m}$, payload bay width shrinks to $0.120\text{ m}$.
     `context.requirements.fuselage_result` is updated to width $= 0.150\text{ m}$.
   - However, in `IterationController.run_iteration:65-68`:
     ```python
     if hasattr(context.requirements, "payload_result") and payload_res.winning_candidate:
         geom_result = payload_res.winning_candidate.derived_variables.get("payload_result")
         if geom_result:
             context.requirements.payload_result = geom_result
     ```
     `PayloadPackagingOptimizer`'s `CandidateEvaluator` never populates `derived_variables["payload_result"]`!
     `geom_result` is `None`. `context.requirements.payload_result` is **never updated during the entire convergence loop**!
   - When convergence completes (lines 694–702 of `pipeline_stage.py`), `context.payload_result = pipeline_reqs.payload_result` copies the stale pre-loop payload layout (`compartment_width_m = 0.278 m`).
4. **Verification Stage Failure**:
   - `VerificationCertificationStage` executes `ComponentChecker.check_subsystem_compatibility`:
     ```python
     if pay_res.payload_layout.compartment_width_m > f_geom.width_m:
     # 0.278 m > 0.150 m  --> True!
     ```
     Generates violation: `"Component clash: Payload compartment width (0.28 m) is wider than the fuselage width (0.15 m)."`.
   - `VerificationEngine` calculates compliance score:
     $$\text{compliance\_pct} = 100.0 - (1 \times 12.0) = 88.0\%$$
   - In `CargoVerificationStrategy`, `min_compliance_pct = 90.0%`.
   - `VerificationValidator.validate` checks $88.0\% < 90.0\%$ and raises `VerificationValidationError`:
     `"Design compliance score (88.0%) is below the minimum required safety compliance boundary (90.0%)."`
5. **Exception Misclassification**:
   - `VerificationValidationError` subclasses `ValueError`.
   - `FixedWingDesignPipeline.execute` specifically catches `VerificationFailedError`, but `VerificationValidationError` falls into `except Exception as e: status = PipelineStatus.INTERNAL_EXCEPTION`.

##### Part 2: Operating Environment COASTAL $\to$ RURAL
1. User supplies `req.environment = OperatingEnvironment.COASTAL`.
2. In `MissionTranslationStage.execute:104-113`:
   ```python
   env_map = {
       OperatingEnvironment.RURAL: EnvironmentType.RURAL,
       OperatingEnvironment.URBAN: EnvironmentType.URBAN,
       OperatingEnvironment.FOREST: EnvironmentType.FOREST,
       OperatingEnvironment.MOUNTAIN: EnvironmentType.MOUNTAIN,
       OperatingEnvironment.DESERT: EnvironmentType.DESERT,
       OperatingEnvironment.MARINE: EnvironmentType.MARINE,
   }
   env = env_map.get(req.environment, EnvironmentType.RURAL)
   ```
3. `OperatingEnvironment.COASTAL` is absent from `env_map`. The `.get()` call falls back to `EnvironmentType.RURAL`.
4. The generated `MissionRequirements.environment` is stored as `RURAL`.

#### 4. Problem Classification
- **Issue C1**: Stale state propagation across convergence loop + exception hierarchy mapping bug.
- **Issue C2**: Incomplete enum translation mapping.

#### 5. Relevant Code Snippets
```python
# backend/design/fixed_wing/convergence/iteration_controller.py:65-68
if hasattr(context.requirements, "payload_result") and payload_res.winning_candidate:
    geom_result = payload_res.winning_candidate.derived_variables.get("payload_result")
    if geom_result:
        context.requirements.payload_result = geom_result  # NEVER EXECUTES (geom_result is None)

# backend/design/fixed_wing/pipeline/pipeline_stage.py:104-112
env_map = {
    OperatingEnvironment.RURAL: EnvironmentType.RURAL,
    OperatingEnvironment.URBAN: EnvironmentType.URBAN,
    OperatingEnvironment.FOREST: EnvironmentType.FOREST,
    OperatingEnvironment.MOUNTAIN: EnvironmentType.MOUNTAIN,
    OperatingEnvironment.DESERT: EnvironmentType.DESERT,
    OperatingEnvironment.MARINE: EnvironmentType.MARINE,
}
env = env_map.get(req.environment, EnvironmentType.RURAL)  # COASTAL -> RURAL
```

#### 6. Proposed Safe Correction
1. **Regenerate Payload Layout in Loop**: In `PayloadPackagingOptimizer.build_specification` (or in `IterationController`), update `payload_layout.compartment_width_m`, `compartment_length_m`, and `compartment_height_m` to match the latest converged `fuselage_result.fuselage_geometry`.
2. **Exception Handling**: In `FixedWingDesignPipeline.execute`, add an explicit handler for `VerificationValidationError` to assign `status = PipelineStatus.VERIFICATION_FAILED`.
3. **Enum Mapping**: In `MissionTranslationStage`, add:
   ```python
   OperatingEnvironment.COASTAL: EnvironmentType.MARINE,
   ```

#### 7. Invariants to Preserve
- Legitimate component clashes (when physical equipment dimensions exceed fuselage envelope) must continue to trigger `Component clash` violations.

---

### Issue D: Contradictory Statuses (AGRICULTURE)

#### 1. Pipeline Stages Responsible
- `VerificationCertificationStage` (Stage 14)
- Pipeline Runner / Report Serializer (`scripts/run_fixed_wing_pipeline.py`)

#### 2. Exact Files and Functions Responsible
- `backend/design/fixed_wing/pipeline/pipeline_stage.py`: [VerificationCertificationStage.execute](file:///c:/Users/acer/Documents/torqwings studio v2/backend/design/fixed_wing/pipeline/pipeline_stage.py#L757-L820)
- `backend/design/fixed_wing/pipeline/fixed_wing_pipeline.py`: [FixedWingDesignPipeline.execute](file:///c:/Users/acer/Documents/torqwings studio v2/backend/design/fixed_wing/pipeline/fixed_wing_pipeline.py#L256-L258, L353-L358)
- `scripts/run_fixed_wing_pipeline.py`: [save_markdown_report](file:///c:/Users/acer/Documents/torqwings studio v2/scripts/run_fixed_wing_pipeline.py#L721-L734, L755-L766)

#### 3. Complete Trace
1. **Input**: `RequirementModel(mission_type=AGRICULTURE, payload_weight_kg=2.0, ...)`
2. Pipeline converges successfully at MTOW $= 6.136\text{ kg}$ across 5 iterations.
3. In `VerificationCertificationStage`:
   - Executes `fw_verifier.process_verification(fw_reqs)`.
   - `FWVerificationEngine` detects the exact same stale payload bay mismatch from Issue C:
     `"Component clash: Payload compartment width (0.20 m) is wider than the fuselage width (0.15 m)."`
   - `fw_res.verification_status` is set to `"FAILED"`, and `fw_res.mission_status` is set to `"Deficient"`.
   - `context.verification_result = fw_res`.
   - Next, executes `common_verifier.verify_aircraft(...)`.
   - `CommonVerificationEngine` evaluates cross-vehicle rules (mass properties, propulsion bounds, safety margins) and returns `report.overall_status = "CERTIFIED"`.
   - Lines 814–820 check:
     ```python
     if report.overall_status not in ("CERTIFIED", "CERTIFIED_WITH_WARNINGS"):
         raise VerificationFailedError(...)
     ```
     Because `report.overall_status == "CERTIFIED"`, **no exception is raised**.
4. In `FixedWingDesignPipeline.execute`:
   - Stage completes without error $\to$ `status = PipelineStatus.SUCCESS`, `res.success = True`, `res.converged = True`.
   - `res.verification_result` is assigned `fw_res` (`verification_status = "FAILED"`).
5. In `save_markdown_report`:
   - Section 1: reports `Success: True`, `Status: SUCCESS`, `Converged: True`.
   - Section 13: reports `Verification Status: FAILED`, `Mission Requirements Satisfied: Deficient`.
   - Section 16 (Final Verdict): checks `if res.success and res.converged:`, so it prints:
     `### **VERDICT: PASS — FULLY CONVERGED & FEASIBLE AIRCRAFT**`

#### 4. Problem Classification
- **Inconsistent Verification Logic / Architectural Decoupling**: The gating logic checks one verifier (`CommonVerificationEngine`), while reporting an un-gated second verifier (`FWVerificationEngine`), yielding polar-opposite statuses in the same report.

#### 5. Relevant Code Snippets
```python
# backend/design/fixed_wing/pipeline/pipeline_stage.py:757, 804, 815
fw_res = fw_verifier.process_verification(fw_reqs)
context.verification_result = fw_res  # fw_res.verification_status == "FAILED"
...
report = common_verifier.verify_aircraft(...)
context.certification_report = report  # report.overall_status == "CERTIFIED"
...
# Only report is checked! fw_res is ignored!
if report.overall_status not in ("CERTIFIED", "CERTIFIED_WITH_WARNINGS"):
    raise VerificationFailedError(...)
```

#### 6. Proposed Safe Correction
1. **Coupled Verification Gate**: In `VerificationCertificationStage`, enforce that both verifiers agree:
   ```python
   fw_passed = fw_res.verification_status in ("VERIFIED", "VERIFIED_WITH_WARNINGS")
   common_passed = report.overall_status in ("CERTIFIED", "CERTIFIED_WITH_WARNINGS")
   if not (fw_passed and common_passed):
       raise VerificationFailedError("Aircraft failed verification checks.")
   ```
2. **Resolve Upstream Stale Bay**: Fixing Issue C eliminates the false `Component clash` on Agriculture, allowing `fw_res` to genuinely pass.
3. **Final Verdict Consistency**: In `save_markdown_report`, ensure the verdict checks `res.verification_result.verification_status != "FAILED"`.

#### 7. Invariants to Preserve
- The Agriculture run's successful physical convergence (MTOW $= 6.136\text{ kg}$, wingspan $= 1.833\text{ m}$, endurance $> 45\text{ min}$) must remain unchanged.

---

### Issue E: Maximum Takeoff Weight (MTOW) Accounting & Propagation

#### 1. Pipeline Stages Responsible
- `MissionTranslationStage` (Stage 1)
- `WingPlanformOptimizationStage` (Stage 4)
- `AircraftConvergenceStage` (Stage 13)
- `ConvergenceManager` (Convergence Loop)
- `MassPropertiesRule` (Common Verification)

#### 2. Exact Files and Functions Responsible
- `backend/design/fixed_wing/pipeline/pipeline_stage.py`: [MissionTranslationStage.execute](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/pipeline/pipeline_stage.py#L114-L117, L144-L152)
- `backend/design/fixed_wing/wing/wing_sizer.py`: [WingSizer.size_wing](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/wing/wing_sizer.py#L80-L91)
- `backend/design/fixed_wing/convergence/convergence_manager.py`: [ConvergenceManager.run_convergence](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/convergence/convergence_manager.py#L58-L75)
- `backend/design/common/verification/rules/mass_properties_rule.py`: [MassPropertiesRule.evaluate](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/common/verification/rules/mass_properties_rule.py#L58-L78)

#### 3. Complete Trace
1. **User Requirement**: `RequirementModel.maximum_takeoff_weight_kg`. (Typically `None` unless a regulatory ceiling like 25.0 kg is specified).
2. **Mission Translation Mutation**:
   - Lines 114–117: If None, creates synthetic limit $m_{\text{limit}} = \max(2.0, \text{payload} \times 3.0)$.
   - Passed to `MissionRequirements(maximum_takeoff_weight_limit_kg=m_limit)`.
   - `MissionEngine` sets `constraints.maximum_takeoff_weight_kg = m_limit`.
   - Lines 144–152 immediately override:
     - `context.execution_metadata["orig_max_mtow"] = constraints.maximum_takeoff_weight_kg`
     - `mission_result.constraints.maximum_takeoff_weight_kg = req.maximum_takeoff_weight_kg or 25.0` (loosened to 25 kg).
     - `mission_result.mission_profile.maximum_takeoff_weight_limit_kg = max(1.5, payload * 2.5)` (initial seed).
   - *State at this point*: Constraints says $25.0\text{ kg}$, profile says $1.5\text{ kg}$ (for 0.5 kg payload) or $5.0\text{ kg}$ (for 2.0 kg payload).
3. **Wing Planform Sizing**:
   `WingSizer.size_wing` reads `mission_profile.maximum_takeoff_weight_limit_kg` ($2.5 \times \text{payload}$) to calculate initial wing area $S$.
4. **Convergence Manager**:
   In each iteration $i$, `mission_profile.maximum_takeoff_weight_limit_kg` is updated to the physical mass computed at iteration $i-1$.
5. **Restoration**:
   In `AircraftConvergenceStage`'s `finally` block (lines 719–721):
   `mission_result.constraints.maximum_takeoff_weight_kg = orig_max_mtow`.
   Restores the synthetic $3.0 \times \text{payload}$ limit ($2.0\text{ kg}$ for 0.5 kg payload; $6.0\text{ kg}$ for 2.0 kg payload).
6. **Verification Rule**:
   `MassPropertiesRule.evaluate` inspects:
   If `req.maximum_takeoff_weight_kg` is `None`, it falls back to `mr.constraints.maximum_takeoff_weight_kg` (`orig_max_mtow`).
   If the converged aircraft physically sized to $6.136\text{ kg}$ (as in Agriculture), it exceeds the synthetic $6.0\text{ kg}$ limit, triggering a false failure!

#### 4. Problem Classification
- **Conflation of Distinct Engineering Quantities**: The codebase uses the single attribute `maximum_takeoff_weight_limit_kg` / `maximum_takeoff_weight_kg` to represent four contradictory concepts:
  1. A hard customer constraint.
  2. An initial sizing seed estimate.
  3. The current iteration state in the convergence loop.
  4. A regulatory certification ceiling.

#### 5. Relevant Code Snippets
```python
# backend/design/fixed_wing/pipeline/pipeline_stage.py:145-151
context.execution_metadata["orig_max_mtow"] = mission_result.constraints.maximum_takeoff_weight_kg
mission_result.constraints.maximum_takeoff_weight_kg = req.maximum_takeoff_weight_kg or 25.0
mission_result.mission_profile.maximum_takeoff_weight_limit_kg = initial_estimate

# backend/design/common/verification/rules/mass_properties_rule.py:68-71
if mtow_limit >= 999.0:
    mtow_limit = getattr(constraints, "maximum_takeoff_weight_kg", None) or 999.0
```

#### 6. Proposed Safe Correction
1. Preserve `RequirementModel.maximum_takeoff_weight_kg` strictly as the user's hard upper bound (or `None` if unconstrained).
2. Create dedicated attributes on `MissionProfile`:
   - `initial_mtow_seed_kg`: for pre-loop wing sizing.
   - `current_iteration_mtow_kg`: for loop feedback.
3. In `MassPropertiesRule`, only enforce MTOW constraint if `mission_requirements.maximum_takeoff_weight_kg` was explicitly provided by the user.

#### 7. Invariants to Preserve
- When a user explicitly enters an MTOW limit (e.g. 5.0 kg), the pipeline must strictly abort or fail verification if MTOW exceeds 5.0 kg.

---

### Issue F: Payload Mass Accounting (Requested 1 kg $\to$ 1.5 kg)

#### 1. Pipeline Stages Responsible
- `MassPropertiesStage` / `MassPropertiesOptimizer` (Stage 10 / In-Loop Subsystem 7)

#### 2. Exact Files and Functions Responsible
- `backend/design/fixed_wing/mass_properties/optimization/candidate_evaluator.py`: [MassCandidateEvaluator.evaluate](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/mass_properties/optimization/candidate_evaluator.py#L143-L150, L204-L206, L326, L332)
- `backend/design/fixed_wing/mass_properties/mass_properties_engine.py`: [MassPropertiesEngine.process_mass_design](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/mass_properties/mass_properties_engine.py#L170, L233)
- `backend/design/fixed_wing/payload/payload_engine.py`: [PayloadEngine.process_payload_design](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/payload/payload_engine.py#L210-L215)

#### 3. Complete Trace
1. **User Requirement**: `payload_weight_kg = 1.0 kg`.
2. **Payload Engine Accounting**:
   - `PayloadEngine` selects camera Sony RX1R II ($0.51\text{ kg}$).
   - `installed_mass = max(requested_mass, total_weight) = max(1.0, 0.51) = 1.0 kg`.
   - `installed_payload_mass_kg` is set to $1.0\text{ kg}$ (allocating $0.51\text{ kg}$ to camera and $0.49\text{ kg}$ to ballast/mount margin).
3. **Pre-Loop Engine Accounting (`MassPropertiesEngine`)**:
   - `pay_mass = requirements.payload_result.installed_payload_mass_kg` ($1.0\text{ kg}$).
   - Adds one component: `ComponentMass("Mission Payload", 1.0 kg)`. Total payload $= 1.0\text{ kg}$.
4. **In-Loop Optimizer Accounting (`MassCandidateEvaluator`)**:
   - Line 146: `pay_mass = getattr(pay_result, "installed_payload_mass_kg", 1.5)` ($1.0\text{ kg}$).
   - Line 149: `mission_equip_mass = 0.500  # Camera / sensors packaging default`.
   - Lines 205–206:
     ```python
     components_ex_batt.append(ComponentMass("Payload", round(pay_mass, 3), ...))            # 1.0 kg
     components_ex_batt.append(ComponentMass("Mission Equipment", round(mission_equip_mass, 3), ...)) # 0.5 kg
     ```
   - Lines 326–332:
     ```python
     payload_components = ["Payload", "Mission Equipment"]
     payload_weight_kg = sum(c.mass_kg for c in components if c.name in payload_components)  # 1.0 + 0.5 = 1.5 kg!
     ```
5. **Terminal / Report Output**:
   Displays `Payload Mass: 1.500 kg` for a 1.000 kg mission input.

#### 4. Problem Classification
- **Double Counting / Disjointed Subsystem Accounting**: `installed_payload_mass_kg` already encapsulates the entire user-requested payload capacity. Adding an arbitrary, hardcoded 0.500 kg "Mission Equipment" component on top duplicates packaging allowance.

#### 5. Relevant Code Snippets
```python
# backend/design/fixed_wing/mass_properties/optimization/candidate_evaluator.py:146, 149, 205-206, 326
pay_mass = getattr(pay_result, "installed_payload_mass_kg", 1.5)
mission_equip_mass = 0.500  # Camera / sensors packaging default
...
components_ex_batt.append(ComponentMass("Payload", round(pay_mass, 3), ...))
components_ex_batt.append(ComponentMass("Mission Equipment", round(mission_equip_mass, 3), ...))
...
payload_components = ["Payload", "Mission Equipment"]
```

#### 6. Proposed Safe Correction
- Allocate `mission_equip_mass` from within `installed_payload_mass_kg` rather than adding it on top:
  If `pay_mass > mission_equip_mass`:
  `payload_mass = pay_mass - mission_equip_mass`
  `equipment_mass = mission_equip_mass`
  Total payload mass remains strictly $1.000\text{ kg}$.
- If payload is generic cargo, set `mission_equip_mass = 0.0`.

#### 7. Invariants to Preserve
- Subsystem mass conservation (`structural + propulsion + avionics + battery + payload == MTOW`) must remain exact.

---

### Issue G: Propulsion Result Propagation (Lost Outputs)

#### 1. Pipeline Stages Responsible
- `PropulsionOptimizationStage` (Stage 8)
- Pipeline Runner / Report Serializer (`scripts/run_fixed_wing_pipeline.py`)

#### 2. Exact Files and Functions Responsible
- `scripts/run_fixed_wing_pipeline.py`: [print_terminal_summary](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/scripts/run_fixed_wing_pipeline.py#L446-L447)
- `scripts/run_fixed_wing_pipeline.py`: [save_markdown_report](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/scripts/run_fixed_wing_pipeline.py#L668-L669)
- `backend/design/fixed_wing/propulsion/propulsion_result.py`: `PropulsionResult`
- `backend/design/fixed_wing/propulsion/optimization/models.py`: `PropulsionSpecification`

#### 3. Complete Trace
1. **Calculation**: `PropulsionEngine.process_propulsion_design` calculates static thrust ($28.4\text{ N}$) and thrust-to-weight ratio ($0.50$).
2. **Result Packaging**: These metrics are packaged into `ThrustAnalysis`:
   ```python
   thrust_analysis = ThrustAnalysis(
       estimated_static_thrust_n=28.4,
       thrust_to_weight_ratio=0.50,
       ...
   )
   ```
   Attached to `PropulsionResult(thrust_analysis=thrust_analysis, ...)`.
3. **Pipeline Storage**: `context.propulsion_result` carries `PropulsionResult`.
4. **Runner Lookup**:
   In `run_fixed_wing_pipeline.py:446-447` and `668-669`:
   ```python
   thrust = getattr(pr, "max_thrust_n", getattr(pr, "static_thrust_n", 0.0))
   tw = getattr(pr, "thrust_to_weight_ratio", 0.0)
   ```
   `PropulsionResult` has no `max_thrust_n`, `static_thrust_n`, or `thrust_to_weight_ratio` attributes at the root level.
5. **Output**: `getattr` defaults to `'N/A'` or `0.0`. The terminal and Markdown display:
   `- **Static Thrust Available**: N/A N`
   `- **Thrust-to-Weight Ratio (T/W)**: N/A`

#### 4. Problem Classification
- **Incorrect Serialization / Attribute Access Mapping**: Root-level attribute lookup performed on a nested container model.

#### 5. Proposed Safe Correction
Update `run_fixed_wing_pipeline.py` to check both nested `pr.thrust_analysis` and root `pr`:
```python
thrust = 0.0
tw = 0.0
if hasattr(pr, "thrust_analysis") and pr.thrust_analysis:
    thrust = getattr(pr.thrust_analysis, "estimated_static_thrust_n", 0.0)
    tw = getattr(pr.thrust_analysis, "thrust_to_weight_ratio", 0.0)
elif hasattr(pr, "static_thrust_n"):
    thrust = getattr(pr, "static_thrust_n", 0.0)
    if hasattr(pr, "thrust_to_weight_ratio"):
        tw = getattr(pr, "thrust_to_weight_ratio", 0.0)
```

#### 6. Invariants to Preserve
- Underlying calculations in `PropulsionEngine` and `PropulsionOptimizer` must not be altered.

---

### Issue H: Configuration Rationale Mismatch

#### 1. Pipeline Stages Responsible
- `ConfigurationSelectionStage` (Stage 2)

#### 2. Exact Files and Functions Responsible
- `backend/design/fixed_wing/configuration/configuration_engine.py`: [ConfigurationEngine.process_configuration](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/configuration/configuration_engine.py#L123-L125)
- `backend/design/fixed_wing/configuration/configuration_strategy.py`: [LongEnduranceConfigurationStrategy.get_engineering_rationale](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/configuration/configuration_strategy.py#L153-L159)

#### 3. Complete Trace
1. In `ConfigurationEngine.process_configuration`:
   - Primary candidate layout is evaluated against constraints (e.g. Twin-Boom Pusher).
   - If the primary candidate triggers a validation warning or error, `chosen_candidate` falls back to an alternative layout (e.g. Single Tractor, Conventional Monoplane).
   - `best_layout` is updated to the chosen layout (`propulsion_layout: Tractor`, `tail_configuration: Conventional`).
2. In line 124:
   `rationale = strategy.get_engineering_rationale(requirements, best_layout)`
3. In `LongEnduranceConfigurationStrategy.get_engineering_rationale`:
   Returns a static string:
   `"The combination of a High Wing and Twin-Boom Pusher layout was chosen to optimize cruise aerodynamic efficiency..."`
   The method never reads `layout["propulsion_layout"]` or `layout["tail_configuration"]`.
4. Output Markdown reports:
   - Propulsion Layout: `Single Tractor`
   - Tail Configuration: `Conventional`
   - Engineering Rationale: *"The combination of a High Wing and Twin-Boom Pusher layout was chosen..."*

#### 4. Problem Classification
- **Hardcoded Boilerplate Rationale**: Rationale is statically defined for the strategy's archetype rather than synthesized from the selected layout variables.

#### 5. Proposed Safe Correction
In `ConfigurationStrategy.get_engineering_rationale`, dynamically compose rationale from the actual keys of `layout`:
```python
wing_pos = layout.get("wing_position", "High Wing")
prop_layout = layout.get("propulsion_layout", "Tractor")
tail_cfg = layout.get("tail_configuration", "Conventional")
return f"A {wing_pos} and {prop_layout} layout with a {tail_cfg} tail was chosen to balance..."
```

#### 6. Invariants to Preserve
- Trade study scoring matrices and configuration ranking must remain unchanged.

---

### Issue I: Multi-Variable Convergence Lag

#### 1. Pipeline Stages Responsible
- `AircraftConvergenceStage` (Stage 13)
- Subsystem: `ConvergenceManager` (`ConvergenceChecker`)

#### 2. Exact Files and Functions Responsible
- `backend/design/fixed_wing/convergence/convergence_checker.py`: [ConvergenceChecker.check_convergence](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/convergence/convergence_checker.py#L17-L30)
- `backend/design/fixed_wing/convergence/convergence_manager.py`: [ConvergenceManager.run_convergence](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/convergence/convergence_manager.py#L93-L98)
- `backend/design/fixed_wing/pipeline/pipeline_stage.py`: [AircraftConvergenceStage.execute](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/pipeline/pipeline_stage.py#L658-L675)

#### 3. Complete Trace
1. In `ConvergenceManager.run_convergence`, convergence is evaluated after each iteration using `ConvergenceChecker.check_convergence(history[-2], history[-1])`.
2. `check_convergence` checks 10 variables simultaneously:
   - `mtow` ($\le 0.05\text{ kg}$)
   - `wing_area` ($\le 0.005\text{ m}^2$)
   - `wing_loading` ($\le 0.2\text{ kg/m}^2$)
   - `battery_mass` ($\le 0.02\text{ kg}$)
   - `empty_weight` ($\le 0.05\text{ kg}$)
   - `cg_x` ($\le 0.005\text{ m}$)
   - `static_margin` ($\le 0.005$)
   - `cruise_power` ($\le 2.0\text{ W}$)
   - `endurance` ($\le 0.5\text{ min}$)
   - `range` ($\le 0.2\text{ km}$)
3. In our forensic runtime trace of SURVEY 1.0 kg:
   - **Iteration 4 $\to$ 5**: MTOW delta $= 0.020\text{ kg}$ (PASSED $\le 0.05$). But `cruise_power` delta $= 2.30\text{ W} > 2.0\text{ W}$, `endurance` delta $= 0.66\text{ min} > 0.5\text{ min}$, and `range` delta $= 0.93\text{ km} > 0.2\text{ km}$. $\implies$ **NOT CONVERGED**.
   - **Iteration 5 $\to$ 6**: MTOW delta $= 0.002\text{ kg}$ (PASSED). All structural and power variables passed, but `range` delta $= 0.57\text{ km} > 0.2\text{ km}$. $\implies$ **NOT CONVERGED**.
   - **Iteration 6 $\to$ 7**: MTOW delta $= 0.000\text{ kg}$. `range` delta fell to $0.08\text{ km} \le 0.2\text{ km}$. All 10 variables satisfied. $\implies$ **CONVERGED**.
4. Discrepancy in Presentation:
   - In `AircraftConvergenceStage:658-675`, history is reconstructed using `ConvergenceEvaluator(tolerance=0.01)` which only inspects MTOW relative delta $\le 1\%$.
   - Consequently, the output table marks `converged: True` starting from iteration 4, and shows $\Delta = 0.000\text{ kg}$ for iterations 6 and 7, making it look like a broken loop.

#### 4. Problem Classification
- **Intentional Engine Design vs. Truncated Reporting**: The convergence loop is functioning correctly as a 10-variable multidisciplinary optimizer. The apparent issue is entirely a presentation mismatch where only the mass variable is shown, omitting the aerodynamic/performance settling deltas.

#### 5. Proposed Safe Correction
- Keep the 10-variable physical convergence criteria intact.
- Update `save_markdown_report` (and `AircraftConvergenceStage` history reconstruction) to either:
  (a) Mark `converged: True` only on the final step where all 10 variables pass, or
  (b) Display the governing non-converged variable delta (e.g. `Range Delta: 0.57 km`) alongside MTOW delta.

#### 6. Invariants to Preserve
- The multi-disciplinary convergence check ensuring aerodynamic, stability, and range variables have physically settled must remain strictly active.

---

## 4. Dependency and Impact Analysis

```
                                  [RequirementModel]
                                          |
                      +-------------------+-------------------+
                      |                                       |
           [MissionTranslationStage]                 [PayloadPackagingStage]
             - env_map (Issue C2)                       - catalog missing (Issue B)
             - MTOW loosen (Issue E)                    - generic cargo (Issue B)
             - Surveillance strategy (Issue A)                |
                      |                                       v
           [WingPlanformOptimization]                [AircraftConvergenceStage]
             - AR=16 & Elliptical (Issue A)             - loop MTOW mutation (Issue E)
             - Root chord floor (Issue A)               - STALE payload_result (Issue C1, D)
                      |                                 - +0.5kg Mission Equip (Issue F)
                      v                                 - 10-variable settling (Issue I)
           [FuselageOptimizationStage]                        |
             - width_m > root_chord (Issue A)                 v
                      |                              [VerificationCertificationStage]
                      +--------------------------------> - Component clash (Issue C1, D)
                                                         - Dual-verifier gate (Issue D)
                                                         - VerificationValidationError (Issue C1)
                                                         - Synthetic MTOW limit (Issue E)
                                                              |
                                                              v
                                                   [Report & Terminal Runner]
                                                         - Lost propulsion (Issue G)
                                                         - Static rationale (Issue H)
                                                         - Contradictory PASS (Issue D)
```

### Ripple Effect Analysis:
1. **Fixing Issue C1 (Stale payload layout in convergence loop)**:
   - Resolves the false component clash ($0.28\text{ m} > 0.15\text{ m}$) on DELIVERY.
   - Automatically resolves the false component clash on AGRICULTURE, allowing `fw_res.verification_status` to pass.
   - Restores DELIVERY compliance score from 88% to 100%, resolving the `INTERNAL_EXCEPTION`.
2. **Fixing Issue A (Surveillance Strategy & Root Chord Floor)**:
   - Immediately unblocks SECURITY, INSPECTION, and MILITARY runs, allowing them to enter and converge in the design loop.
   - Produces realistic tactical UAV wings ($AR \approx 8.5$, wingspan $\approx 0.97\text{ m}$).
3. **Fixing Issue B (Payload Catalog & Generic Cargo)**:
   - Immediately unblocks TRAINING, RESEARCH, and low-mass DELIVERY runs.
4. **Fixing Issue F (Payload Mass Accounting)**:
   - Eliminates 0.5 kg phantom mass, lowering MTOW by ~0.6–0.7 kg (accounting for structural snowball effects) and improving flight endurance/range estimates.

---

## 5. Recommended Correction Order

To avoid circular regressions and maintain system integrity, corrections should be executed in four strict phases:

```
Phase 1: Translation & Catalog Foundations (Issues C2, B)
  ├── 1.1 Add OperatingEnvironment.COASTAL mapping in MissionTranslationStage
  └── 1.2 Enrich PayloadSelector catalog & add generic cargo synthesis

Phase 2: Aerodynamic Sizing & Strategy Registration (Issue A)
  ├── 2.1 Register SurveillanceMissionStrategy and SurveillanceWingStrategy (AR ~ 8.5)
  └── 2.2 Enforce root chord clearance floor in WingSizer

Phase 3: State Propagation, Exception Handling & Mass Accounting (Issues C1, D, E, F)
  ├── 3.1 Propagate updated payload_result in IterationController during convergence
  ├── 3.2 Correct in-loop payload mass accounting (eliminate +0.5kg phantom equipment)
  ├── 3.3 Synchronize dual-verifier gate in VerificationCertificationStage
  ├── 3.4 Explicitly catch VerificationValidationError in FixedWingDesignPipeline
  └── 3.5 Prevent synthetic MTOW limit from overriding unconstrained user missions

Phase 4: Reporting, Serialization & Presentation (Issues G, H, I)
  ├── 4.1 Update runner to read nested pr.thrust_analysis attributes
  ├── 4.2 Parameterize configuration rationale dynamically
  └── 4.3 Synchronize iteration history table convergence status with ConvergenceChecker
```

---

## 6. Required Regression Test Plan

Following implementation of the proposed corrections, the following regression test campaign must be executed:

### 1. Regression Baselines (Must Maintain Zero Regression)
- **SURVEY (0.5 kg)**: Must converge in $\le 7$ iterations; reported MTOW $\approx 3.10\text{ kg}$; verified status `VERIFIED`; overall verdict `PASS`.
- **SURVEY (1.0 kg)**: Must converge in $\le 7$ iterations; reported MTOW $\approx 5.1\text{--}5.8\text{ kg}$; verified status `VERIFIED`; overall verdict `PASS`.
- **AGRICULTURE (2.0 kg)**: Must converge in $\le 6$ iterations; reported MTOW $\approx 6.1\text{ kg}$; verification status must cleanly report `VERIFIED` (resolving the contradiction); overall verdict `PASS`.

### 2. Previously Failing Test Cases (Must Now Pass)
- **SECURITY (0.5 kg, 30 min, 30 km, 80 km/h)**: Must size wing with $AR \approx 8.5$, root chord $> 0.13\text{ m}$, clear fuselage width ($0.12\text{ m}$), and converge to `SUCCESS`.
- **INSPECTION (0.5 kg, 20 min, 20 km, 60 km/h)**: Must clear root chord check and converge to `SUCCESS`.
- **MILITARY (2.0 kg, 45 min, 10 km, 80 km/h, COASTAL)**: Environment must preserve `MARINE`; wing must clear root chord check; converge to `SUCCESS`.
- **RESEARCH (0.8 kg, 40 min, 60 km, 90 km/h)**: Must match lightweight scientific probe and converge to `SUCCESS`.
- **TRAINING (0.2 kg, 15 min, 15 km, 60 km/h)**: Must match micro camera sensor and converge to `SUCCESS`.
- **DELIVERY (1.0 kg, 45 min, 80 km, 90 km/h, COASTAL)**: Must synthesize 1.0 kg cargo parcel and converge to `SUCCESS`.
- **DELIVERY (3.0 kg, 30 min, 30 km, 80 km/h)**: Must converge with updated payload bay dimensions; compliance score must reach $100\%$; status `SUCCESS`.

### 3. Automated Invariant & Audit Validations
- Execute `scripts/run_fixed_wing_smoke_tests.py`.
- Verify mass conservation equation:
  $$\text{structural\_mass} + \text{propulsion\_mass} + \text{avionics\_mass} + \text{battery\_mass} + \text{payload\_mass} \equiv \text{MTOW} \quad (\pm 0.001\text{ kg})$$
- Verify propulsion Markdown output displays numerical static thrust ($> 0\text{ N}$) and T/W ratio ($> 0$).
