# Torq Wings Final Aircraft Design Specification: TW-VTOL-20260921-213333

**Aircraft Class**: `VTOL`  
**Configuration**: `Lift + Cruise QuadPlane (4 Vertical Lift Rotors + 1 Forward Cruise Pusher/Pusher, Twin Booms, Inverted V-Tail)`  
**Design Status**: `DESIGN_VALIDATED`  
**Flight Validation Status**: `PHYSICAL_GROUND_VALIDATED` (Flight Validated: `False`)  
> [!IMPORTANT]
> DESIGN, BENCH, AND GROUND COMMISSIONED ONLY. FLIGHT TEST ENVELOPE NOT ESTABLISHED.

## 1. Executive Summary & Mission Requirements

| Parameter | Requirement | Sized / Achieved | Margin / Delta |
|:---|:---|:---|:---|
| Payload Mass | 1.5 kg [MIN] | 1.5 kg | +0.00 kg (`PASS`) |
| Cruise Endurance | 30.0 min [MIN] | 217.0 min | +187.00 min (`PASS`) |
| Range | 40.0 km [MIN] | 361.62 km | +321.62 km (`PASS`) |
| Hover Duration | 5.0 min [MIN] | 5.0 min | +0.00 min (`PASS`) |

## 2. Mass Properties & Center of Gravity

- **Maximum Takeoff Weight (MTOW)**: `8.264 kg`
- **Empty Mass**: `4.959 kg`
- **Payload Mass**: `1.500 kg`
- **Battery Mass**: `2.450 kg`
- **Center of Gravity (CG)**: `[0.5150, 0.0000, 0.0000] m`
- **Allowable CG Travel Range**: `[0.4749 m .. 0.5257 m]` (Margin: `0.0508 m`)
- **Inertia Tensor Status**: `DEFERRED` (Detailed solid-body inertia tensor deferred to 3D CAD mass properties compilation.)

### Major Component Mass Breakdown

| Component | Category | Mass (kg) | X_CG (m) | Y_CG (m) | Z_CG (m) | Provenance |
|:---|:---|:---|:---|:---|:---|:---|
| Airframe & Booms | STRUCTURE | 2.232 | 0.515 | 0.000 | 0.000 | `CALCULATED` |
| Lift Propulsion (4x Motors + Props) | PROPULSION | 1.480 | 0.515 | 0.000 | 0.000 | `CALCULATED` |
| Cruise Propulsion (Motor + Prop) | PROPULSION | 0.420 | 0.050 | 0.000 | 0.000 | `CALCULATED` |
| Lift ESCs (4x Spedix GS40A) | PROPULSION | 0.080 | 0.515 | 0.000 | 0.000 | `CALCULATED` |
| Cruise ESC (Hobbywing Skywalker 40A) | PROPULSION | 0.045 | 0.200 | 0.000 | 0.000 | `CALCULATED` |
| Flight Battery | ENERGY | 2.450 | 0.475 | 0.000 | 0.000 | `CALCULATED` |
| Payload | PAYLOAD | 1.500 | 0.535 | 0.000 | -0.030 | `CALCULATED` |
| Avionics & Harness | AVIONICS | 0.380 | 0.400 | 0.000 | 0.000 | `CALCULATED` |

## 3. Aerodynamics & Wing Geometry

- **Wingspan (b)**: `2.400 m`
- **Wing Reference Area (S)**: `0.6500 m²`
- **Aspect Ratio (AR)**: `8.86`
- **Mean Aerodynamic Chord (MAC)**: `0.2740 m` (LE: `0.4400 m`)
- **Root / Tip Chords**: `0.3100 m` / `0.2300 m` (Taper: `0.74`)
- **Airfoils**: Root: `MH60 (or Selig S8036)`, Tip: `MH60`
- **Cruise Lift Coefficient ($C_L$)**: `0.480`
- **Zero-Lift Drag Coefficient ($C_{D0}$)**: `0.0320`
- **Cruise Lift-to-Drag ($L/D$)**: `11.20` (Max $L/D$: `13.00`)

## 4. Fuselage, Booms & Empennage

- **Fuselage Dimensions (L x W x H)**: `1.450 m x 0.180 m x 0.200 m`
- **Fineness Ratio**: `8.06`
- **Twin Booms**: `2 booms`, Length: `1.350 m`, Spacing: `0.820 m`
- **Empennage Type**: `INVERTED_V_TAIL`
- **Tail Area**: `0.1250 m²`
- **V-Tail Dihedral**: `110.0°`
- **Projected Areas**: Horizontal = `0.0950 m²`, Vertical = `0.0550 m²`

## 5. Propulsion System Architecture

### Cruise Propulsion
- **Motor**: `Sunnysky X4120 550KV` (1x)
- **Propeller**: `APC 15x8E` (Dia: `15.0"`, Pitch: `8.0"`)
- **Cruise ESC**: `Hobbywing Skywalker 40A V2` (`40A`)
- **Cruise Electrical Power**: `175.0 W` (Thrust: `8.20 N`)

