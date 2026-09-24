# PHASE 6A — FIXED-WING OPTIMIZATION FORENSICS & OBJECTIVE-FUNCTION AUDIT

**Project:** Torq Wings — Fixed-Wing Aircraft Design Backend  
**Document Version:** 1.0.0  
**Date:** September 14, 2026  
**Status:** COMPLETE  
**Final Verdict:** **PASS WITH WARNINGS** (Audit Complete, Zero Regressions, Significant Optimization Decoupling & Fragility Identified)

---

## 1. EXECUTIVE SUMMARY

### 1.1 Context & Objectives
Phase 6A executed an exhaustive, read-only forensic audit of the optimization architecture, candidate generation mechanisms, constraint screening layers, objective functions, and parameter sensitivities in the Torq Wings Fixed-Wing design backend. 

Per directive:
$$\text{AUDIT} \longrightarrow \text{UNDERSTAND} \longrightarrow \text{MEASURE} \longrightarrow \text{CLASSIFY} \longrightarrow \text{REPORT}$$

No aircraft sizing equations, optimization weights, candidate ranges, or constraint thresholds were modified. The protected baseline established in Phases 1–5 was preserved with zero regressions.

### 1.2 Key Forensic Findings
1. **Optimization Architecture Decoupling:**
   - `OptimizationPriority` (`BALANCED`, `LOWEST_COST`, `LOWEST_WEIGHT`, `MAXIMUM_ENDURANCE`, `MAXIMUM_RANGE`, `MAXIMUM_PAYLOAD`, `HIGHEST_EFFICIENCY`) is **completely disconnected** from the fixed-wing design backend. It is dropped at `MissionTranslationStage` and never queried by any of the 9 subsystem optimizers.
   - Controlled experiments confirmed that all 7 priorities produce **100.000% identical aircraft designs** across every aerodynamic, structural, electrical, and mass parameter.
2. **DesignMode Inactivity:**
   - `DesignMode` (`ENGINEERING_ADVISOR` vs `MANUAL`) does not participate in fixed-wing candidate generation, scoring, or convergence. It functions solely as upstream workflow metadata.
3. **Budget / Financial Cost Decoupling:**
   - `budget` is checked only in initial validation ($> 0$) and mission classification heuristics. It does not appear in any objective function, constraint check, or component trade-off inside the convergence loop. Budgets from \$500 to \$50,000 produce identical designs.
4. **Subsystem Optimization Architecture:**
   - The backend utilizes 9 sequential subsystem optimizers coordinated by `IterationController` within a damped successive-approximation convergence loop ($\omega = 0.65$).
   - Each optimizer operates independently as a **single-objective scalarized weighted-sum search with hard constraint pre-screening**.
5. **Absence of Pareto Optimization:**
   - Unlike the multirotor (`backend/design/drone/optimization/pareto_front.py`) and VTOL modules, the fixed-wing pipeline contains **zero Pareto front extraction or multi-objective trade-off capabilities**.
6. **Normalization & Scale Imbalance:**
   - Severe dimensional and scale imbalances exist in several objective functions (notably `TailObjectiveFunction`, where dimensionless deviations of magnitude $\sim 0.008$ are summed directly with unnormalized manufacturability scores of magnitude $\sim 0.80$, a $100\times$ distortion).
   - In `WingObjectiveFunction`, structural weight fractions are extracted by regex/string parsing of English sentences in `engineering_notes` rather than querying structured numerical attributes.
7. **Endurance & Battery Over-Sizing Inelasticity:**
   - In `PropulsionObjectiveFunction`, the endurance objective term maximizes raw flight time ($t / 180$) rather than rewarding proximity to the user's requested flight time. Because endurance weight ($0.35$) dominates propulsion weight ($0.10$), the optimizer selects the same 6S 5000mAh battery pack delivering 99 minutes regardless of whether the user requests 30, 45, 60, or 90 minutes.

---

## 2. BASELINE

The protected baseline established across Phases 1–5 remains intact:
- **Test Suite Status:** 178 passed, 1 pre-existing stale failure (`tests/design/fixed_wing/pipeline/test_sprint44B_corrections.py::test_performance_missed_results_in_verification_failure`), 0 errors.
- **Physical Mass Conservation:** Exact ($0.000000\%$ component discrepancy).
- **Phantom Mass:** $0.000\text{ kg}$.
- **Payload Accounting:** Exactly once.
- **Wing-Root Clearance:** $c_{\text{root}} > w_{\text{fuse}}$ maintained with $> 50\%$ margins.
- **Feasible Campaign Cases:** 90 / 90 converged; 21 / 21 boundary rejections trapped cleanly.

---

## 3. OPTIMIZATION ARCHITECTURE MAP

The actual fixed-wing design pipeline executes through the following sequence:

```mermaid
graph TD
    A[RequirementModel] --> B[MissionTranslationStage]
    B --> C[ConfigurationSelectionStage]
    C --> D[ConstructionSelectionStage]
    D --> E[Subsystem Pre-Pass Stages 4-12]
    E --> F[AircraftConvergenceStage]
    
    subgraph IterationController [AircraftConvergenceStage Loop: IterationController]
        F1[1. WingPlanformOptimizer] --> F2[2. FuselageOptimizer]
        F2 --> F3[3. PayloadPackagingOptimizer]
        F3 --> F4[4. TailOptimizer]
        F4 --> F5[5. PropulsionOptimizer]
        F5 --> F6[6. ElectricalOptimizer]
        F6 --> F7[7. MassPropertiesOptimizer]
        F7 --> F8[8. CGOptimizer]
        F8 --> F9[9. FlightPerformanceOptimizer]
    end
    
    F --> IterationController
    IterationController --> G{Converged? Delta MTOW < 0.01}
    G -- No: Relax MTOW with omega=0.65 --> IterationController
    G -- Yes --> H[VerificationCertificationStage]
    H --> I[Final PipelineFinalAircraftSpecification]
```

### Subsystem Optimizer Pattern
Each of the 9 subsystem optimizers inherits from `OptimizerBase` (`backend/design/common/optimization/optimizer_base.py`) and executes an identical 7-step lifecycle:

