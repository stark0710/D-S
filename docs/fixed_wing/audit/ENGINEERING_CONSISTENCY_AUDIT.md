# Engineering Consistency Audit — Fixed-Wing Design Studio

This document captures the reverse-engineered engineering inconsistencies, calculation duplicates, and physical mismatches identified in the Fixed-Wing Design Studio codebase.

## Mismatch Registry

| Parameter | Source A / Value | Source B / Value | Source A Module | Source B Module | Possible Cause | Recommendation |
|---|---|---|---|---|---|---|
| **Sized Payload Weight** | `0.510` kg (Selected Sensor) | `1.010` kg (Calculated Payload) | `PayloadSelector` | `MassPropertiesStage` / `mission_payload_rule.py` | Payload gimbal and packaging overhead of `0.500` kg is added to the sensor weight, but compliance rules compare total payload weight against raw sensor requirement. | Update `mission_payload_rule.py` to compare only the sensor payload weight (`0.510` kg) against the requirement, or require the input requirement to specify "sensor payload" vs "useful payload". |
| **Lift-to-Drag Ratio (L/D)** | `requirements.wing_result.analysis.aerodynamic_efficiency_score * 0.18` (Estimated L/D, typical: `12.6`) | `requirements.flight_performance_result.aerodynamic_analysis.lift_to_drag_ratio` (Calculated L/D, typical: `15.75`) | `PropulsionEngine` (Initial) | `FlightPerformanceEngine` | Estimated L/D is used as a fallback. However, inside the convergence loop, `flight_performance_result` was not updated in step with `performance_result`. | Ensure `flight_performance_result` is kept synchronized with `performance_result` at the end of each iteration step (Resolved in Sprint 44B-1). |
| **Battery Sizing Category** | Fuel Weight / Useful Load | Empty Weight | `MassPropertiesStage` | Classical Aeronautical Sizing | Sizing rules treat electric batteries as "fuel weight" (fuel mass fraction) and group it under "Useful Load" (`2.242` kg useful load vs `1.01` kg payload). | Clearly document that for electric aircraft, the battery weight is treated as a component of "useful load" in the mass fractions. |
| **Propeller Clearance Constraints** | `max_prop_diameter_m = max(0.28, height_m * 2.0)` | `11.0` inches (`0.2794` m) | `PropulsionConstraints` | `PropellerSelector` database constraints | Sizing sets a physical clearance constraint based on fuselage height, forcing prop diameter to $\le 11$ inches, which restricts motor options to the 6S catalog. | Implement a dynamic warning when fuselage sizing forces propulsion into a sub-optimal efficiency regime. |

## Suspicious & Conflicting Calculations

1. **Stall Speed Discrepancy**:
   - In `WingSizer.size_wing()`, the wing loading is sized based on an estimated stall speed of `46.7` km/h.
   - However, in `FlightPerformanceEngine.process_performance_design()`, the actual clean stall speed is calculated as `62.0` km/h.
   - This occurs because structural weight buildup increases the final MTOW from the initial estimate, shifting the stall speed higher. This is the primary driver of the iteration/convergence loop.

2. **Electrical Current Budget**:
   - The current budget verification `V_ELEC_CURRENT_BUDGET` checks that `current_draw_cruise_a` is within ESC/battery ratings.
   - However, in several iterations, `current_draw_cruise_a` is read as `0.0` A when the flight performance stage falls back to the `0.0` default candidate on validation failure.
   - This causes the verification to print a false-positive pass: "Electrical currents (0.0 A) are within component ratings (ESC: 0.0 A, Battery: 0.0 A)" even though the sizing itself is invalid.

3. **Neutral Point and Stability Assumptions**:
   - The neutral point $X_{np}$ is estimated as a fixed percentage fraction based on the tail configuration:
     - `0.42` for Conventional
     - `0.25` for Tailless
     - `0.38` for others
   - This is a coarse aerodynamic approximation that does not account for the actual wing sweep, tail airfoil lift slope, or downwash effects, leading to conservative static margins (`0.157` vs target range `[0.05, 0.25]`).
