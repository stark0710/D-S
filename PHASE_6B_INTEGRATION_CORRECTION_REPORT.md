# TORQ WINGS — FIXED-WING PIPELINE INTEGRATION CORRECTION REPORT
## Multi-Engine Propulsion + JSON Export + Manual Pareto Access

---

### 1. Executive Summary

During manual end-to-end execution of the Torq Wings production `FixedWingDesignPipeline`, a physical and architectural inconsistency was uncovered in multi-engine aircraft sizing:
- For multi-engine architectures—specifically cargo/delivery transport missions where `CargoConfigurationStrategy` defines `architecture = "Twin-Engine High-Wing Cargo Transport"`, `propulsion_layout = "Twin Tractor"`, and `engine_count = 2`—the downstream propulsion sizer, mass build-up, and electrical models sized only **1 motor, 1 propeller, 1 ESC, 35.55 N static thrust, and 0.455 kg propulsion mass**.
- In addition, the interactive manual runner (`scripts/run_fixed_wing_pipeline.py`) suffered from two deficiencies:
  1. The exported `final_specification` dictionary serialized as `{}` in `result.json` due to relying on `__dict__` against slotted classes inheriting from `FinalAircraftSpecification`.
  2. The production Phase 6B-6 Pareto frontier extraction engine (`pareto=True`) was locked inside `FixedWingDesignPipeline.execute()`, with no user prompt or output display in the interactive runner.

This integration correction successfully resolved all issues without modifying the locked optimization algorithms (Phases 6B-1 through 6B-6), without introducing new global optimizers, without weakening any validation constraint, and with **zero regression** on the single-engine baseline ($N=1$).

---

### 2. Forensic Audit & Root Cause Analysis

A systematic trace from configuration selection down through convergence revealed where `engine_count` was lost:

1. **Configuration Selection**:
   `CargoConfigurationStrategy.select_best_layout()` correctly set `"engine_count": "2"`, `"propulsion_layout": "Twin Tractor"`, and `"architecture": "Twin-Engine High-Wing Cargo Transport"`.
2. **Propulsion Sizing Disconnection**:
   In `PropulsionEngine.process_propulsion_design()`, `engine_count` was completely ignored. Drag forces and thrust requirements were calculated for the total aircraft weight, but the engine selected a single motor and single propeller to satisfy total thrust, outputting `estimated_static_thrust_n = 35.55 N` (1 unit).
3. **Propulsion Optimizer Disconnection**:
   In `PropulsionCandidateEvaluator`, motor power and mass assumed 1 motor (`m_motor = motor["weight_g"] / 1000.0`, `m_esc = esc["weight_g"] / 1000.0`). `engine_count` was never extracted from the configuration context.
4. **Mass Properties Engine Disconnection**:
   In `MassPropertiesEngine` and `mass_properties/optimization/candidate_evaluator.py`, propulsion mass was hardcoded as `motor_mass = (motor_g / 1000.0)` and `prop_mass = 0.065`, completely ignoring `engine_count = 2`.
5. **Nacelle Longitudinal Coordinate Disconnection**:
   Single-engine tractor aircraft mount the engine in the fuselage nose cone ($x = 0.06\text{ m}$). When twin-engine mass was scaled to 2 units ($0.910\text{ kg}$), placing two engines at the fuselage nose cone created an artificial forward CG imbalance. Twin tractor engines are physically mounted on wing nacelles ($x_{\text{nacelle}} \approx x_{\text{wing\_attach}} - 0.05\text{ m}$), which properly balances the airframe longitudinally.
6. **JSON Serialization Bug**:
   `PipelineFinalAircraftSpecification` uses `__slots__` and property delegation. Standard `__dict__` reflection yielded `{}`.

---

### 3. Multi-Engine Integration Changes

The configuration's authoritative `engine_count` is now extracted from `ConfigurationResult` (or `selected_configuration["engine_count"]`) and propagated through:
1. `backend/design/fixed_wing/propulsion/optimization/models.py`:
   - Added typed fields: `engine_count: int`, `per_motor_static_thrust_n: float`, `per_motor_max_power_w: float`, `per_motor_cruise_power_w: float`, `propulsion_layout: str`, `motor_weight_g: float`, `esc_weight_g: float`.
2. `backend/design/fixed_wing/propulsion/propulsion_engine.py`:
   - Authoritative extraction of `engine_count = int(config_res.selected_configuration.get("engine_count", 1))`.
   - Propagated to `PowerAnalysis.metadata`, `ThrustAnalysis`, and engineering notes.