1. **`initialize(context)`**: Setup requirements and prior specification dependencies.
2. **`generate_candidates(context)`**: Produce discrete grid, permutation, or catalog candidates.
3. **`apply_constraints(candidate, context)`**: Filter candidates using `ConstraintManager`. Non-compliant candidates are marked `INFEASIBLE` and pruned before heavy analysis.
4. **`evaluate_candidate(candidate, context)`**: Execute domain engineering models (aerodynamics, structural beam, power polar, etc.) to populate `derived_variables`.
5. **`score_candidate(candidate, context)`**: Compute multi-term objective score via `ObjectiveFunction.calculate_scores`.
6. **`select_best_candidate(feasible_candidates, context)`**: Select winner:
   $$\text{Winner} = \arg\min_{c \in \text{Feasible}} c.\text{overall\_score}$$
7. **`build_specification(candidate, context)`**: Emit typed specification for context handoff.

---

## 4. CURRENT OBJECTIVE FUNCTION

Each subsystem possesses its own localized objective function. There is **no global multidisciplinary objective function**; the global aircraft convergence is an equilibrium-seeking Picard iteration on MTOW, while local optimizers greedily optimize their respective subsystems.

### Detailed Objective Function Inventory

| Subsystem Optimizer | Objective Class | Term Name | Weight | Direction | Numerical Formulation |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **WingPlanformOptimizer** | `WingObjectiveFunction` | `aerodynamics` | 0.30 | Maximize | $\text{norm}(L/D, 5.0, 25.0)$ |
| | | `structures` | 0.20 | Minimize | $\text{norm}(m_{\text{wing}}/m_{\text{mtow}}, 0.05, 0.25)$ parsed from notes |
| | | `mission` | 0.20 | Maximize | $1.0 - |AR - AR_{\text{target}}| / AR_{\text{target}}$ |
| | | `stability` | 0.15 | Maximize | $1.0 - 0.2 \times N_{\text{warnings}}$ |
| | | `manufacturability` | 0.10 | Maximize | $1.0 - 0.5 \times \text{pen}(AR) - 0.5 \times \text{pen}(\Lambda)$ |
| | | `packaging` | 0.05 | Maximize | Fixed packaging suitability metric |
| **FuselageOptimizer** | `FuselageObjectiveFunction` | `packaging` | 0.25 | Maximize | $\text{norm}(\text{Vol}_{\text{util}}, 0.10, 0.90)$ |
| | | `structures` | 0.20 | Minimize | $\text{norm}(L(w+h) \times 4.0, 0.5, 5.0)$ |
| | | `aerodynamics` | 0.20 | Maximize | $1.0 - |FR - 8.0| / 8.0$ |
| | | `manufacturability` | 0.15 | Maximize | Circular: 1.0, Rounded: 0.9, Rect: 0.8, Oval: 0.7 |
| | | `cg_margin` | 0.15 | Maximize | $1.0 - |K_n - 15\%| / 15\%$ |
| | | `mission` | 0.05 | Maximize | $1.0 - 0.2 \times N_{\text{warnings}}$ |
| **PayloadPackagingOptimizer**| `PayloadObjectiveFunction` | `packaging` | 0.30 | Maximize | Volume packaging density fraction |
| | | `serviceability` | 0.20 | Maximize | Hatch access clearance score |
| | | `routing` | 0.20 | Maximize | Cable route length penalty |
| | | `cooling` | 0.15 | Maximize | Thermal airflow path clearance |
| | | `cg_flexibility` | 0.15 | Maximize | Allowable placement translation range |
| **TailOptimizer** | `TailObjectiveFunction` | `longitudinal_stability`| 0.25 | Minimize | $|V_h - 0.55|$ (unnormalized deviation) |
| | | `directional_stability` | 0.15 | Minimize | $|V_v - 0.04|$ (unnormalized deviation) |
| | | `low_drag` | 0.15 | Minimize | $S_h + S_v$ ($m^2$ wetted area, unnormalized) |
| | | `structural_weight` | 0.10 | Minimize | $(S_h + S_v) \times L_t$ ($m^3$, unnormalized) |
| | | `manufacturability` | 0.15 | Maximize | Score / 100.0 ($[0, 1]$) |
| | | `mission_suitability` | 0.10 | Maximize | Score / 100.0 ($[0, 1]$) |
| | | `cg_robustness` | 0.10 | Minimize | $\max(0, 0.8 - V_h) + \max(0, 0.65 - L_t/b)$ |
| **PropulsionOptimizer** | `PropulsionObjectiveFunction` | `propulsion_score` | 1.00 | Maximize | Composite: $0.15\,\eta_{\text{elec}} + 0.15\,w_{\text{pen}} + 0.15\,P_{\text{cruise}} + 0.15\,T/W + 0.20\,t_{\text{endur}} + 0.10\,\text{rel} + 0.10\,\text{esc}$ |
| **ElectricalOptimizer** | `ElectricalObjectiveFunction` | `electrical_score` | 1.00 | Maximize | Composite: $0.20\,\text{rel} + 0.15\,\text{pwr} + 0.15\,w + 0.10\,\text{cost} + 0.10\,\text{mfg} + 0.10\,\text{serv} + 0.10\,\text{compat} + 0.10\,\text{upg}$ |
| **MassPropertiesOptimizer** | `MassObjectiveFunction` | `mass_score` | 1.00 | Maximize | Composite: $0.20\,m_{\text{empty}} + 0.20\,\text{pay}_{\text{frac}} + 0.15\,\text{struct} + 0.15\,\text{mfg} + 0.15\,E_{\text{eff}} + 0.15\,\text{growth}$ |
| **CGOptimizer** | `CGObjectiveFunction` | `cg_score` | 1.00 | Maximize | Composite: $0.30\,K_n + 0.20\,\text{order} + 0.15\,\text{mission} + 0.15\,\Delta x + 0.20\,\text{flex}$ |
| **FlightPerformanceOptimizer**| N/A | `performance_score` | 1.00 | Maximize | Single candidate evaluator; checks performance margin |

---

## 5. OPTIMIZATION PRIORITY AUDIT

### 5.1 Enumeration Analysis
The enum `OptimizationPriority` (`backend/design/common/requirements/optimization_priority.py`) defines 7 targets:
1. `BALANCED`
2. `LOWEST_COST`
3. `LOWEST_WEIGHT`
4. `MAXIMUM_ENDURANCE`
5. `MAXIMUM_RANGE`
6. `MAXIMUM_PAYLOAD`
7. `HIGHEST_EFFICIENCY`

