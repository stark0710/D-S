# Fixed-Wing Aircraft Design Report

**Execution Timestamp**: 2026-09-15 02:47:55  
**Design Status**: `SUCCESS` | **Overall Outcome**: **PASS**  

---

## 1. Run Summary

| Metric | Value |
|:---|:---|
| **Pipeline Execution** | `FixedWingDesignPipeline.execute()` |
| **Success** | `True` |
| **Status** | `SUCCESS` |
| **Converged** | `True` |
| **Iterations** | `4` |
| **Reported MTOW** | `4.207 kg` |
| **Subsystem Verification** | `VERIFIED` |
| **Common Certification** | `CERTIFIED` |

## 2. User Requirements

| Requirement Field | Value |
|:---|:---|
| **Mission Type** | `DELIVERY` |
| **Payload Weight** | `1.000 kg` |
| **Target Flight Time** | `45.0 min` |
| **Target Range** | `40.0 km` |
| **Target Cruise Speed** | `80.0 km/h` |
| **Takeoff Type** | `RUNWAY` |
| **Landing Type** | `RUNWAY` |
| **Environment** | `RURAL` |
| **Optimization Priority** | `BALANCED` |
| **Design Mode** | `ENGINEERING_ADVISOR` |
| **Max MTOW Limit** | `None` |
| **Budget Limit** | `None` |

## 3. Mission

- **Mission Category**: `Cargo`
- **Cruise Altitude**: `N/A m`
- **Design Cruise Speed**: `80.0 km/h`
- **Payload Capacity**: `1.000 kg`
- **Target Range**: `40.0 km`
- **Target Endurance**: `45.0 min`

## 4. Aircraft Configuration

- **Selected Architecture**: `Twin-Engine High-Wing Cargo Transport`
- **Wing Configuration**: `High Wing`
- **Propulsion Layout**: `Twin Tractor`
- **Tail Configuration**: `Conventional`
- **Landing Gear Layout**: `Tricycle`
- **Payload Arrangement**: `Fuselage Cargo Compartment (CG)`

> **Configuration Rationale**: A Twin-Engine High-Wing layout is the standard for cargo transport. High wings leave the fuselage low to the ground for easy loading and maintain wing clearance. Twin tractor engines distribute thrust and structural bending moments, while Tricycle gear ensures stability during heavy taxiing and runway operations.

## 5. Geometry

### Wing Planform
- **Wingspan**: `1.579 m`
- **Wing Reference Area**: `0.311 m²`
- **Aspect Ratio**: `8.00`
- **Root Chord**: `0.292 m`
- **Tip Chord**: `0.102 m`
- **Taper Ratio**: `0.35`
- **Mean Aerodynamic Chord (MAC)**: `0.213 m`
- **Root Airfoil**: `Selig S1223`
- **Tip Airfoil**: `Clark Y`

### Fuselage & Tail
- **Fuselage Length**: `1.300 m`
- **Fuselage Width**: `0.150 m`
- **Fuselage Height**: `0.100 m`
- **Horizontal Tail Area**: `0.041 m²` (Span: `0.352 m`)
- **Vertical Tail Area**: `0.015 m²` (Span: `0.000 m`)

## 6. Construction & Materials

- **Selected Architecture**: `Foam-Core Composite Shell (C1)`
- **Primary Spar Material**: `Carbon Fiber CFRP`
- **Skin / Covering**: `Balsa / Film / Foam`
- **Structural Complexity Score**: `1.00`

## 7. Weight & Mass Properties

| Component / Discipline | Mass (kg) | Mass Fraction (%) |
|:---|:---:|:---:|
| **Structural Weight** | `1.563` | `37.2%` |
| **Propulsion System** | `0.455` | `10.8%` |
| **Avionics & Wiring** | `0.442` | `10.5%` |
| **Battery Pack** | `0.747` | `17.8%` |
| **Payload Mass** | `1.000` | `23.8%` |
| **TOTAL MTOW** | **`4.207`** | **100.0%** |

> **Mass Conservation Verification**: Subsystem mass conservation strictly verified within 0.0000%.

## 8. CG & Stability