3. `backend/design/fixed_wing/propulsion/optimization/propulsion_optimizer.py`:
   - Canonical AT3520 baseline parameters: `motor_weight_g = 310.0`, `esc_weight_g = 80.0`.
   - Extracted `engine_count` and populated `PropulsionSpecification`.

---

### 4. Propulsion Calculation Changes

For an aircraft with $N$ identical propulsion units:
- **Per-unit cruise drag / thrust**:
  $$D_{\text{unit}} = \frac{D_{\text{total}}}{N}$$
- **Per-unit takeoff thrust**:
  $$T_{\text{to, unit}} = \frac{T_{\text{to, total}}}{N}$$
- **Per-unit static thrust**:
  $$T_{\text{unit}} = \left( \rho \cdot A_{\text{prop}} \cdot P_{\text{shaft, unit}}^2 \right)^{1/3}$$
- **Total aircraft static thrust**:
  $$T_{\text{static, total}} = N \cdot T_{\text{unit}}$$
- **Total maximum power**:
  $$P_{\text{max, total}} = N \cdot P_{\text{max, unit}}$$
- **Total cruise electrical power**:
  $$P_{\text{cruise, total}} = N \cdot P_{\text{cruise, unit}}$$

No new thrust equations were invented; existing validated momentum-disc and aerodynamic equations were preserved.

---

### 5. Mass Propagation

Propulsion hardware scales strictly by `engine_count`:
- $\text{Motor mass} = N \times m_{\text{motor}} = 2 \times 0.310 = 0.620\text{ kg}$
- $\text{Propeller mass} = N \times m_{\text{prop}} = 2 \times 0.065 = 0.130\text{ kg}$
- $\text{ESC mass} = N \times m_{\text{ESC}} = 2 \times 0.080 = 0.160\text{ kg}$
- $\text{Total propulsion hardware mass} = N \times 0.455\text{ kg} = 0.910\text{ kg}$

**Zero Phantom Mass**:
- Non-propulsion subsystems (avionics, payload, landing gear, fasteners, wiring, safety margin) are **not** multiplied by $N$.
- Zero phantom mission equipment is introduced (`mission_equipment = 0.0` unless explicitly specified in mission metadata).
- Longitudinal placement accounts for physical wing nacelles:
  $$x_{\text{motor}} = \max(0.06, x_{\text{wing\_attach}} - 0.05)$$

---

### 6. Power & Battery Propagation

The multi-engine configuration propagates downstream to the electrical and energy sizing systems:
- Continuous cruise electrical draw:
  $$P_{\text{continuous}} = P_{\text{cruise, total}} + P_{\text{avionics}} + P_{\text{payload}}$$
- Mission energy requirement (Phase 6B-3 target-aware):
  $$E_{\text{req}} = \frac{P_{\text{continuous}} \times \max(t_{\text{target}}, t_{\text{range}})}{0.85 \times 60.0}$$
- Battery mass:
  $$m_{\text{battery}} = \frac{E_{\text{req}}}{e_{\text{specific}}}$$
- For twin-engine Delivery ($1.0\text{ kg}$ payload, $45\text{ min}$, $40\text{ km}$, $80\text{ km/h}$):
  $$P_{\text{cruise}} = 149.8\text{ W} \implies m_{\text{battery}} = 0.837\text{ kg}$$

---

### 7. JSON Serialization Fix

In `scripts/run_fixed_wing_pipeline.py`, `to_dict` was completely overhauled to handle slotted and complex inherited structures:
1. Recognizes dataclasses with `__slots__` via `dataclasses.fields()`.
2. Inspects `__slots__` tuples across the class hierarchy.
3. Automatically serializes `@property` and dynamic getters (e.g. `mission`, `configuration`, `wing`, `fuselage`, `propulsion`, `electrical`, `mass_properties`, `cg`, `performance`, `convergence_report`, `certification_report`).
4. Result: `final_specification` in `result.json` is fully populated with all engineering subsystems and zero empty `{}` dictionaries.

---

### 8. Pareto Runner Integration

Phase 6B-6 Pareto front extraction is now seamlessly exposed in `scripts/run_fixed_wing_pipeline.py`:
1. **Interactive Prompt**:
   ```
   Generate Pareto alternatives? [Y/N, Default: N]:
   ```