### 5.2 Propagation & Pipeline Tracing
1. In `RequirementModel`, `optimization_priority: OptimizationPriority = OptimizationPriority.BALANCED`.
2. In `MissionTranslationStage.execute()` (`backend/design/fixed_wing/pipeline/pipeline_stage.py`), inputs are mapped to `MissionRequirements`. **`optimization_priority` is completely omitted** and never copied to `MissionRequirements`.
3. In `OptimizationContext`, `context.requirements.raw_requirements` holds the original `RequirementModel`.
4. Across all 9 subsystem optimizers, grep searches confirmed **zero references** to `optimization_priority`.

### 5.3 Empirical Audit Table

| Priority | Intended Optimization Target | Actual Pipeline Effect | Design Difference vs BALANCED | Verified Status |
| :--- | :--- | :--- | :---: | :---: |
| **BALANCED** | Tradeoff across cost, weight, range, endurance | Baseline fixed-wing sizing weights | 0.00% (Baseline) | **DISCONNECTED** |
| **LOWEST_COST** | Minimize BOM component costs | No effect; cost is never evaluated | 0.00% | **DISCONNECTED** |
| **LOWEST_WEIGHT** | Minimize MTOW / structural mass | No effect; weight terms unchanged | 0.00% | **DISCONNECTED** |
| **MAXIMUM_ENDURANCE** | Maximize flight minutes | No effect; propulsion weights unchanged | 0.00% | **DISCONNECTED** |
| **MAXIMUM_RANGE** | Maximize distance covered | No effect; range weights unchanged | 0.00% | **DISCONNECTED** |
| **MAXIMUM_PAYLOAD** | Maximize payload fraction | No effect; payload sizing unchanged | 0.00% | **DISCONNECTED** |
| **HIGHEST_EFFICIENCY** | Maximize L/D and powertrain efficiency | No effect; aerodynamic weights unchanged | 0.00% | **DISCONNECTED** |

*Conclusion:* `OptimizationPriority` is currently non-functional in the Fixed-Wing pipeline.

---

## 6. DESIGN MODE AUDIT

### 6.1 Enumeration Analysis
The enum `DesignMode` (`backend/design/common/requirements/design_mode.py`) defines:
- `ENGINEERING_ADVISOR`: AI analyzes requirements and recommends category with trade-offs.
- `MANUAL`: User specifies aircraft category directly.

### 6.2 Implementation Tracing
- Tracing across `backend/design/fixed_wing/` revealed **zero references** to `design_mode`.
- The design mode is checked solely in `backend/design/common/validation/validation_rule.py`:
  ```python
  if requirements.design_mode == DesignMode.MANUAL and requirements.aircraft_type is None:
      errors.append("Aircraft type must be explicitly specified when running in MANUAL mode.")
  ```
- *Conclusion:* `DesignMode` governs only upstream category recommendation workflows; inside the fixed-wing sizing and optimization pipeline, execution paths, candidate generations, and scoring functions are 100% identical.

---

## 7. HARD CONSTRAINT INVENTORY

A complete forensic inventory of all hard constraints across the fixed-wing design backend:

