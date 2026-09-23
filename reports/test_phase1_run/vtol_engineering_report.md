# VTOL Sizing Synthesis & Engineering Architecture Report

*Generated on: 2026-09-21 21:36:35*

## 1. Executive Summary

- **Overall Status**: `SUCCESS`
- **Converged**: `True`
- **Iterations**: `1`

## 2. Aircraft Specifications

- **MTOW**: `7.500 kg`
- **Empty Weight**: `4.763 kg`
- **Payload Weight**: `2.00 kg`
- **Estimated Endurance**: `244.4 min`
- **Estimated Range**: `407.37 km`

## 3. Configuration & Propulsion Architecture

- **Architecture Type**: `Twin Boom VTOL`
- **Lift Motors**: `4`
- **Lift Rotors**: `4`
- **Cruise Motors**: `1`
- **Propulsion Arrangement**: `4_lift_plus_1_forward`
- **Wing Configuration**: `High-wing cantilever with twin boom mounts`
- **Tail Configuration**: `Inverted V-tail on twin booms`

## 4. Phase 1 Architecture Stage Inventory

| Subsystem / Stage | Architectural Status | Scope Classification |
|:---|:---:|:---|
| `requirements` | `IMPLEMENTED` | Phase 1 Core |
| `mission` | `IMPLEMENTED` | Phase 1 Core |
| `configuration` | `IMPLEMENTED` | Phase 1 Core |
| `fixed_wing_interface` | `PARTIAL` | Phase 1 Core |
| `hover_physics` | `IMPLEMENTED` | Phase 1 Core |
| `transition_physics` | `IMPLEMENTED` | Phase 1 Core |
| `electrical_battery_sizing` | `IMPLEMENTED` | Phase 1 Core |
| `mass_convergence` | `IMPLEMENTED` | Phase 1 Core |
| `stability_and_control` | `IMPLEMENTED` | Phase 1 Core |
| `optimization` | `NOT_IMPLEMENTED_YET` | Phase 2+ Deferred Physics |
| `verification` | `NOT_IMPLEMENTED_YET` | Phase 2+ Deferred Physics |

## 5. Fixed-Wing Integration Boundary

- **Adapter Status**: `PARTIAL`
- **Delegated Subsystems**: Wing, Tail, Fuselage, Cruise Propulsion, Forward Aerodynamics

## 6. Mass Properties, CG & Multidisciplinary Convergence (Phase 5)

- **Converged MTOW**: `7.500 kg`
- **Empty Weight**: `4.763 kg`
- **Battery Weight**: `1.837 kg`
- **Payload Weight**: `0.90 kg`
- **Convergence Status**: `CONVERGED` (1 iterations, residual `0.000206 kg`)
- **Longitudinal CG**: `x_cg = 0.5194 m` (29.9% MAC, datum: `FUSELAGE_NOSE`)
- **Mass Conservation Residual**: `0.000000 kg`

### Component Mass Ledger