2. **Default**: Disabled (`pareto=False`). Zero extra computation or candidate extraction when disabled.
3. **When Enabled (`pareto=True`)**:
   - Calls the existing `FixedWingDesignPipeline.execute(..., pareto=True)` using `ParetoFrontExtractor`.
   - Displays a clean terminal summary table:
     ```
     --------------------------------------------------------------------------------
     PARETO FRONTIER ANALYSIS (Phase 6B-6)
     --------------------------------------------------------------------------------
     Candidate Pool      : 24
     Feasible Candidates : 24
     Pareto Front Size   : 3

     Candidate ID           MTOW (kg)   Endurance (min) Range (km)  Payload (kg) L/D   Selected
     --------------------------------------------------------------------------------
     [W1_T1_P1]             3.655       45.0            30.0        0.500        13.5  * SELECTED
     ...
     ```
   - Exports the full typed `pareto_front` structure into the JSON artifact and Markdown report.

---

### 9. Delivery Case: Before vs. After

| Metric | Before (Inconsistent Single Unit) | After (Physically Consistent Twin) | Engineering Rationale |
| :--- | :---: | :---: | :--- |
| **Architecture** | Twin-Engine Cargo Transport | Twin-Engine Cargo Transport | Unchanged |
| **Propulsion Layout** | Twin Tractor | Twin Tractor | Unchanged |
| **Engine Count** | 1 (displayed "Twin") | **2** | Physically sized 2 units |
| **Motor Count** | 1 | **2** | 2 × AT3520 units |
| **Propeller Count** | 1 | **2** | 2 × 12x6 APC units |
| **ESC Count** | 1 | **2** | 2 × 60A ESC units |
| **Per-Motor Thrust** | 35.55 N | 35.55 N | Validated momentum disc |
| **Total Static Thrust**| 35.55 N | **71.10 N** | $2 \times 35.55\text{ N}$ |
| **Propulsion Mass** | 0.455 kg | **0.910 kg** | $2 \times (0.310 + 0.065 + 0.080)\text{ kg}$ |
| **Cruise Power** | ~80 W | **149.8 W** | Physics-based drag & 2-motor flight |
| **Battery Mass** | 0.540 kg | **0.837 kg** | Target-aware energy sizing for twin power |
| **MTOW** | 4.207 kg (erroneous) | **4.876 kg** | Re-converged multidisciplinary MTOW |
| **Thrust-to-Weight (T/W)** | 0.86 | **1.49** | $71.10\text{ N} / (4.876\text{ kg} \times 9.81) = 1.486$ |
| **Static Margin** | 12.0% | **13.9%** | Stable longitudinal margin [10%, 20%] |
| **Mass Conservation** | diff = 0.0000 kg | **diff = 0.0000 kg** | Exact sum of all components == MTOW |
| **Pipeline Status** | Inconsistent | **SUCCESS (Converged & Certified)** | Fully certified airframe |

---

### 10. Single-Engine Baseline Regression Results

To verify that single-engine configurations remain **100% numerically identical** to the locked Phase 6B-4 baseline, 5 representative single-engine missions were executed through the full convergence pipeline:

| Representative Case | Payload | Flight Time | Range | Engine Count | Static Thrust | MTOW | Battery Mass | Propulsion Mass | Status | Regression? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Survey 0.5kg** | 0.5 kg | 45 min | 30 km | 1 | 35.55 N | **3.655 kg** | 0.616 kg | 0.455 kg | SUCCESS | **ZERO** (Exact match) |
| **Survey 1.0kg** | 1.0 kg | 45 min | 30 km | 1 | 35.55 N | **4.375 kg** | 0.720 kg | 0.455 kg | SUCCESS | **ZERO** (Exact match) |
| **Agriculture 2.0kg**| 2.0 kg | 35 min | 25 km | 1 | 35.55 N | **5.071 kg** | 0.616 kg | 0.455 kg | SUCCESS | **ZERO** (Exact match) |
| **Security 0.5kg** | 0.5 kg | 60 min | 40 km | 1 | 35.55 N | **3.607 kg** | 0.795 kg | 0.455 kg | SUCCESS | **ZERO** (Exact match) |
| **Inspection 0.5kg**| 0.5 kg | 40 min | 25 km | 1 | 35.55 N | **3.159 kg** | 0.407 kg | 0.455 kg | SUCCESS | **ZERO** (Exact match) |

*Conclusion*: Zero numerical drift across all single-engine platforms.

---

### 11. Mass Conservation Verification

Across all single-engine and twin-engine aircraft, exact component mass conservation was validated:
$$\sum_{i=1}^{M} m_i = \text{MTOW}$$