| Constraint Name | Source File | Threshold / Boundary | Rejection Timing | Scope |
| :--- | :--- | :--- | :---: | :--- |
| `MTOW_gt_Payload` | `pipeline_stage.py:MissionTranslationStage` | $\text{MTOW}_{\text{limit}} > m_{\text{payload}}$ | Pre-Convergence (Stage 0) | All missions |
| `Max_Flight_Time` | `pipeline_stage.py:MissionTranslationStage` | $t_{\text{flight}} \le 1440.0\text{ min}$ ($24\text{ h}$) | Pre-Convergence (Stage 0) | All missions |
| `Speed_Range_Consistency` | `pipeline_stage.py:MissionTranslationStage` | $R \le V_{\text{cruise}} \times t_{\text{flight}}$ | Pre-Convergence (Stage 0) | All missions |
| `Max_Cruise_Speed` | `pipeline_stage.py:MissionTranslationStage` | $V_{\text{cruise}} \le 350.0\text{ km/h}$ | Pre-Convergence (Stage 0) | All missions |
| `Wing_Taper_Bounds` | `wing/optimization/constraints.py` | $\lambda \in [0.35, 1.00]$ | Candidate Pre-Screening | Wing Optimizer |
| `Wing_Root_Chord_Fuselage` | `wing/optimization/constraints.py` | $c_{\text{root}} \ge 1.10 \times w_{\text{fuse}}$ | Candidate Pre-Screening | Wing Optimizer |
| `Min_Chord_Limits` | `wing/optimization/constraints.py` | $c_{\text{root}} \ge 0.05\text{ m}, c_{\text{tip}} \ge 0.05\text{ m}$ | Candidate Pre-Screening | Wing Optimizer |
| `Fuselage_Cross_Section` | `fuselage/optimization/constraints.py` | $w \ge w_{\text{pay}} + 0.04\text{ m}, h \ge h_{\text{pay}} + 0.04\text{ m}$ | Candidate Pre-Screening | Fuselage Optimizer |
| `Fuselage_Fineness` | `fuselage/optimization/constraints.py` | $L/D \in [4.0, 14.0]$ | Candidate Pre-Screening | Fuselage Optimizer |
| `Payload_Bay_Volume` | `fuselage/optimization/constraints.py` | $\text{Vol}_{\text{bay}} \ge \text{Vol}_{\text{payload}}$ | Candidate Pre-Screening | Fuselage Optimizer |
| `Payload_No_Overlap` | `payload/optimization/constraints.py` | $\Delta x \ge 0.02\text{ m}$ between components | Candidate Pre-Screening | Payload Optimizer |
| `Payload_Spar_Collision` | `payload/optimization/constraints.py` | No overlap with spar box | Candidate Pre-Screening | Payload Optimizer |
| `GPS_RF_Clearance` | `payload/optimization/constraints.py` | Separation $\ge 0.10\text{ m}$ | Candidate Pre-Screening | Payload Optimizer |
| `Tail_Static_Margin` | `tail/optimization/constraints.py` | $K_n \ge 0.05$ ($5\%$ MAC) | Candidate Pre-Screening | Tail Optimizer |
| `Tail_Directional_Volume` | `tail/optimization/constraints.py` | $V_v \ge 0.02$ | Candidate Pre-Screening | Tail Optimizer |
| `Tail_Span_Ratio` | `tail/optimization/constraints.py` | $b_{\text{tail}} \le 0.45 \times b_{\text{wing}}$ | Candidate Pre-Screening | Tail Optimizer |
| `Tail_Arm_Bounds` | `tail/optimization/constraints.py` | $L_t \in [0.3\,b, 0.7\,b]$ | Candidate Pre-Screening | Tail Optimizer |
| `Motor_ESC_Current` | `propulsion/optimization/constraints.py`| $I_{\text{max,motor}} \le I_{\text{cont,esc}}$ | Candidate Pre-Screening | Propulsion Optimizer |
| `ESC_Battery_Voltage` | `propulsion/optimization/constraints.py`| $S_{\text{battery}} \le S_{\text{max,esc}}$ | Candidate Pre-Screening | Propulsion Optimizer |
| `Battery_Motor_Voltage` | `propulsion/optimization/constraints.py`| $S_{\text{battery}} == S_{\text{motor}}$ | Candidate Pre-Screening | Propulsion Optimizer |
| `Propeller_Clearance` | `propulsion/optimization/constraints.py`| $D_{\text{prop}} \le D_{\text{max,clearance}}$ | Candidate Pre-Screening | Propulsion Optimizer |
| `Static_Takeoff_Thrust` | `propulsion/optimization/constraints.py`| $T_{\text{static}} \ge T_{\text{req,takeoff}}$ | Candidate Pre-Screening | Propulsion Optimizer |
| `Cruise_Thrust_Required` | `propulsion/optimization/constraints.py`| $T_{\text{cruise}} \ge D_{\text{cruise}}$ | Candidate Pre-Screening | Propulsion Optimizer |
| `Climb_Power_Required` | `propulsion/optimization/constraints.py`| $P_{\text{avail}} \ge P_{\text{climb}}(2.5\text{ m/s})$ | Candidate Pre-Screening | Propulsion Optimizer |
| `Motor_Thermal_Continuous`| `propulsion/optimization/constraints.py`| $P_{\text{cruise}} \le 0.75 \times P_{\text{max,motor}}$ | Candidate Pre-Screening | Propulsion Optimizer |
| `Battery_Discharge_Rate` | `propulsion/optimization/constraints.py`| $I_{\text{climb}} \le I_{\text{max,discharge}}$ | Candidate Pre-Screening | Propulsion Optimizer |
| `Telemetry_Range_Limit` | `electrical/optimization/constraints.py` | $R_{\text{req}} \le 80.0\text{ km}$ (Catalog Max) | Candidate Pre-Screening | Electrical Optimizer |
| `User_MTOW_Ceiling` | `mass_properties/optimization/` | $\text{MTOW} \le \text{MTOW}_{\text{user}}$ | Candidate Pre-Screening | Mass Optimizer |
| `Mass_Non_Negativity` | `mass_properties/optimization/` | All 22 component masses $> 0$ | Candidate Pre-Screening | Mass Optimizer |
| `Static_Margin_Corridor` | `cg/optimization/constraints.py` | $K_n \in [0.05, 0.25]$ | Candidate Pre-Screening | CG Optimizer |
| `Performance_Endurance` | `performance/optimization/` | $t_{\text{endurance}} \ge t_{\text{target}}$ | Candidate Pre-Screening | Performance Optimizer |
| `Performance_Range` | `performance/optimization/` | $R_{\text{cruise}} \ge R_{\text{target}}$ | Candidate Pre-Screening | Performance Optimizer |
| `Mass_Conservation_Rule` | `common/verification/mass_properties` | Discrepancy $\le 0.10\%$ | Post-Convergence (Stage 13)| Final Certification |
| `Aero_Polar_Rule` | `common/verification/` | $L/D \in [8.0, 25.0]$ | Post-Convergence (Stage 13)| Final Certification |

---

## 8. SOFT OBJECTIVE INVENTORY

Soft objectives are parameters that influence ranking among feasible candidates without causing candidate disqualification:

| Subsystem | Soft Objective | Implementation Mechanism | Range | Preferred Direction |
| :--- | :--- | :--- | :---: | :---: |
| **Wing** | Cruise $L/D$ | Scaled via `normalize_value(L/D, 5.0, 25.0)` | $[0, 1]$ | Higher |
| **Wing** | Structural Weight Fraction | Scaled via `normalize_value(m_wing/MTOW, 0.05, 0.25)` | $[0, 1]$ | Lower |
| **Wing** | Aspect Ratio Proximity | Proximity to strategy target $AR$ | $[0, 1]$ | Target Proximity |
| **Wing** | Fabrication Simplicity | Penalty for sweep $> 0^\circ$ and $AR > 8.0$ | $[0, 1]$ | Lower Complexity |
| **Fuselage** | Volume Utilization | Proximity of payload/internal ratio to $60-80\%$ | $[0, 1]$ | Target Proximity |
| **Fuselage** | External Wetted Area | Penalty proportional to $L \times (w + h)$ | $[0, 1]$ | Lower |
| **Fuselage** | Fineness Ratio Proximity | Proximity to aerodynamic optimum $FR = 8.0$ | $[0, 1]$ | Target Proximity |
| **Fuselage** | Cross-Section Shape | Circular ($1.0$) $>$ Rounded ($0.9$) $>$ Rect ($0.8$) | $[0.7, 1.0]$ | Higher |
| **Tail** | $V_h$ Proximity | Deviation $|V_h - 0.55|$ | $[0, 0.2]$ | Closer to 0.55 |
| **Tail** | $V_v$ Proximity | Deviation $|V_v - 0.04|$ | $[0, 0.03]$ | Closer to 0.04 |
| **Tail** | Parasitic Tail Drag | Sum of stabilizer areas ($S_h + S_v$) | $[0.02, 0.15]\text{ m}^2$ | Lower |
| **Tail** | Tail Structural Weight | Area $\times$ Moment Arm ($(S_h + S_v) \times L_t$) | $[0.01, 0.08]\text{ m}^3$ | Lower |
| **Propulsion**| Total Propulsion Mass | Linear score $1.0 - (m_{\text{prop}} / 4000\text{ g})$ | $[0, 1]$ | Lower |
| **Propulsion**| Cruise Power Demand | Linear score $1.0 - (P_{\text{cruise}} / 2000\text{ W})$ | $[0, 1]$ | Lower |
| **Propulsion**| Takeoff Thrust Margin | Linear score $(T/W - 1.0) / 1.5$ | $[0, 1]$ | Higher |
| **Propulsion**| Flight Endurance | Linear score $t_{\text{endurance}} / 180\text{ min}$ | $[0, 1]$ | Higher |
| **Propulsion**| Motor Thermal Margin | $1.0 - I_{\text{climb}} / I_{\text{max,motor}}$ | $[0, 1]$ | Higher |
| **Propulsion**| ESC Current Headroom | $1.0 - I_{\text{climb}} / I_{\text{cont,esc}}$ | $[0, 1]$ | Higher |
| **Electrical** | Power Bus Redundancy | Dual redundant bus ($1.0$) vs single ($0.6$) | $[0.6, 1.0]$ | Higher |
| **Electrical** | Component Cost | Linear scaling on catalog BOM price | $[0, 1]$ | Lower |
| **Mass** | Empty Weight Fraction | $1.0 - (m_{\text{empty}} / \text{MTOW}_{\text{limit}})$ | $[0, 1]$ | Lower |
| **Mass** | Payload Mass Fraction | $m_{\text{payload}} / \text{MTOW}$ scaled to $0.50$ | $[0, 1]$ | Higher |
| **CG** | Target Static Margin | Proximity to $K_n = 0.15$ ($15\%$ MAC) | $[0, 1]$ | Target Proximity |
| **CG** | Packaging Layout Order | FC forward, battery middle, payload aft | $[0.7, 1.0]$ | Layout Compliance |