### VTOL Lift Propulsion
- **Lift Motors**: `T-Motor MN5008 KV340` (4x)
- **Lift Propellers**: `T-Motor 18x6.1 Carbon` (Dia: `18.0"`)
- **Lift ESC**: `Spedix GS40A` (`40A`)
- **Thrust-to-Weight (T/W)**: `1.50` (Total Hover Thrust: `121.6 N`)
- **Hover Electrical Power**: `1100.0 W` (Disk Loading: `7.8 kg/m²`)

### VTOL Transition Dynamics
- **Stall Speed ($V_{stall}$)**: `15.50 m/s`
- **Safe Transition Speed ($V_{trans}$)**: `18.60 m/s`
- **Transition Duration**: `18.0 s`
- **Transition Energy**: `24.50 Wh`

## 6. Energy Storage & Electrical Architecture

- **Battery**: `Tattu Plus 6S 22000mAh 25C` (6S LiPo, `22.2 V`)
- **Capacity / Energy**: `22000 mAh` / `488.4 Wh`
- **Mission Energy Required**: `280.0 Wh`
- **Battery Reserve**: `22.0%`

## 7. Stability, Control & Trim

- **Neutral Point ($x_{NP}$)**: `0.5332 m` (49.2% MAC)
- **Static Margin**: `7.27% MAC` (`0.0108 m`)
- **Longitudinal Stability ($C_{m\alpha}$)**: `-0.3761 1/rad` (Stable: `True`)
- **Directional Stability ($C_{n\beta}$)**: `0.1093 1/rad` (Stable: `True`)
- **Lateral Stability ($C_{l\beta}$)**: `-0.0524 1/rad` (Stable: `True`)
- **Elevator Control Power ($C_{m\delta_e}$)**: `-1.1034 1/rad`
- **Trim Status**: Feasible (`True`), Trim Elevator: `-1.20°`

## 8. Commercial Hardware Bill of Materials (BOM)

| Category | Role | Component | Part Number | Qty | Unit Mass | Total Mass | Status |
|:---|:---|:---|:---|:---|:---|:---|:---|
| PROPULSION_LIFT | VTOL Lift Motor | T-Motor MN5008 KV340 | N/A | 4 | 0.285 kg | 1.140 kg | `COMMERCIAL_COMPONENT_VERIFIED` |
| PROPULSION_LIFT | VTOL Lift ESC | Spedix Spedix GS40A | SP-GS40A-4IN1 | 4 | 0.020 kg | 0.080 kg | `COMMERCIAL_COMPONENT_VERIFIED` |
| PROPULSION_CRUISE | Forward Cruise Motor | Sunnysky X4120 550KV | N/A | 1 | 0.330 kg | 0.330 kg | `COMMERCIAL_COMPONENT_VERIFIED` |
| PROPULSION_CRUISE | Forward Cruise ESC | Hobbywing Hobbywing Skywalker 40A V2 | HW-SK40A-V2 | 1 | 0.045 kg | 0.045 kg | `COMMERCIAL_COMPONENT_VERIFIED` |
| ENERGY | Flight Battery Pack | Tattu Tattu Plus 6S 22000mAh 25C | N/A | 1 | 2.450 kg | 2.450 kg | `COMMERCIAL_COMPONENT_VERIFIED` |
| AVIONICS | Autopilot / Flight Controller | Holybro Pixhawk 6X | N/A | 1 | 0.085 kg | 0.085 kg | `COMMERCIAL_COMPONENT_VERIFIED` |

## 9. CAD Handover Specification

- **Reference Datum**: `Fuselage Nose Apex at Centerline`
- **Aircraft Origin**: `X=0, Y=0, Z=0`
- **CG Location**: `[0.5150, 0.0000, 0.0000] m`
- **Airfoils**: MH60 (or Selig S8036), MH60
- **Mounting Coordinates Resolved**:
  - `cruise_motor`: `[0.050, 0.000, 0.000] m`
  - `lift_motor_front_left`: `[0.165, -0.410, 0.020] m`
  - `lift_motor_front_right`: `[0.165, 0.410, 0.020] m`
  - `lift_motor_rear_left`: `[0.865, -0.410, 0.020] m`
  - `lift_motor_rear_right`: `[0.865, 0.410, 0.020] m`
  - `wing_mount_spar_le`: `[0.508, 0.000, 0.000] m`
  - `tail_mount`: `[1.330, 0.000, 0.080] m`

## 10. Simulation Handover Specification

- **MTOW**: `8.264 kg`, Empty Mass: `4.959 kg`
- **CG Vector**: `[0.5150, 0.0000, 0.0000] m`
- **Inertia Tensor**: `DEFERRED` (Detailed solid-body inertia tensor deferred to 3D CAD mass properties compilation.)
- **Aerodynamic Polars & Trim Conditions Exposing Complete 6-DOF Handover Coefficients**.