| Aircraft Configuration | Sum of Components ($\sum m_i$) | Reported MTOW | Absolute Delta | Conservation Status |
| :--- | :---: | :---: | :---: | :---: |
| Survey 0.5kg ($N=1$) | 3.655 kg | 3.655 kg | 0.0000 kg | **EXACT MATCH** |
| Survey 1.0kg ($N=1$) | 4.375 kg | 4.375 kg | 0.0000 kg | **EXACT MATCH** |
| Agriculture 2.0kg ($N=1$) | 5.071 kg | 5.071 kg | 0.0000 kg | **EXACT MATCH** |
| Security 0.5kg ($N=1$) | 3.607 kg | 3.607 kg | 0.0000 kg | **EXACT MATCH** |
| Inspection 0.5kg ($N=1$) | 3.159 kg | 3.159 kg | 0.0000 kg | **EXACT MATCH** |
| Delivery 1.0kg ($N=2$) | 4.876 kg | 4.876 kg | 0.0000 kg | **EXACT MATCH** |

---

### 12. Thrust-to-Weight (T/W) Validation

Aircraft-level static thrust-to-weight ratio strictly evaluates:
$$(T/W)_{\text{aircraft}} = \frac{\sum_{j=1}^N T_{\text{static}, j}}{\text{MTOW} \times g}$$
- For Survey 0.5kg ($N=1$):
  $$T/W = \frac{35.55\text{ N}}{3.655\text{ kg} \times 9.80665\text{ m/s}^2} = 0.99$$
- For Delivery 1.0kg ($N=2$):
  $$T/W = \frac{71.10\text{ N}}{4.876\text{ kg} \times 9.80665\text{ m/s}^2} = 1.49$$

The multi-engine calculation is physically consistent throughout.

---

### 13. Pareto Validation

Phase 6B-6 Pareto front extraction was verified both with Pareto disabled and enabled:
1. **Pareto Disabled (`pareto=False`)**:
   - `res.pareto_front` remains `None`. Pipeline executes at standard baseline speed.
2. **Pareto Enabled (`pareto=True`)**:
   - `ParetoFrontExtractor` successfully extracted non-dominated candidate architectures.
   - Mathematical self-check `self_check_pareto_front(front)` returned `True`.
   - Every candidate is feasible with zero constraint violations.
   - Candidates are mutually non-dominated across (MTOW min, Endurance max, Range max, Payload max, L/D max).

---

### 14. Dedicated Integration Test Suite Results

A dedicated 17-test suite (`tests/design/fixed_wing/pipeline/test_multi_engine_integration.py`) was implemented and executed:

| Test ID | Test Function | Description | Result |
| :--- | :--- | :--- | :---: |
| TEST 1 | `test_1_single_engine_architecture` | Verify 1 unit for engine_count = 1 | **PASSED** |
| TEST 2 | `test_2_twin_engine_architecture` | Verify 2 motors, 2 props, 2 ESCs for engine_count = 2 | **PASSED** |
| TEST 3 | `test_3_twin_thrust` | Verify total thrust = per_unit × 2 (71.10 N) | **PASSED** |
| TEST 4 | `test_4_twin_propulsion_mass` | Verify propulsion mass scales to 0.910 kg | **PASSED** |
| TEST 5 | `test_5_twin_power` | Verify total cruise power and current propagation | **PASSED** |
| TEST 6 | `test_6_twin_battery` | Verify Phase 6B-3 target-aware battery responds to twin power | **PASSED** |
| TEST 7 | `test_7_twin_mass_conservation` | Verify exact mass conservation ($\sum m_i == \text{MTOW}$) | **PASSED** |
| TEST 8 | `test_8_twin_tw` | Verify aircraft T/W uses total thrust (1.49) | **PASSED** |
| TEST 9 | `test_9_configuration_consistency` | Verify architecture, engine_count, and propulsion agree | **PASSED** |
| TEST 10 | `test_10_single_engine_regression` | Verify Survey baseline remains 3.655 kg | **PASSED** |
| TEST 11 | `test_11_delivery_real_case` | Run exact 1.0kg / 45min / 40km delivery case | **PASSED** |
| TEST 12 | `test_12_json_serialization` | Verify final_specification is NOT {} in JSON | **PASSED** |
| TEST 13 | `test_13_json_propulsion_details` | Verify JSON contains engine_count and multi-engine details | **PASSED** |
| TEST 14 | `test_14_json_mass_accounting` | Verify JSON contains 22-item mass breakdown | **PASSED** |
| TEST 15 | `test_15_pareto_disabled` | Verify pareto_front is None when pareto=False | **PASSED** |
| TEST 16 | `test_16_pareto_enabled` | Verify production Pareto extractor produces populated front | **PASSED** |
| TEST 17 | `test_17_pareto_mathematical_self_check` | Verify Pareto candidates are feasible and mutually non-dominated | **PASSED** |

**Summary: 17 passed in 346.00s.**

---

### 15. Full Fixed-Wing Test Suite Results