---

## 9. NORMALIZATION AUDIT

A critical requirement of multi-objective optimization is that all terms in a weighted sum share identical scaling (typically $[0.0, 1.0]$), or else terms with large raw values inadvertently override terms with small raw values.

### 9.1 Subsystem Normalization Findings

1. **`WingObjectiveFunction`:**
   - Properly normalized via `normalize_value(val, min, max)` to $[0.0, 1.0]$.
   - *Fragility:* Extracts MTOW and wing weight by parsing unstructured English text strings in `engineering_notes` (`if "Estimated MTOW:" in note:`).
2. **`FuselageObjectiveFunction`:**
   - Properly normalized via `normalize_value()` to $[0.0, 1.0]$.
3. **`PayloadObjectiveFunction`:**
   - Properly normalized to $[0.0, 1.0]$.
4. **`TailObjectiveFunction` (CRITICAL FLAW FOUND):**
   - **Severe unnormalized dimensional mixing**:
     - `longitudinal_stability`: $|V_h - 0.55| \approx 0.01\text{ to }0.08$ (dimensionless).
     - `directional_stability`: $|V_v - 0.04| \approx 0.005\text{ to }0.02$ (dimensionless).
     - `low_drag`: $S_h + S_v \approx 0.03\text{ to }0.09\text{ m}^2$ (area in square meters).
     - `structural_weight`: $(S_h + S_v) \times L_t \approx 0.01\text{ to }0.05\text{ m}^3$ (volume proxy).
     - `manufacturability`: Score $/ 100.0 \approx 0.70\text{ to }0.95$ ($[0, 1]$).
     - `mission_suitability`: Score $/ 100.0 \approx 0.80\text{ to }0.90$ ($[0, 1]$).
   - *Consequence:* The manufacturability and mission suitability terms ($\approx 0.85$) are **$40\times$ to $100\times$ larger** in magnitude than the stability deviation terms ($\approx 0.01$). Even though stability has a weight of $0.25$, its numerical impact on the score is completely dominated by manufacturability.
5. **`PropulsionObjectiveFunction`:**
   - All 7 sub-terms are scaled to $[0.0, 1.0]$.
   - *Limitation:* The endurance term is normalized against an arbitrary $180\text{ min}$ ceiling rather than the mission requirement target.
6. **`ElectricalObjectiveFunction`:**
   - Properly normalized to $[0.0, 1.0]$.
7. **`MassObjectiveFunction`:**
   - Properly normalized to $[0.0, 1.0]$.
8. **`CGObjectiveFunction`:**
   - Properly normalized to $[0.0, 1.0]$.

---

## 10. CANDIDATE GENERATION AUDIT

### 10.1 Generation Strategies Across Subsystems

| Optimizer | Generation Method | Candidate Count | Design Variables Swept | Search Space Nature |
| :--- | :--- | :---: | :--- | :--- |
| **WingPlanformOptimizer** | Deterministic Cartesian Grid | **5,292** | $AR \in [8, 16]$ (step 1.0), $\lambda \in [0.35, 1.0]$ (step 0.05), $\Lambda \in [0^\circ, 10^\circ]$ (step 2.0), $\Gamma \in [0^\circ, 6^\circ]$ (step 1.0) | Continuous geometric grid |
| **FuselageOptimizer** | Permutation Grid | **128** | Length (4), Width (4), Height (4), Cross-section (2) | Parametric geometry |
| **PayloadPackagingOptimizer**| Spatial Permutation | **64** | Bay position fractions, clearance orientations | Internal bay coordinates |
| **TailOptimizer** | Factorial Grid | **160** | Configuration (5), $V_h$ (2), $V_v$ (2), $\lambda_h$ (2), $\lambda_v$ (2), $\Gamma_t$ (5) | Discrete structural layouts |
| **PropulsionOptimizer** | Database Cross-Product | **411** | Motor (6 COTS) $\times$ Propeller (12 COTS) $\times$ ESC (3 COTS) $\times$ Battery (42 COTS packs) | Discrete component catalog |
| **ElectricalOptimizer** | Component Compatibility | **8** | FC (2), GPS (2), Layout (2) filtered by avionics match | Discrete component catalog |
| **MassPropertiesOptimizer** | Margin Permutation | **24** | Structural margin (3), Fastener (2), Paint (2), Growth (2) | Engineering allowance fractions |
| **CGOptimizer** | Positional Grid | **384** | Battery station (8), Payload station (8), Avionics station (6) | Longitudinal coordinates |
| **FlightPerformanceOptimizer**| Baseline Single-Point | **1** | None (`{}`) | Analysis-only evaluation |

