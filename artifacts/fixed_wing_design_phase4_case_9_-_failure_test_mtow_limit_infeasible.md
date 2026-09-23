# Fixed-Wing Aircraft Design Report

**Execution Timestamp**: 2026-09-14 21:07:14  
**Design Status**: `INVALID_REQUIREMENTS` | **Overall Outcome**: **FAIL**  

---

## 1. Run Summary

| Metric | Value |
|:---|:---|
| **Pipeline Execution** | `FixedWingDesignPipeline.execute()` |
| **Success** | `False` |
| **Status** | `INVALID_REQUIREMENTS` |
| **Converged** | `False` |
| **Iterations** | `0` |
| **Reported MTOW** | `0.000 kg` |
| **Subsystem Verification** | `N/A` |
| **Common Certification** | `N/A` |

## 2. User Requirements

| Requirement Field | Value |
|:---|:---|
| **Mission Type** | `AGRICULTURE` |
| **Payload Weight** | `2.000 kg` |
| **Target Flight Time** | `60.0 min` |
| **Target Range** | `40.0 km` |
| **Target Cruise Speed** | `65.0 km/h` |
| **Takeoff Type** | `RUNWAY` |
| **Landing Type** | `RUNWAY` |
| **Environment** | `RURAL` |
| **Optimization Priority** | `BALANCED` |
| **Design Mode** | `ENGINEERING_ADVISOR` |
| **Max MTOW Limit** | `1.0` |
| **Budget Limit** | `None` |

## 3. Mission

*Mission analysis data unavailable.*

## 4. Aircraft Configuration

*Configuration data unavailable.*

## 5. Geometry

### Wing Planform

### Fuselage & Tail

## 6. Construction & Materials

*Construction engine data unavailable.*

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
- **Convergence Message**: `Convergence not achieved.`

### Monitored Physical Convergence Variables & Tolerances

| Monitored Physical Variable | Convergence Tolerance | Final Value | Disciplinary Status |
|:---|:---:|:---:|:---:|
| **Takeoff Mass (MTOW)** | `± 0.050 kg` | `0.000 kg` | `PENDING` |
| **Wing Reference Area** | `± 0.005 m²` | `0.000 m²` | `PENDING` |
| **Wing Loading (W/S)** | `± 0.200 kg/m²` | `0.00 kg/m²` | `PENDING` |
| **Battery Pack Mass** | `± 0.020 kg` | `0.000 kg` | `PENDING` |
| **Structural Empty Mass** | `± 0.050 kg` | `0.000 kg` | `PENDING` |
| **CG Longitudinal (X)** | `± 0.005 m` | `0.000 m` | `PENDING` |
| **Static Margin** | `± 0.5% MAC` | `0.0%` | `PENDING` |
| **Cruise Electrical Power** | `± 2.0 W` | `0.0 W` | `PENDING` |
| **Flight Endurance** | `± 0.5 min` | `0.0 min` | `PENDING` |
| **Mission Range** | `± 0.2 km` | `0.0 km` | `PENDING` |

## 13. Verification & Certification Status

- **Subsystem Engineering Verification**: `N/A`
- **Regulatory Airworthiness Certification**: `N/A`
- **Overall Pipeline Stage Gate**: `FAILED`

## 14. Warnings

No engineering warnings reported.

## 15. Errors

- ❌ Maximum takeoff weight limit (1.0 kg) must be greater than payload weight (2.0 kg)

## 16. Final Engineering Verdict

### **VERDICT: PIPELINE EXECUTION FAILED**

Execution halted at status `INVALID_REQUIREMENTS`. Inspect Section 15 for specific engineering root causes and constraints.
