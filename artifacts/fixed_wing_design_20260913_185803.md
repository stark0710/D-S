# Fixed-Wing Aircraft Design Report

**Execution Timestamp**: 2026-09-13 18:58:03  
**Design Status**: `INTERNAL_EXCEPTION` | **Overall Outcome**: **FAIL**  

---

## 1. Run Summary

| Metric | Value |
|:---|:---|
| **Pipeline Execution** | `FixedWingDesignPipeline.execute()` |
| **Success** | `False` |
| **Status** | `INTERNAL_EXCEPTION` |
| **Converged** | `False` |
| **Iterations** | `3` |
| **Reported MTOW** | `7.505 kg` |

## 2. User Requirements

| Requirement Field | Value |
|:---|:---|
| **Mission Type** | `DELIVERY` |
| **Payload Weight** | `3.000 kg` |
| **Target Flight Time** | `30.0 min` |
| **Target Range** | `30.0 km` |
| **Target Cruise Speed** | `80.0 km/h` |
| **Takeoff Type** | `RUNWAY` |
| **Landing Type** | `RUNWAY` |
| **Environment** | `RURAL` |
| **Optimization Priority** | `BALANCED` |
| **Design Mode** | `MANUAL` |
| **Max MTOW Limit** | `None` |
| **Budget Limit** | `None` |

## 3. Mission

- **Mission Category**: `Cargo`
- **Cruise Altitude**: `N/A m`
- **Design Cruise Speed**: `80.0 km/h`
- **Payload Capacity**: `3.000 kg`

## 4. Aircraft Configuration

- **Wing Configuration**: `High Wing`
- **Propulsion Layout**: `Twin Tractor`
- **Tail Configuration**: `Conventional`
- **Landing Gear Layout**: `Tricycle`

## 5. Geometry

### Wing Planform
- **Wingspan**: `2.110 m`
- **Wing Reference Area**: `0.556 m²`
- **Aspect Ratio**: `8.00`
- **Mean Aerodynamic Chord**: `0.284 m`
- **Root Airfoil**: `Selig S1223`
- **Tip Airfoil**: `Clark Y`

### Fuselage & Tail
- **Fuselage Length**: `1.300 m`
- **Fuselage Width**: `0.150 m`
- **Fuselage Height**: `0.100 m`
- **Horizontal Tail Area**: `0.099 m²` (Span: `0.544 m`)
- **Vertical Tail Area**: `0.035 m²` (Span: `0.000 m`)

## 6. Construction & Materials

- **Selected Architecture**: `Foam-Core Composite Shell (C1)`
- **Primary Spar Material**: `Carbon Fiber CFRP`
- **Skin / Covering**: `Balsa / Film / Foam`
- **Structural Complexity Score**: `1.00`

## 7. Weight & Mass Properties

| Component / Discipline | Mass (kg) | Mass Fraction (%) |
|:---|:---:|:---:|
| **Structural Weight** | `2.287` | `30.5%` |
| **Propulsion System** | `0.455` | `6.1%` |
| **Avionics & Wiring** | `0.442` | `5.9%` |
| **Battery Pack** | `0.821` | `10.9%` |
| **Payload Mass** | `3.500` | `46.6%` |
| **TOTAL MTOW** | **`7.505`** | **100.0%** |

> **Mass Conservation Verification**: Subsystem mass conservation strictly verified within 0.0000%.

## 8. CG & Stability

- **Center of Gravity (X, Y, Z)**: `(0.565 m, 0.000 m, -0.033 m)`
- **Longitudinal Static Margin**: `14.6%` (Design Target: 10.0% – 18.0% MAC)
- **Static Stability Status**: `STABLE`

## 9. Propulsion

- **Selected Motor**: `T-Motor AT3520`
- **Selected Propeller**: `11x7 APC`
- **Static Thrust Available**: `N/A` N
- **Thrust-to-Weight Ratio (T/W)**: `N/A`

## 10. Electrical & Battery

- **Battery Pack Mass**: `0.821 kg`
- **Estimated Energy Capacity**: `~164.2 Wh` (@ 200 Wh/kg specific energy)
- **Cruise Power Consumption**: Included in battery reserve sizing

## 11. Performance

- **Clean Stall Speed**: `36.6 km/h`
- **Cruise Speed**: `80.0 km/h` (Safety Margin: `2.19x`)
- **Aerodynamic Efficiency (L/D)**: `12.8`
- **Calculated Endurance**: `30.6 min` (Target: `30.0 min`)
- **Calculated Range**: `40.8 km` (Target: `30.0 km`)

## 12. Convergence

- **Convergence Reached**: `False`
- **Total Sizing Iterations**: `3`

| Iteration | Old MTOW (kg) | New MTOW (kg) | Delta (kg) | Rel Error (%) |
|:---:|:---:|:---:|:---:|:---:|
| 1 | 7.5050 | 7.4470 | 0.0580 | 0.77% |
| 2 | 7.4470 | 7.4940 | 0.0470 | 0.63% |
| 3 | 7.4940 | 7.5050 | 0.0110 | 0.15% |

## 13. Verification

*Verification report unavailable.*

## 14. Warnings

No engineering warnings reported.

## 15. Errors

- ❌ Design compliance score (88.0%) is below the minimum required safety compliance boundary (90.0%).

## 16. Final Engineering Verdict

### **VERDICT: PIPELINE EXECUTION FAILED**

Execution halted at status `INTERNAL_EXCEPTION`. Inspect Section 15 for specific root causes.