| Category | Component | Mass (kg) | x_arm (m) | Moment (kg*m) | Classification |
|:---|:---|:---:|:---:|:---:|:---:|
| `STRUCTURE` | Wing Structure | 0.7590 | 0.543 | 0.4123 | `DERIVED` |
| `STRUCTURE` | Fuselage Structure | 0.9000 | 0.711 | 0.6399 | `CONFIGURABLE_ASSUMPTION` |
| `STRUCTURE` | Tail Structure | 0.2120 | 1.200 | 0.2544 | `DERIVED` |
| `STRUCTURE` | Twin Booms Structure | 0.4500 | 0.600 | 0.2700 | `CONFIGURABLE_ASSUMPTION` |
| `STRUCTURE` | Landing Gear Assembly | 0.2800 | 0.450 | 0.1260 | `CONFIGURABLE_ASSUMPTION` |
| `STRUCTURE` | Structural Hardware & Fasteners | 0.1800 | 0.500 | 0.0900 | `CONFIGURABLE_ASSUMPTION` |
| `PROPULSION` | Lift Motors (4x) | 0.7200 | 0.500 | 0.3600 | `DERIVED` |
| `PROPULSION` | Lift ESCs (4x) | 0.1680 | 0.500 | 0.0840 | `CONFIGURABLE_ASSUMPTION` |
| `PROPULSION` | Lift Propellers (4x) | 0.2080 | 0.500 | 0.1040 | `DERIVED` |
| `PROPULSION` | Forward Cruise Motor | 0.1400 | 0.900 | 0.1260 | `DERIVED` |
| `PROPULSION` | Forward Cruise ESC | 0.0450 | 0.800 | 0.0360 | `CONFIGURABLE_ASSUMPTION` |
| `PROPULSION` | Forward Cruise Propeller | 0.0350 | 0.950 | 0.0333 | `CONFIGURABLE_ASSUMPTION` |
| `PROPULSION` | Propulsion Mounts & Hardware | 0.1200 | 0.500 | 0.0600 | `CONFIGURABLE_ASSUMPTION` |
| `ELECTRICAL` | Primary Flight Battery Pack | 1.8368 | 0.450 | 0.8266 | `DERIVED` |
| `ELECTRICAL` | Electrical Wiring Harness | 0.2200 | 0.450 | 0.0990 | `CONFIGURABLE_ASSUMPTION` |
| `ELECTRICAL` | Power Distribution Board & Regulators | 0.0850 | 0.400 | 0.0340 | `CONFIGURABLE_ASSUMPTION` |
| `AVIONICS` | Primary Flight Controller | 0.0450 | 0.250 | 0.0112 | `DERIVED` |
| `AVIONICS` | GNSS & Navigation Unit | 0.0650 | 0.350 | 0.0227 | `DERIVED` |
| `AVIONICS` | Telemetry & RC Communication | 0.0500 | 0.480 | 0.0240 | `DERIVED` |
| `AVIONICS` | Pitot-Static & Air Data Sensors | 0.0350 | 0.100 | 0.0035 | `DERIVED` |
| `AVIONICS` | Companion Computer | 0.0460 | 0.300 | 0.0138 | `DERIVED` |
| `PAYLOAD` | Primary Mission Payload | 0.6500 | 0.300 | 0.1950 | `DERIVED` |
| `PAYLOAD` | Payload Mount & Dampener | 0.2500 | 0.280 | 0.0700 | `DERIVED` |

## 7. Aerodynamic Stability Derivatives & Control-Surface Sizing (Phase 6)

- **Wing MAC**: `0.1413 m` (LE: `0.4600 m`)
- **Wing Aerodynamic Center**: `x_AC = 0.4953 m` (25.0% MAC)
- **Neutral Point**: `x_NP = 0.5295 m` (49.2% MAC)
- **Static Margin**: `7.15% MAC` (0.0101 m) [`STABLE`]
- **Tail Volume Coefficients**: `V_H = 0.5000`, `V_V = 0.0400`

### Inverted V-Tail & Control Surfaces

- **Inverted V-Tail Area**: `0.1032 m²` (2 panels x `0.0516 m²`, dihedral: `45.3°`)
- **Projected Areas**: Horizontal = `0.0726 m²`, Vertical = `0.0733 m²`
- **Effective Lift Areas**: S_H_eff = `0.0510 m²`, S_V_eff = `0.0521 m²`
- **Ruddervator Area**: `0.0309 m²` (30.0% tail, chord ratio `0.30`)
- **Ruddervator Mixing**: `delta_left = delta_e - delta_r; delta_right = delta_e + delta_r` (Limits: `±25°`)
- **Wing Aileron Area**: `0.0206 m²` (8.23% wing, span: 2 x `0.270 m`)

### Stability & Control Derivatives

- `C_m_alpha`: `-0.3700 1/rad` (Pitch Stiff: `True`)
- `C_n_beta`: `0.1093 1/rad` (Weathercock Stable: `True`)
- `C_l_beta`: `-0.0524 1/rad` (Dihedral Effect: `True`)
- `C_m_delta_e`: `-1.1034 1/rad`
- `C_n_delta_r`: `-0.0883 1/rad`
- `C_l_delta_a`: `0.3495 1/rad`

### Trim Feasibility & CG Envelope

- **Overall Trim Status**: `TRIM_FEASIBLE`
- **Longitudinal CG Envelope**: `[0.4741 m .. 0.5225 m]` (Width: `34.2% MAC`, Status: `WITHIN_LIMITS`)
- **Control Authority Status**: `AUTHORITY_CALCULATED` (Pitch Max: `8.04 N·m`, Yaw Max: `8.21 N·m`, Roll Max: `25.99 N·m`)