The entire fixed-wing test suite (`tests/design/fixed_wing/`) was executed:
- **Total Tests Collected**: 234
- **Passed**: 233
- **Failed**: 1 (Known pre-existing stale test: `test_sprint44B_corrections.py::test_performance_missed_results_in_verification_failure`)
- **New Failures**: 0
- **Regressions**: 0

The single pre-existing failure is documented in locked Phase 6B-4/6B-6 notes and per instructions was left unmodified.

---

### 16. Files Modified

| File Path | Description of Changes |
| :--- | :--- |
| `backend/design/fixed_wing/propulsion/optimization/models.py` | Added multi-engine fields (`engine_count`, `per_motor_*`, `propulsion_layout`, component weights). |
| `backend/design/fixed_wing/propulsion/propulsion_engine.py` | Extracted authoritative `engine_count`, scaled static thrust ($N \times T_{\text{unit}}$), power, and metadata. |
| `backend/design/fixed_wing/propulsion/optimization/candidate_evaluator.py` | Computed per-motor power and scaled propulsion hardware mass ($N \times (m_{\text{motor}} + m_{\text{ESC}}) + m_{\text{batt}}$). |
| `backend/design/fixed_wing/propulsion/optimization/constraints.py` | Evaluated per-motor current against ESC and motor thermal limits; total current against battery C-rating. |
| `backend/design/fixed_wing/propulsion/optimization/propulsion_optimizer.py` | Canonical AT3520 baseline parameters (`310.0g` motor, `80.0g` ESC); passed `engine_count`. |
| `backend/design/fixed_wing/mass_properties/mass_properties_engine.py` | Sized $N$ motors, $N$ props, $N$ ESCs; positioned twin tractor motors at wing nacelles ($x_{\text{wing}} - 0.05$). |
| `backend/design/fixed_wing/mass_properties/optimization/candidate_evaluator.py` | Standardized on `StructuralWeightEngine` build-up; scaled $N$ propulsion hardware; wing nacelle positioning. |
| `backend/design/fixed_wing/cg/optimization/candidate_evaluator.py` | Placed twin-engine tractor nacelles at wing leading edge station ($x_{\text{wing}} - 0.05$) to balance airframe. |
| `scripts/run_fixed_wing_pipeline.py` | Fixed `to_dict` serialization for slotted specifications; added interactive Pareto prompt & display. |
| `tests/design/fixed_wing/pipeline/test_multi_engine_integration.py` | Complete 17-test integration verification suite. |

---

### 17. Forensic Diff & Architectural Integrity Audit

1. **Phase 6B Optimization Algorithms Preserved**:
   - `OptimizationPriorityPolicy` (Phase 6B-1): Active and unchanged.
   - `TailObjectiveFunction` (Phase 6B-2): Active and unchanged.
   - Target-Aware Battery Sizing (Phase 6B-3): Active and unchanged.
   - Typed Wing Objective (Phase 6B-4): Active and unchanged.
   - Pareto Front Extraction (Phase 6B-6): Active and invoked directly via `pareto=True`.
2. **Validation Invariants**:
   - Zero validators weakened or removed.
   - All physical component mass constraints and electrical limits strictly enforced.
3. **Mass Conservation**:
   - $\sum m_i = \text{MTOW}$ exact to $0.0000\text{ kg}$.
   - Zero phantom equipment mass.
   - Zero double counting of motors or batteries.
4. **Propulsion Physics**:
   - Per-unit thrust derived from validated momentum-disc equation.
   - Total static thrust = $N \times \text{per-unit thrust}$.
   - $T/W = T_{\text{total}} / (\text{MTOW} \times g)$.

---

### 18. Known Limitations

1. **Pre-existing Stale Test**:
   `test_sprint44B_corrections.py::test_performance_missed_results_in_verification_failure` fails because the converged pipeline now finds a feasible solution for case 1708 instead of failing. Per the scope mandate, this test was not modified.
2. **Interactive Manual Runner Terminal**:
   The interactive runner requires interactive input unless piped with EOF. When running unattended scripts, pass inputs or call `FixedWingDesignPipeline` directly.

---

### 19. Final Engineering Verdict

### **VERDICT: PASS — MULTI-ENGINE PROPULSION, JSON SERIALIZATION & PARETO RUNNER FULLY INTEGRATED**

The Torq Wings Fixed-Wing design pipeline is now 100% physically, aerodynamically, and structurally consistent for multi-engine aircraft, maintains exact mass conservation, serializes complete technical specifications to JSON, exposes production Pareto optimization to interactive manual users, and preserves the single-engine numerical baseline with zero regressions.