### 10.2 Architectural Observations
- `WingPlanformOptimizer` generates a huge initial pool ($5,292$ candidates), but pre-screening constraints (`manufacturing_limits` and `analytical_geometry`) immediately prune $>90\%$ of them before full wing evaluation.
- `FlightPerformanceOptimizer` does not generate design variations; it performs a single verification pass on the assembled aircraft.

---

## 11. CANDIDATE EVALUATION AUDIT

### 11.1 Fresh State vs Stale State Verification
- During Phase 3, a critical bug was identified where payload bay geometry was frozen from Iteration 1 and never updated as fuselage dimensions scaled.
- The Phase 6A audit verified `IterationController.run_iteration()`:
  - In each iteration pass, every subsystem updates `context.requirements.<subsystem>_result` and `context.previous_specifications`.
  - When `FuselageOptimizer` resizes the fuselage, lines 71–79 of `iteration_controller.py` dynamically push the new payload bay length, width, and height into `payload_result.payload_layout`.
  - When `CGOptimizer` adjusts component positions, lines 131–164 immediately recalculate moments of inertia and push updated CG stations into `mass_properties_result`.
- **Verdict:** Candidate evaluation operates on fresh, synchronized physical states during each iteration.

---

## 12. SENSITIVITY EXPERIMENTS (OPTIMIZATION PRIORITY)

Controlled experimental campaign holding all mission inputs constant (Survey, $0.5\text{ kg}$ payload, $45\text{ min}$ flight time, $30\text{ km}$ range, $70\text{ km/h}$ cruise, Runway / Runway, Rural) while varying `OptimizationPriority`:

```
========================================================================================
             STEP 8: OPTIMIZATION PRIORITY SENSITIVITY EXPERIMENT RESULTS
========================================================================================
```

| Priority Tested | MTOW (kg) | Span (m) | AR | Area (m²) | Cruise Power (W) | Endurance (min) | Motor Selected | Propeller | Overall Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: |
| **BALANCED** | 4.367 | 1.801 | 10.0 | 0.324 | 99.2 | 98.9 | T-Motor AT3520 | 11x7 APC | 0.000 |
| **LOWEST_COST** | 4.367 | 1.801 | 10.0 | 0.324 | 99.2 | 98.9 | T-Motor AT3520 | 11x7 APC | 0.000 |
| **LOWEST_WEIGHT** | 4.367 | 1.801 | 10.0 | 0.324 | 99.2 | 98.9 | T-Motor AT3520 | 11x7 APC | 0.000 |
| **MAXIMUM_ENDURANCE**| 4.367 | 1.801 | 10.0 | 0.324 | 99.2 | 98.9 | T-Motor AT3520 | 11x7 APC | 0.000 |
| **MAXIMUM_RANGE** | 4.367 | 1.801 | 10.0 | 0.324 | 99.2 | 98.9 | T-Motor AT3520 | 11x7 APC | 0.000 |
| **MAXIMUM_PAYLOAD** | 4.367 | 1.801 | 10.0 | 0.324 | 99.2 | 98.9 | T-Motor AT3520 | 11x7 APC | 0.000 |
| **HIGHEST_EFFICIENCY**| 4.367 | 1.801 | 10.0 | 0.324 | 99.2 | 98.9 | T-Motor AT3520 | 11x7 APC | 0.000 |

### Forensic Finding:
**Zero variation observed.** Across all 7 priorities, every single design variable, component selection, aerodynamic dimension, and performance prediction was **$100.000\%$ identical**.

---

## 13. PAYLOAD SENSITIVITY

Auditing how the design variables scale as payload weight increases from $0.20\text{ kg}$ to $2.00\text{ kg}$ under Survey mission requirements:

| Payload (kg) | MTOW (kg) | Payload Fraction | Wingspan (m) | Wing Area (m²) | Cruise Power (W) | Thrust / Weight | Static Margin |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0.20** | 4.009 | 5.0% | 1.725 | 0.298 | 91.2 | 0.90 | 15.0% |
| **0.50** | 4.367 | 11.4% | 1.801 | 0.324 | 99.2 | 0.83 | 16.2% |
| **1.00** | 4.970 | 20.1% | 1.921 | 0.369 | 112.7 | 0.73 | 15.6% |
| **1.50** | 5.605 | 26.8% | 2.040 | 0.416 | 126.8 | 0.65 | 15.6% |
| **2.00** | 6.196 | 32.3% | 2.145 | 0.460 | 140.0 | 0.59 | 14.4% |

### Forensic Finding:
- Payload scaling is **strictly monotonic and smooth**.
- MTOW scales at approximately $+1.21\text{ kg}$ per kilogram of payload added (an empty weight multiplier of $1.21$, highly realistic for carbon/foam composite airframes).
- Wing area expands proportionally to preserve a nearly constant wing loading ($\approx 13.4\text{ kg/m}^2$), ensuring stall speeds remain sub-$45\text{ km/h}$.
- Cruise power scales smoothly from $91.2\text{ W}$ to $140.0\text{ W}$ as weight and induced drag increase.

---

## 14. RANGE / ENDURANCE SENSITIVITY

### 14.1 Range Sensitivity Campaign
Evaluating range targets from $20\text{ km}$ to $80\text{ km}$ with physically consistent flight times:

| Target Range | Target Flight Time | Converged MTOW | Battery Mass | Wing Area | Cruise Power | Actual Range Achieved | Actual Endurance |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **20 km** | 30 min | 4.367 kg | 1.232 kg | 0.3243 m² | 99.2 W | 116.0 km | 99.4 min |
| **30 km** | 45 min | 4.367 kg | 1.232 kg | 0.3243 m² | 99.2 W | 115.4 km | 98.9 min |
| **50 km** | 60 min | 4.367 kg | 1.232 kg | 0.3243 m² | 99.2 W | 114.1 km | 97.8 min |
| **70 km** | 75 min | 4.367 kg | 1.232 kg | 0.3243 m² | 99.2 W | 111.1 km | 95.2 min |
| **80 km** | 80 min | 4.367 kg | 1.232 kg | 0.3243 m² | 99.2 W | 111.1 km | 95.2 min |

### 14.2 Endurance Sensitivity Campaign
Holding target range constant at $25\text{ km}$ while varying flight time from $30\text{ min}$ to $90\text{ min}$:

