# VTOL Sizing Synthesis & Engineering Report
## Sprint 44 — End-to-End Design Pipeline

This report summarizes the sizing results for the VTOL hybrid platform.

### Sizing Executive Summary
*   **Total Takeoff Weight (MTOW)**: 8.070 kg
*   **Empty Weight**: 4.914 kg
*   **Payload Capacity**: 3.25 kg
*   **Estimated Endurance**: 222.8 min
*   **Estimated Range**: 371.41 km

### Subsystem Sizing Details
*   **Wing Span**: 1.87 m (AR: 13.0)
*   **Selected Airfoil**: Clark Y
*   **Tail Configuration**: Inverted V-tail on twin booms (Arm: 0.36m)
*   **Fuselage volume**: 0.073 m3
*   **Lift Motors**: T-Motor MN6007
*   **Forward Motors**: T-Motor MN5008
*   **Battery Pack**: LiHV (6S 6P, 684.0 Wh)

### Mass Properties & CG Sizing
*   **Converged MTOW**: 8.070 kg
*   **Empty Weight**: 4.914 kg
*   **Center of Gravity (x_cg)**: 0.5219 m (30.5% MAC, datum: FUSELAGE_NOSE)
*   **Convergence Status**: CONVERGED (17 iterations, residual 0.0118 kg <= 0.0150 kg)

### Transition Engineering
*   **Transition Direction**: TRANSITION_TO_CRUISE
*   **Conversion Speed**: 80.4 km/h
*   **Transition Duration**: 18.0 s
*   **Corridor Checkpoints**: 5

### Stability & Control Sizing (Phase 6)
*   **Tail Architecture**: Inverted V-tail on twin booms (dihedral: 45.3 deg)
*   **Wing Aerodynamic Center (x_AC)**: 0.4968 m (25.0% MAC)
*   **Neutral Point (x_NP)**: 0.5324 m (49.2% MAC)
*   **Static Margin**: 7.14% MAC (0.0105 m)
*   **Static Stability Margin Status**: STABLE
*   **Quasi-Steady Trim Status**: TRIM_FEASIBLE
*   **Longitudinal CG Envelope**: [0.4747 m .. 0.5250 m]