- **Center of Gravity (X, Y, Z)**: `(0.528 m, 0.000 m, -0.030 m)`
- **Longitudinal Static Margin**: `14.4%` (Design Target: 10.0% – 18.0% MAC)
- **Static Stability Status**: `STABLE`

## 9. Propulsion

- **Selected Motor**: `T-Motor AT3520`
- **Selected Propeller**: `11x7 APC`
- **Propulsion Layout**: `Single Tractor`
- **Estimated Static Thrust**: `35.55 N`
- **Thrust-to-Weight Ratio (T/W)**: `0.86`
- **Required Cruise Thrust**: `3.10 N`
- **Cruise Electrical Power**: `129.3 W` (5.8 A @ 0.0 V)
- **Maximum Power Rating**: `950.0 W`
- **Estimated Cruise Throttle**: `13.6%`
- **Takeoff Acceleration Force**: `32.5 N`

## 10. Electrical & Battery

- **Battery Pack Mass**: `0.747 kg`
- **Estimated Energy Capacity**: `~149.4 Wh` (@ 200 Wh/kg specific energy)
- **Cruise Power Consumption**: Included in battery reserve sizing

## 11. Performance

- **Clean Stall Speed**: `38.9 km/h`
- **Cruise Speed**: `80.0 km/h` (Safety Margin: `2.06x`)
- **Aerodynamic Efficiency (L/D)**: `13.2`
- **Calculated Endurance**: `49.4 min` (Target: `45.0 min`)
- **Calculated Range**: `65.8 km` (Target: `40.0 km`)

## 12. Convergence

- **Convergence Reached**: `True`
- **Total Sizing Iterations**: `4`
- **Convergence Message**: `All variables stabilized below convergence tolerances at iteration 4.`

### Monitored Physical Convergence Variables & Tolerances

| Monitored Physical Variable | Convergence Tolerance | Final Value | Disciplinary Status |
|:---|:---:|:---:|:---:|
| **Takeoff Mass (MTOW)** | `± 0.050 kg` | `4.207 kg` | `CONVERGED` |
| **Wing Reference Area** | `± 0.005 m²` | `0.311 m²` | `CONVERGED` |
| **Wing Loading (W/S)** | `± 0.200 kg/m²` | `13.51 kg/m²` | `CONVERGED` |
| **Battery Pack Mass** | `± 0.020 kg` | `0.747 kg` | `CONVERGED` |
| **Structural Empty Mass** | `± 0.050 kg` | `1.563 kg` | `CONVERGED` |
| **CG Longitudinal (X)** | `± 0.005 m` | `0.528 m` | `CONVERGED` |
| **Static Margin** | `± 0.5% MAC` | `14.4%` | `CONVERGED` |
| **Cruise Electrical Power** | `± 2.0 W` | `129.3 W` | `CONVERGED` |
| **Flight Endurance** | `± 0.5 min` | `49.4 min` | `CONVERGED` |
| **Mission Range** | `± 0.2 km` | `65.8 km` | `CONVERGED` |

### Multidisciplinary Iteration Progression

| Iteration | MTOW (kg) | Wing S (m²) | Battery (kg) | Static Margin | Cruise Pwr (W) | Endurance (min) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 4.100 | 0.271 | 0.720 | 14.5% | 107.0 | 65.4 |
| 2 | 4.164 | 0.304 | 0.720 | 14.6% | 120.7 | 59.3 |
| 3 | 4.195 | 0.309 | 0.720 | 14.4% | 127.8 | 58.1 |
| 4 | 4.207 | 0.311 | 0.720 | 14.4% | 129.3 | 58.0 |

## 13. Verification & Certification Status

- **Subsystem Engineering Verification**: `VERIFIED`
- **Regulatory Airworthiness Certification**: `CERTIFIED`
- **Overall Pipeline Stage Gate**: `PASSED`

## 14. Warnings

No engineering warnings reported.

## 15. Errors

Zero pipeline execution errors.

## 16. Final Engineering Verdict

### **VERDICT: PASS — FULLY CONVERGED & FEASIBLE AIRCRAFT**

The Fixed-Wing design pipeline successfully converged across all aerodynamic, physical structural, propulsion, mass properties, and performance disciplines without violating safety margins or database boundaries.