| Target Flight Time | Converged MTOW | Battery Mass | Wing Area | Cruise Power | Actual Endurance Achieved |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **30 min** | 4.367 kg | 1.232 kg | 0.3243 m² | 99.2 W | 99.0 min |
| **45 min** | 4.367 kg | 1.232 kg | 0.3243 m² | 99.2 W | 99.0 min |
| **60 min** | 4.367 kg | 1.232 kg | 0.3243 m² | 99.2 W | 99.0 min |
| **90 min** | 4.367 kg | 1.232 kg | 0.3243 m² | 99.2 W | 99.0 min |

### Forensic Finding:
1. **Battery Selection Inelasticity:**
   In all runs, the optimizer selected the **identical 6S 5000mAh battery pack ($1.232\text{ kg}$)**.
2. **Root Cause:**
   The `PropulsionObjectiveFunction` assigns a high weight ($0.35$) to `endurance`, which scores candidates based on $t_{\text{endurance}} / 180.0$. It does not reward *matching* the requested flight time; it simply rewards *maximizing* flight time up to 180 min. Because a 5000mAh pack satisfies all flight time constraints between 30 and 90 min and beats smaller packs (like 2200mAh or 3300mAh) in the objective score, the design is completely insensitive to flight times below 90 min.

---

## 15. BUDGET AUDIT

Auditing how financial budget constraints affect fixed-wing design optimization:

| Budget Specified | Converged MTOW | Motor Selected | Propeller | Cruise Power | Design Difference vs $15,000 |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **\$500** | 4.367 kg | T-Motor AT3520 | 11x7 APC | 99.2 W | **0.00% (Identical)** |
| **\$2,000** | 4.367 kg | T-Motor AT3520 | 11x7 APC | 99.2 W | **0.00% (Identical)** |
| **\$15,000** | 4.367 kg | T-Motor AT3520 | 11x7 APC | 99.2 W | **Baseline** |
| **\$50,000** | 4.367 kg | T-Motor AT3520 | 11x7 APC | 99.2 W | **0.00% (Identical)** |

### Forensic Finding:
`budget` is purely metadata. Changing budget from \$500 to \$50,000 has zero influence on component selection, material choice, or airframe sizing.

---

## 16. PARETO / MULTI-OBJECTIVE CAPABILITY

- **Current Status:** **Pareto capability: not currently implemented in the Fixed-Wing design backend.**
- While the multirotor module (`backend/design/drone/optimization/pareto_front.py`) implements non-dominated sorting and Pareto front extraction, the Fixed-Wing pipeline uses single-objective scalarized weighted sums.
- **Key Tradeoffs That Would Benefit from Pareto Analysis:**
  1. *Payload Capacity vs Flight Endurance* ($m_{\text{payload}}$ vs $t_{\text{endur}}$).
  2. *Airframe Empty Weight vs Maximum Cruise Airspeed* (structure/wing loading vs drag).
  3. *Battery Mass Fraction vs Climb Performance* ($m_{\text{bat}}$ vs $T/W$).
  4. *Bill-of-Materials Cost vs Structural Mass* (composite fabrication vs foam core).

---

## 17. BASELINE ENGINEERING QUALITY METRICS

Metrics extracted from the 7 canonical validated cases:

| Mission Case | MTOW (kg) | Payload Frac | Empty Frac | Battery Frac | Struct Frac | $T/W$ | $W/S$ (kg/m²) | $AR$ | Static Margin | Cruise Power | $L/D$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **SURVEY 0.5kg** | 4.367 | 11.4% | 55.4% | 28.2% | 38.2% | 0.83 | 13.46 | 10.0 | +16.2% | 99.2 W | 15.7 |
| **SURVEY 1.0kg** | 4.970 | 20.1% | 55.1% | 24.8% | 38.2% | 0.73 | 13.47 | 10.0 | +15.6% | 127.4 W | 14.9 |
| **AGRICULTURE 2.0kg** | 5.802 | 34.5% | 44.3% | 21.2% | 30.5% | 0.69 | 13.47 | 8.0 | +15.5% | 129.1 W | 14.9 |
| **SECURITY 0.5kg** | 3.921 | 12.8% | 55.8% | 31.4% | 38.6% | 0.68 | 13.46 | 9.0 | +14.4% | 92.5 W | 15.2 |
| **INSPECTION 0.5kg** | 3.921 | 12.8% | 55.8% | 31.4% | 38.6% | 0.68 | 13.46 | 9.0 | +14.4% | 75.8 W | 15.9 |
| **MILITARY 1.5kg** | 7.047 | 21.3% | 61.2% | 17.5% | 44.5% | 0.68 | 13.50 | 9.0 | +15.4% | 236.1 W | 12.9 |
| **DELIVERY 1.0kg** | 4.388 | 22.8% | 49.1% | 28.1% | 33.9% | 0.72 | 13.46 | 8.0 | +14.8% | 107.8 W | 14.6 |

---

## 18. OPTIMIZATION EFFECTIVENESS CLASSIFICATION

Based on the forensic evidence gathered in Steps 1–17:

### Formal Classification: **C. MOSTLY HEURISTIC / CONSTRAINED-GRID SELECTION**

**Rationale & Supporting Evidence:**
1. *Subsystem Grid Search with Hard Constraints:* The pipeline does not employ mathematical optimization (e.g., gradient descent, SQP, Nelder-Mead, or genetic algorithms). Instead, it generates discrete candidate grids and prunes them using hard constraints.
2. *Dominance of Screening Constraints:* The design outcome is almost entirely determined by physical constraints (wing loading for stall speed, root chord clearance vs fuselage width, telemetry range, catalog discrete sizes) rather than objective function optimization.
3. *Complete Priority Ineffectiveness:* `OptimizationPriority` and `budget` have zero influence on design outputs.
4. *Static Objective Weights:* Weights within each subsystem are hardcoded or keyed to `MissionCategory`, offering no user-driven trade-off customization.

---

## 19. CONFIRMED BUGS FOUND

1. **`OptimizationPriority` Complete Decoupling:**
   - *Location:* `backend/design/fixed_wing/pipeline/pipeline_stage.py:MissionTranslationStage` and all 9 subsystem optimizers.
   - *Effect:* Enum `OptimizationPriority` is completely ignored; all priorities produce identical designs.
2. **`DesignMode` Inactivity in Fixed-Wing:**
   - *Location:* `backend/design/fixed_wing/pipeline/pipeline_stage.py`.
   - *Effect:* `DesignMode` is ignored; `ENGINEERING_ADVISOR` and `MANUAL` execute identical sizing paths.
