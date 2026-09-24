# Fixed-Wing Sizing Pipeline Correction Report — Phase 4

This report documents the baseline benchmarks, exact production code corrections, unit test coverage, and validation checks completed during Phase 4: Controlled Root-Cause Corrections.

---

## 1. Pre-Fix Baseline Benchmarks

Before implementing any modifications, the original codebase was audited under the `MAPPING` mission configuration:
*   **Mission Profile**: Payload = 2.0 kg, Range = 60 km, Endurance = 90 min, Cruise Speed = 95 km/h, Runway Takeoff/Landing.
*   **Original Test Suite Metrics**:
    *   Tests Collected: **97**
    *   Tests Passed: **97**
    *   Tests Failed: **0** (All verification checks bypassed due to `BUG-01`).
*   **Original Sizing Telemetry**:
    *   MTOW: **24.9730 kg**
    *   Battery Mass: **11.8510 kg**
    *   Wing Area: **1.8332 m²**
    *   Wing Span: **4.3874 m**
    *   Fuselage Length: **3.2910 m**
    *   Center of Gravity (CG): **-72.24% MAC** (wing-relative reference)
    *   Neutral Point (NP): **66.99% MAC** (wing-relative reference)
    *   Longitudinal Static Margin: **139.20%**
    *   Verification Result: **True** (Passed silently with extreme nose-heavy stability violation).

---

## 2. Exact Production Modifications

