# Fixed-Wing Aircraft Design Report

**Execution Timestamp**: 2026-09-13 19:20:49  
**Design Status**: `COMPONENT_DATABASE_LIMITATION` | **Overall Outcome**: **FAIL**  

---

## 1. Run Summary

| Metric | Value |
|:---|:---|
| **Pipeline Execution** | `FixedWingDesignPipeline.execute()` |
| **Success** | `False` |
| **Status** | `COMPONENT_DATABASE_LIMITATION` |
| **Converged** | `False` |
| **Iterations** | `0` |
| **Reported MTOW** | `0.000 kg` |

## 2. User Requirements

| Requirement Field | Value |
|:---|:---|
| **Mission Type** | `TRAINING` |
| **Payload Weight** | `0.200 kg` |
| **Target Flight Time** | `15.0 min` |
| **Target Range** | `15.0 km` |
| **Target Cruise Speed** | `60.0 km/h` |
| **Takeoff Type** | `HAND_LAUNCH` |
| **Landing Type** | `BELLY_LANDING` |
| **Environment** | `RURAL` |
| **Optimization Priority** | `LOWEST_WEIGHT` |
| **Design Mode** | `ENGINEERING_ADVISOR` |
| **Max MTOW Limit** | `None` |
| **Budget Limit** | `None` |

## 3. Mission

- **Mission Category**: `Survey`
- **Cruise Altitude**: `N/A m`
- **Design Cruise Speed**: `60.0 km/h`
- **Payload Capacity**: `0.200 kg`

## 4. Aircraft Configuration

- **Wing Configuration**: `High Wing`
- **Propulsion Layout**: `Pusher`
- **Tail Configuration**: `Conventional`
- **Landing Gear Layout**: `Belly Landing`

## 5. Geometry

### Wing Planform
- **Wingspan**: `1.081 m`
- **Wing Reference Area**: `0.111 m²`
- **Aspect Ratio**: `10.50`
- **Mean Aerodynamic Chord**: `0.107 m`
- **Root Airfoil**: `Clark Y`
- **Tip Airfoil**: `NACA 0012`

### Fuselage & Tail
- **Fuselage Length**: `0.811 m`
- **Fuselage Width**: `0.122 m`
- **Fuselage Height**: `0.149 m`
- **Horizontal Tail Area**: `0.009 m²` (Span: `0.203 m`)
- **Vertical Tail Area**: `0.007 m²` (Span: `0.000 m`)

## 6. Construction & Materials

- **Selected Architecture**: `Balsa Skeleton Composite D-Box (C2)`
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

- ❌ COMPONENT_DATABASE_LIMITATION: Lightest available component of type 'RGB Camera' in database weighs 0.51 kg, which exceeds the maximum allowed structural payload limit of 0.21 kg.

## 16. Final Engineering Verdict

### **VERDICT: PIPELINE EXECUTION FAILED**

Execution halted at status `COMPONENT_DATABASE_LIMITATION`. Inspect Section 15 for specific root causes.