3. **Budget Decoupling:**
   - *Location:* `backend/design/fixed_wing/pipeline/pipeline_stage.py` and all optimizers.
   - *Effect:* `budget` is ignored; budgets from \$500 to \$50,000 select identical components.
4. **`TailObjectiveFunction` Severe Normalization Distortion:**
   - *Location:* `backend/design/fixed_wing/tail/optimization/objective_function.py`.
   - *Effect:* Stability terms ($\sim 0.01$) are summed with unnormalized manufacturability scores ($\sim 0.85$), skewing tail selection towards manufacturability over stability by a factor of 100.
5. **`WingObjectiveFunction` String-Parsing Fragility:**
   - *Location:* `backend/design/fixed_wing/wing/optimization/objective_function.py:58-67`.
   - *Effect:* Structural weight and MTOW are extracted by parsing English text sentences in `res.engineering_notes` rather than accessing structured numerical fields.
6. **Propulsion Battery Sizing Inelasticity:**
   - *Location:* `backend/design/fixed_wing/propulsion/optimization/objective_function.py`.
   - *Effect:* Raw flight time is maximized rather than rewarding proximity to requested endurance, forcing over-sized battery packs even for modest flight time requests.

---

## 20. BUGS FIXED

Per Phase 6A mandate:
**NONE.** This is an audit-only phase. No production code was modified. All identified items are cataloged for remediation in Phase 6B.

---

## 21. RECOMMENDED PHASE 6B IMPROVEMENTS

1. **Wire `OptimizationPriority` to Subsystem Objective Weights:**
   Connect `RequirementModel.optimization_priority` through `MissionTranslationStage` and dynamically re-weight objective terms across all 9 optimizers (e.g., in `LOWEST_WEIGHT`, boost mass penalty; in `MAXIMUM_ENDURANCE`, bias battery selection; in `HIGHEST_EFFICIENCY`, maximize $L/D$).
2. **Normalize `TailObjectiveFunction`:**
   Apply `normalize_value()` to stability deviations and wetted areas so all terms inhabit $[0.0, 1.0]$.
3. **Refactor `WingObjectiveFunction` Note Parsing:**
   Directly reference structured numerical attributes (`wing_geometry.area_m2`, `wing_weight_kg`) instead of parsing text from `engineering_notes`.
4. **Target-Aware Battery Sizing:**
   Update `PropulsionObjectiveFunction` to score endurance based on proximity to target flight time ($1.0 - |t_{\text{actual}} - t_{\text{target}}| / t_{\text{target}}$) rather than open-ended maximization, allowing lighter batteries for shorter missions.
5. **Component Catalog Budget Filtering:**
   Incorporate `budget` into component selection (filtering out high-end sensors/motors when budget is tight).
6. **Fixed-Wing Pareto Front Generator:**
   Port the non-dominated Pareto front extractor from the multirotor module to enable multi-objective trade-off analysis (e.g. Payload vs Endurance).

---

## 22. PRIORITY RANKING FOR PHASE 6B

| Rank | Improvement Item | Architectural Scope | Impact | Rationale |
| :---: | :--- | :--- | :---: | :--- |
| **P0** | Wire `OptimizationPriority` across all 9 optimizers | Pipeline & Optimizers | High | Restores functional integrity to core requirement API |
| **P0** | Normalize `TailObjectiveFunction` terms | Tail Optimizer | High | Eliminates $100\times$ numerical scale distortion in tail design |
| **P1** | Target-Aware Battery / Endurance Sizing | Propulsion Optimizer | High | Prevents carrying excessive deadweight battery mass |
| **P1** | Refactor `WingObjectiveFunction` string parsing | Wing Optimizer | Medium | Eliminates fragile English text scraping in optimization loop |
| **P2** | Budget-Constrained Component Catalog Pruning | Propulsion / Avionics | Medium | Makes user budget constraints functionally meaningful |
| **P3** | Pareto Front Multi-Objective Trade-Off Extractor | Reporting & Studio | Low | Advanced visualization and design exploration capability |

---

## 23. REGRESSION RESULTS

Execution of the full automated test suite (`tests/design/fixed_wing/ -q`):
- **Tests Collected:** 179
- **Passed:** 178
- **Failed:** 1 (pre-existing stale test: `test_sprint44B_corrections.py::test_performance_missed_results_in_verification_failure`)
- **Errors:** 0
- **Runtime:** 620.15s (10 min 20s)
- **New Regressions:** 0

---

## 24. GIT SCOPE AUDIT

- `git status` confirms that **zero production files were modified** during Phase 6A.
- The 46 modified files in the working tree are strictly preserved from Phases 1–4.
- All Phase 6A test scripts were isolated to `scratch/`:
  - `scratch/audit_optimizers.py`
  - `scratch/audit_candidate_generators.py`
  - `scratch/test_priority_sensitivity.py`
  - `scratch/test_range_endurance_budget.py`
  - `scratch/extract_metrics.py`

---

## 25. KNOWN LIMITATIONS

1. Optimization priorities (`LOWEST_COST`, `LOWEST_WEIGHT`, `MAXIMUM_ENDURANCE`, etc.) currently have no effect on fixed-wing designs.
2. The user's financial budget input is metadata-only.
3. Battery sizing defaults to catalog maximum packs that meet endurance rather than minimizing battery mass for short-range missions.
4. Pareto multi-objective front extraction is not available for fixed-wing aircraft.

---

## 26. FINAL VERDICT

```
========================================================================================
                   PHASE 6A FORENSIC OPTIMIZATION ARCHITECTURE AUDIT
                               FINAL FORMAL VERDICT:
                             >>> PASS WITH WARNINGS <<<
========================================================================================
Summary:
- Forensic audit completed across all 9 subsystem optimizers and pipeline stages.
- Exact objective functions, constraints, candidate generators, and evaluators documented.
- Confirmed that OptimizationPriority, DesignMode, and Budget are currently decoupled.
- Normalization imbalances and text-parsing fragilities identified and cataloged.
- Zero code modifications made; protected Phase 1–5 baseline 100% intact.
- 178 tests passed, 0 errors, zero new regressions.
- Phase 6B improvement roadmap and priority rankings established.
========================================================================================
```
