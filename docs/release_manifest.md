# Release Manifest — Torq Wings Design Studio V3
## Production Release Tag: v3.0.0-fixedwing

This document lists all locked files, public interfaces, databases, and configurations frozen for the official production release of the Fixed-Wing Design Studio.

---

## 1. Frozen Code Components & API Implementations

All modules within the Fixed-Wing pipeline are frozen. Modifying these files requires a minor version increment and regression validation.

| Component / Layer | Module Path | Primary Interface | Frozen Status |
| :--- | :--- | :--- | :---: |
| **Pipeline Entry** | `backend/design/fixed_wing/pipeline/fixed_wing_pipeline.py` | `FixedWingDesignPipeline` | **LOCKED** |
| **Vehicle Selection** | `backend/design/advisor/recommendation/` | `VehicleRecommendationEngine` | **LOCKED** |
| **Wing Design** | `backend/design/fixed_wing/wing/wing_engine.py` | `WingEngine` | **LOCKED** |
| **Airfoil Sizing** | `backend/design/fixed_wing/airfoil/airfoil_engine.py` | `AirfoilEngine` | **LOCKED** |
| **Fuselage Sizing** | `backend/design/fixed_wing/fuselage/fuselage_engine.py` | `FuselageEngine` | **LOCKED** |
| **Payload Integration** | `backend/design/fixed_wing/payload/payload_engine.py` | `PayloadEngine` | **LOCKED** |
| **Tail Design** | `backend/design/fixed_wing/tail/tail_engine.py` | `TailEngine` | **LOCKED** |
| **Propulsion Sizing** | `backend/design/fixed_wing/propulsion/propulsion_engine.py` | `PropulsionEngine` | **LOCKED** |
| **Electrical Sizing** | `backend/design/fixed_wing/electrical/electrical_optimizer.py` | `ElectricalOptimizer` | **LOCKED** |
| **Mass Properties** | `backend/design/fixed_wing/mass_properties/mass_properties_engine.py` | `MassPropertiesEngine` | **LOCKED** |
| **CG & Balances** | `backend/design/fixed_wing/pipeline/pipeline_stage.py` | `CGOptimizerStage` | **LOCKED** |
| **Performance Sizing** | `backend/design/fixed_wing/flight_performance/flight_performance_engine.py` | `FlightPerformanceEngine` | **LOCKED** |
| **Convergence Manager** | `backend/design/fixed_wing/convergence/convergence_manager.py` | `ConvergenceManager` | **LOCKED** |
| **Verification & Safety** | `backend/design/fixed_wing/verification/verification_engine.py` | `VerificationEngine` | **LOCKED** |

---

## 2. Frozen Component Databases

Component databases are compiled within the source code modules and frozen.

| Catalog Database | Location in Source Code | Key Records Listed | Status |
| :--- | :--- | :--- | :---: |
| **Brushless Motors** | `backend/design/fixed_wing/propulsion/motor_selector.py` | SunnySky, T-Motor, KDE series DC Motors | **FROZEN** |
| **Propellers** | `backend/design/fixed_wing/propulsion/propeller_selector.py` | APC, Wood Gas, standard carbon propeller lines | **FROZEN** |
| **Flight Controllers** | `backend/design/fixed_wing/electrical/candidate_generator.py` | Pixhawk series, Cube Orange+, Matek H743-WING | **FROZEN** |
| **GPS Modules** | `backend/design/fixed_wing/electrical/candidate_generator.py` | Holybro GNSS, CubePilot Here3/Here4 RTK | **FROZEN** |
| **Telemetry Radios** | `backend/design/fixed_wing/electrical/candidate_generator.py` | Holybro SiK, RFD900ux, Silvus StreamCaster | **FROZEN** |
| **RC Receivers** | `backend/design/fixed_wing/electrical/candidate_generator.py` | FrSky Archer, ExpressLRS, TBS Crossfire | **FROZEN** |
| **Servos** | `backend/design/fixed_wing/electrical/candidate_generator.py` | KST Micro, Wing, and High-Torque servos | **FROZEN** |
| **BEC / Regulators** | `backend/design/fixed_wing/electrical/candidate_generator.py` | Castle Creations BEC, Castle BEC Pro | **FROZEN** |
| **Power Distribution** | `backend/design/fixed_wing/electrical/candidate_generator.py` | Holybro PM02/PM06, Maucher 200A Modules | **FROZEN** |
| **Mission Payloads** | `backend/design/fixed_wing/electrical/candidate_generator.py` | RGB cameras, Multispectral sensors, Lidars | **FROZEN** |

---

## 3. Frozen Verification & Sizing Parameters

All engineering constraints, optimization settings, and safety verification boundaries are locked.

- **Atmospheric Constants**: Gravity ($g = 9.80665$ m/s²), Sea-level air density ($\rho_0 = 1.225$ kg/m³).
- **Physical Limits**:
  - Maximum Takeoff Weight (MTOW) ceiling: 65 kg (Heavy UAV category).
  - Wing loading boundaries: [1.0, 100.0] kg/m².
  - Certified static margin envelope: [5.0%, 25.0%].
  - Empty weight structural limit: 65% of MTOW.
- **Verification Strategy Bounds**:
  - Minimum Sizing Compliance Score: 85.0% for certified flight readiness.
  - Maximum Acceptable Risk Rating: Medium (Risk index <= 35.0).
  - Maximum Allowed Active Violations: 3 rules.
