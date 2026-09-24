# Fixed-Wing Aircraft Design Report

**Execution Timestamp**: 2026-09-13 19:09:59  
**Design Status**: `SIZING_INFEASIBLE` | **Overall Outcome**: **FAIL**  

---

## 1. Run Summary

| Metric | Value |
|:---|:---|
| **Pipeline Execution** | `FixedWingDesignPipeline.execute()` |
| **Success** | `False` |
| **Status** | `SIZING_INFEASIBLE` |
| **Converged** | `False` |
| **Iterations** | `0` |
| **Reported MTOW** | `0.000 kg` |

## 2. User Requirements

| Requirement Field | Value |
|:---|:---|
| **Mission Type** | `SECURITY` |
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

- **Mission Category**: `Surveillance`
- **Cruise Altitude**: `N/A m`
- **Design Cruise Speed**: `80.0 km/h`
- **Payload Capacity**: `0.500 kg`

## 4. Aircraft Configuration

- **Wing Configuration**: `High Wing`
- **Propulsion Layout**: `Tractor`
- **Tail Configuration**: `Conventional`
- **Landing Gear Layout**: `Tricycle`

## 5. Geometry

### Wing Planform
- **Wingspan**: `1.335 m`
- **Wing Reference Area**: `0.111 m²`
- **Aspect Ratio**: `16.00`
- **Mean Aerodynamic Chord**: `0.071 m`
- **Root Airfoil**: `Clark Y`
- **Tip Airfoil**: `MH 32`

### Fuselage & Tail
- **Horizontal Tail Area**: `0.004 m²` (Span: `0.156 m`)
- **Vertical Tail Area**: `0.006 m²` (Span: `0.000 m`)

## 6. Construction & Materials

- **Selected Architecture**: `Foam-Core Composite Shell (C1)`
- **Primary Spar Material**: `Carbon Fiber CFRP`
- **Skin / Covering**: `Balsa / Film / Foam`
- **Structural Complexity Score**: `1.00`

## 7. Weight & Mass Properties

| Component / Discipline | Mass (kg) | Mass Fraction (%) |
|:---|:---:|:---:|
| **Structural Weight** | `0.000` | `0.0%` |
| **Propulsion System** | `0.000` | `0.0%` |
| **Avionics & Wiring** | `0.000` | `0.0%` |
| **Battery Pack** | `0.000` | `0.0%` |
| **Payload Mass** | `0.000` | `0.0%` |
| **TOTAL MTOW** | **`0.000`** | **100.0%** |

> **Mass Conservation Verification**: No MassPropertiesResult available.

## 8. CG & Stability

*CG and stability data unavailable.*

## 9. Propulsion

*Propulsion data unavailable.*

## 10. Electrical & Battery

*Electrical subsystem data unavailable.*

## 11. Performance

*Performance data unavailable.*

## 12. Convergence

- **Convergence Reached**: `False`
- **Total Sizing Iterations**: `0`

## 13. Verification

*Verification report unavailable.*

## 14. Warnings

No engineering warnings reported.

## 15. Errors

- ❌ Sized fuselage width (0.12 m) exceeds wing root chord (0.11 m), which causes extreme aerodynamic blockage and drag. Select a more slender fuselage profile.

## 16. Final Engineering Verdict

### **VERDICT: PIPELINE EXECUTION FAILED**

Execution halted at status `SIZING_INFEASIBLE`. Inspect Section 15 for specific root causes.
