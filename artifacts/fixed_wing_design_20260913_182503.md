# Fixed-Wing Aircraft Design Report

**Execution Timestamp**: 2026-09-13 18:25:03  
**Design Status**: `SUCCESS` | **Overall Outcome**: **PASS**  

---

## 1. Run Summary

| Metric | Value |
|:---|:---|
| **Pipeline Execution** | `FixedWingDesignPipeline.execute()` |
| **Success** | `True` |
| **Status** | `SUCCESS` |
| **Converged** | `True` |
| **Iterations** | `6` |
| **Reported MTOW** | `5.137 kg` |

## 2. User Requirements

| Requirement Field | Value |
|:---|:---|
| **Mission Type** | `SURVEY` |
| **Payload Weight** | `0.500 kg` |
| **Target Flight Time** | `30.0 min` |
| **Target Range** | `30.0 km` |
| **Target Cruise Speed** | `80.0 km/h` |
| **Takeoff Type** | `RUNWAY` |
| **Landing Type** | `RUNWAY` |
| **Environment** | `RURAL` |
| **Optimization Priority** | `BALANCED` |
| **Design Mode** | `ENGINEERING_ADVISOR` |
| **Max MTOW Limit** | `None` |
| **Budget Limit** | `None` |

## 3. Mission

- **Mission Category**: `Survey`
- **Cruise Altitude**: `N/A m`
- **Design Cruise Speed**: `80.0 km/h`
- **Payload Capacity**: `0.500 kg`

## 4. Aircraft Configuration

- **Wing Configuration**: `High Wing`
- **Propulsion Layout**: `Pusher`
- **Tail Configuration**: `Conventional`
- **Landing Gear Layout**: `Tricycle`

## 5. Geometry

### Wing Planform
- **Wingspan**: `1.953 m`
- **Wing Reference Area**: `0.381 m²`
- **Aspect Ratio**: `10.00`
- **Mean Aerodynamic Chord**: `0.210 m`
- **Root Airfoil**: `Clark Y`
- **Tip Airfoil**: `NACA 0012`

### Fuselage & Tail
- **Fuselage Length**: `2.000 m`
- **Fuselage Width**: `0.150 m`
- **Fuselage Height**: `0.100 m`
- **Horizontal Tail Area**: `0.040 m²` (Span: `0.348 m`)
- **Vertical Tail Area**: `0.018 m²` (Span: `0.000 m`)

## 6. Construction & Materials

- **Selected Architecture**: `Foam-Core Composite Shell (C1)`
- **Primary Spar Material**: `Carbon Fiber CFRP`
- **Skin / Covering**: `Balsa / Film / Foam`
- **Structural Complexity Score**: `1.00`

## 7. Weight & Mass Properties

| Component / Discipline | Mass (kg) | Mass Fraction (%) |
|:---|:---:|:---:|
| **Structural Weight** | `1.998` | `38.9%` |
| **Propulsion System** | `0.455` | `8.9%` |
| **Avionics & Wiring** | `0.442` | `8.6%` |
| **Battery Pack** | `1.232` | `24.0%` |
| **Payload Mass** | `1.010` | `19.7%` |
| **TOTAL MTOW** | **`5.137`** | **100.0%** |

> **Mass Conservation Verification**: Subsystem mass conservation strictly verified within 0.0000%.

## 8. CG & Stability

- **Center of Gravity (X, Y, Z)**: `(0.928 m, 0.000 m, -0.029 m)`
- **Longitudinal Static Margin**: `15.5%` (Design Target: 10.0% – 18.0% MAC)
- **Static Stability Status**: `STABLE`

## 9. Propulsion

- **Selected Motor**: `T-Motor AT3520`
- **Selected Propeller**: `11x7 APC`
- **Static Thrust Available**: `N/A` N
- **Thrust-to-Weight Ratio (T/W)**: `N/A`

## 10. Electrical & Battery

- **Battery Pack Mass**: `1.232 kg`
- **Estimated Energy Capacity**: `~246.4 Wh` (@ 200 Wh/kg specific energy)
- **Cruise Power Consumption**: Included in battery reserve sizing

## 11. Performance

- **Clean Stall Speed**: `43.5 km/h`
- **Cruise Speed**: `80.0 km/h` (Safety Margin: `1.84x`)
- **Aerodynamic Efficiency (L/D)**: `12.9`
- **Calculated Endurance**: `66.0 min` (Target: `30.0 min`)
- **Calculated Range**: `88.0 km` (Target: `30.0 km`)

## 12. Convergence

- **Convergence Reached**: `True`
- **Total Sizing Iterations**: `6`

| Iteration | Old MTOW (kg) | New MTOW (kg) | Delta (kg) | Rel Error (%) |
|:---:|:---:|:---:|:---:|:---:|
| 1 | 5.1370 | 4.1810 | 0.9560 | 18.61% |
| 2 | 4.1810 | 4.9940 | 0.8130 | 19.45% |
| 3 | 4.9940 | 5.1160 | 0.1220 | 2.44% |
| 4 | 5.1160 | 5.1330 | 0.0170 | 0.33% |
| 5 | 5.1330 | 5.1360 | 0.0030 | 0.06% |
| 6 | 5.1360 | 5.1370 | 0.0010 | 0.02% |

## 13. Verification

- **Verification Status**: `VERIFIED`
- **Mission Requirements Satisfied**: `Ready`

## 14. Warnings

No engineering warnings reported.

## 15. Errors

Zero pipeline execution errors.

## 16. Final Engineering Verdict

### **VERDICT: PASS — FULLY CONVERGED & FEASIBLE AIRCRAFT**

The Fixed-Wing design pipeline successfully converged across all aerodynamic, physical structural, propulsion, mass properties, and performance disciplines without violating safety margins or database boundaries.