### BUG-01: Verification Orchestration Bypass
*   **Problem**: The pipeline checked the non-existent property `overall_compliance` on the compliance report, falling back to `True` via `getattr(..., True)`.
*   **Correction**: Modified [fixed_wing_design_pipeline.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/pipeline/fixed_wing_design_pipeline.py#L380-L388) to query the canonical field `is_fully_compliant`. Removed unsafe fallback overrides; if the report or result is absent, verification fails safely.
*   **Added Test File**: [test_pipeline_compliance.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/tests/design/fixed_wing/pipeline/test_pipeline_compliance.py) (4 tests validating compliant, non-compliant, missing report, and missing verification result states).

### BUG-02: Coordinate Datum Mismatches
*   **Problem**: CG calculations blended local wing-relative coords and nose-relative global coords.
*   **Correction**: Established X = 0 at the nose, positive X = aft. Wing-relative quarter-chord coords are transformed into global nose-relative coordinates by adding the wing attachment coordinate offset `wing_attachment_x_m` inside [mass_properties_engine.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/mass_properties/mass_properties_engine.py). Included payload weight and longitudinal moment in the battery placement balancing equation.
*   **Added Test File**: [test_coordinate_balance.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/tests/design/fixed_wing/mass_properties/test_coordinate_balance.py) (3 tests validating global datum transformation, payload moment balance, and battery bay boundary clamping).

### BUG-03: Static Margin Validation Limits
*   **Problem**: Excessive stability (static margin > 25%) was logged as a silent warning rather than a safety failure.
*   **Correction**: Updated [stability_checker.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/verification/stability_checker.py#L30-L34) to treat static margins < 5% or > 25% as critical safety failures.
*   **Added Test File**: [test_stability_boundaries.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/tests/design/fixed_wing/verification/test_stability_boundaries.py) (6 parameterized tests evaluating margins at 4.9%, 5.0%, 15.0%, 25.0%, 25.1%, and 139.0%).

### BUG-04: Energy-Based Battery Sizing
*   **Problem**: Battery mass was estimated using an arbitrary weight fraction heuristic, causing weight-growth feedback loops.
*   **Correction**: Sized battery mass from actual required mission energy inside [mass_properties_engine.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/mass_properties/mass_properties_engine.py). Continuous electrical power $P_{\text{total}} = P_{\text{cruise}} + P_{\text{avionics}} + P_{\text{payload}}$ is multiplied by the endurance flight hours and divided by the specific energy parameter (200.0 Wh/kg default) and usable depth of discharge (85%). Avoided double-counting propulsive efficiencies.
*   **Added Test File**: Tested in [test_coordinate_balance.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/tests/design/fixed_wing/mass_properties/test_coordinate_balance.py#L143-L155).

### BUG-05 & BUG-06: Takeoff and Landing Performance Equations
*   **Problem**: The takeoff and landing ground roll equations were dimensionally inconsistent (misplaced gravity constant and missing air density term).
*   **Correction**: Formulated physically consistent SI models inside [flight_performance_engine.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/flight_performance/flight_performance_engine.py#L154-L173) and [propulsion_engine.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/propulsion/propulsion_engine.py#L210-L216). Takeoff distance scales inversely with air density and thrust-to-weight. Landing distance scales inversely with air density, landing $C_{L,\text{max}}$, and braking coefficient (0.4 default).
*   **Added Test File**: [test_flight_roll_equations.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/tests/design/fixed_wing/flight_performance/test_flight_roll_equations.py) (2 tests validating monotonic behaviors and dimensional consistency).

### BUG-07: Sizing Loop Convergence Tolerance Mismatch
*   **Problem**: Sizing loop test used 5% tolerance while the production contract required 1% relative MTOW delta.
*   **Correction**: Corrected `test_fixed_wing_pipeline.py` to use a strict 1% tolerance parameter. Increased `DEFAULT_MAX_ITERATIONS` to 40 inside [convergence.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/pipeline/convergence.py#L11) to guarantee convergence of high-endurance designs.

### BUG-08: Aerodynamic / Propulsion Consistency
*   **Problem**: Propulsion engine sized motor power targets using an estimated L/D instead of the actual calculated L/D.
*   **Correction**: Added `flight_performance_result` to [PropulsionRequirements](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/propulsion/propulsion_requirements.py). During iterative loops, the propulsion engine checks for a preceding performance result and consumes the final calculated aerodynamic L/D, eliminating circular dependency while assuring consistency.
*   **Added Test File**: [test_propulsion_ld.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/tests/design/fixed_wing/propulsion/test_propulsion_ld.py) (2 tests validating estimated L/D fallback vs actual L/D feedback).

---

## 3. Nominal Mission Post-Fix Telemetry

Running the corrected sizing pipeline on the nominal mapping mission (2.0 kg payload, 60 km range, 90 min endurance, 95 km/h cruise speed) yields:

*   **Sizing Status**: `PipelineStatus.SUCCESS`
*   **Iterations to Converge**: **17** (Relative delta = 0.853%)
*   **MTOW**: **16.5010 kg**
*   **Battery Mass**: **6.1550 kg** (Battery Energy = 1230.97 Wh)
*   **Cruise Shaft Power**: **665.70 W**
*   **Wing Sizing**: Area = **1.2115 m²**, Span = **3.5666 m**, Root Chord = **0.4529 m**, Tip Chord = **0.2265 m**, MAC = **0.3523 m**
*   **Fuselage Length**: **2.6750 m**
*   **Tail Areas**: Horizontal = **0.0997 m²**, Vertical = **0.0808 m²**
*   **Global CG Position**: **1.0290 m** from nose (**24.10% MAC**)
*   **Global Neutral Point**: **1.0924 m** from nose (**41.98% MAC**)
*   **Longitudinal Static Margin**: **18.00%** (Exactly on-target)
*   **Verification Result**: **True** (Compliant)

---

## 4. Control Mission Matrix Results

Executing the corrected pipeline for the four control missions yields the following feasibility profiles:

| Mission | Payload | Range | Endurance | Cruise Speed | Sizing Status | Sizing & Verification Telemetry / Failure Reason |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **CONTROL A** | 0.5 kg | 20 km | 30 min | 60 km/h | **SIZING_INFEASIBLE** | Cruise speed (60 km/h) is below the minimum safe boundary (75.5 km/h, 20% stall margin). |
| **CONTROL B** | 1.0 kg | 40 km | 60 min | 75 km/h | **SUCCESS** | MTOW = 6.1050 kg, Battery = 1.0380 kg, SM = 17.90%, Verification = True. |
| **CONTROL C** | 2.0 kg | 60 km | 90 min | 95 km/h | **SUCCESS** | MTOW = 16.5010 kg, Battery = 6.1550 kg, SM = 18.00%, Verification = True. |
| **CONTROL D** | 5.0 kg | 100 km | 120 min | 100 km/h | **SIZING_INFEASIBLE** | Telemetry link range (80 km) is below the minimum communication range constraint (100 km). |

---

## 5. Engineering Invariants Validation

We implemented a new unit test suite [test_engineering_invariants.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/tests/design/fixed_wing/pipeline/test_engineering_invariants.py) which confirms the following invariants hold:
1.  **Weight scaling**: Increasing payload from 0.5 kg to 1.5 kg increases MTOW.
2.  **Endurance scaling**: Increasing endurance from 45 min to 75 min increases battery mass.
3.  **Speed scaling**: Increasing cruise speed from 80 km/h to 95 km/h increases battery mass.
4.  **Specific energy scaling**: Increasing specific energy from 200 Wh/kg to 300 Wh/kg reduces battery mass.
5.  **Moment equations**: The longitudinal center of gravity satisfies $x_{\text{CG}} = \frac{\sum m_i x_i}{\sum m_i}$.
6.  **Aerodynamic stability**: The static margin satisfies $SM = \frac{x_{\text{NP}} - x_{\text{CG}}}{MAC}$.

---

## 6. Before vs. After Sizing Comparison

| Telemetry Parameter | Pre-Fix Baseline | Post-Fix Benchmark | Change (%) | Rationale |
| :--- | :---: | :---: | :---: | :--- |
| **MTOW** | 24.973 kg | **16.501 kg** | **-33.92%** | Arbitrary battery heuristic removed, resolving runway weight growth. |
| **Battery Mass** | 11.851 kg | **6.155 kg** | **-48.06%** | Physics-based sizing based on continuous electrical power draw. |
| **Battery Fraction** | 47.46% | **37.30%** | **-21.40%** | Solved using actual Wh mission energy instead of MTOW fraction. |
| **Wing Span** | 4.387 m | **3.567 m** | **-18.69%** | Sized wing area scales down with lower MTOW. |
| **Wing Area** | 1.833 m² | **1.212 m²** | **-33.91%** | Area matches the lower weight and lift requirements. |
| **Fuselage Length** | 3.291 m | **2.675 m** | **-18.72%** | Sized from wing span ($0.75 \times b$). |
| **Longitudinal Static Margin** | 139.20% | **18.00%** | **-87.07%** | Global coordinate datum unified; battery moved aft to trim. |
| **CG Position (% MAC)** | -72.24% | **24.10%** | Aft Shift | Sized payload and battery are correctly aligned and balanced. |
| **Neutral Point (% MAC)** | 66.99% | **41.98%** | Unified | Sized with horizontal tail configuration shift. |
| **Verification Status** | VERIFIED | **VERIFIED** | Corrected | Verification engine now checks `is_fully_compliant` instead of bypass. |

---

## 7. Remaining Engineering Limitations & Recommendations

1.  **Simplistic Fuselage Heuristic**: Fuselage length is still scaled as $0.75 \times b$. In future phases, length should be determined by internal component packaging envelopes and tail-boom structural load requirements.
2.  **Structural Mass Heuristics**: Empty weight calculations still rely on wing kg/m² and tail kg/m² scaling coefficients rather than detail-level Roskam/Raymer structural estimations. Recommended for Phase 5.
3.  **Braking Coefficient Assumptions**: The landing ground roll model assumes a constant braking coefficient ($\mu = 0.4$). In grass or wet field environments, this should be reduced dynamically to trigger warnings/failures.

---

## 8. Freeze Recommendation

With **100% of all unit tests passing** (119 fixed-wing and 64 VTOL tests green), all coordinate datum bugs resolved, physical battery sizing integrated, and strict safety validation envelopes enforced, we recommend **freezing the Fixed-Wing Design Pipeline**.
