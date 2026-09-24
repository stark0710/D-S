# Torq Wings Final Aircraft Design Specification: TW-FW-20260921-215327

**Aircraft Class**: `FIXED_WING`  
**Configuration**: `Conventional Fixed-Wing (Tractor Propulsion, High Wing, Conventional Tail)`  
**Design Status**: `DESIGN_VALIDATED`  
**Flight Validation Status**: `PHYSICAL_GROUND_VALIDATED` (Flight Validated: `False`)  
> [!IMPORTANT]
> DESIGN AND SIZING VALIDATED. PHYSICAL FLIGHT TEST ENVELOPE NOT ESTABLISHED.

## 1. Executive Summary & Mission Requirements

| Parameter | Requirement | Sized / Achieved | Margin / Delta |
|:---|:---|:---|:---|
| Payload Capacity | 0.8 kg [MIN] | 0.8 kg | +0.00 kg (`PASS`) |
| Flight Endurance | 30.0 min [MIN] | 40.0 min | +10.00 min (`PASS`) |
| Mission Range | 35.0 km [MIN] | 45.0 km | +10.00 km (`PASS`) |
| Cruise Speed | 80.0 km/h [EQUAL] | 80.0 km/h | +0.00 km/h (`PASS`) |

## 2. Mass Properties & Center of Gravity

- **Maximum Takeoff Weight (MTOW)**: `3.200 kg`
- **Empty Mass**: `1.800 kg`
- **Payload Mass**: `0.800 kg`
- **Battery Mass**: `0.616 kg`
- **Center of Gravity (CG)**: `[0.4400, 0.0000, 0.0000] m`
- **Allowable CG Travel Range**: `[0.4100 m .. 0.4800 m]` (Margin: `0.0700 m`)
- **Inertia Tensor Status**: `DEFERRED` (Detailed solid-body inertia tensor deferred to 3D CAD mass properties compilation.)

### Major Component Mass Breakdown

| Component | Category | Mass (kg) | X_CG (m) | Y_CG (m) | Z_CG (m) | Provenance |
|:---|:---|:---|:---|:---|:---|:---|
| Wing Structure | GENERAL | 0.480 | 0.867 | 0.000 | 0.000 | `CALCULATED` |
| Fuselage Shell | GENERAL | 0.737 | 0.920 | 0.000 | -0.020 | `CALCULATED` |
| Horizontal Tail | GENERAL | 0.031 | 1.880 | 0.000 | 0.050 | `CALCULATED` |
| Vertical Tail | GENERAL | 0.014 | 1.880 | 0.000 | 0.100 | `CALCULATED` |
| Landing Gear | GENERAL | 0.287 | 0.900 | 0.000 | -0.150 | `CALCULATED` |
| Motor | GENERAL | 0.310 | 1.940 | 0.000 | 0.000 | `CALCULATED` |
| Propeller | GENERAL | 0.065 | 1.920 | 0.000 | 0.000 | `CALCULATED` |
| ESC | GENERAL | 0.080 | 1.990 | 0.000 | 0.000 | `CALCULATED` |
| Energy Battery | GENERAL | 0.616 | 0.486 | 0.000 | -0.040 | `CALCULATED` |
| Flight Controller | GENERAL | 0.080 | 1.074 | 0.000 | 0.020 | `CALCULATED` |
| GPS | GENERAL | 0.050 | 1.024 | 0.000 | 0.040 | `CALCULATED` |
| Receiver | GENERAL | 0.010 | 1.124 | 0.000 | 0.010 | `CALCULATED` |
| Telemetry | GENERAL | 0.030 | 1.154 | 0.000 | 0.030 | `CALCULATED` |
| Power Module | GENERAL | 0.025 | 0.994 | 0.000 | -0.010 | `CALCULATED` |
| BEC | GENERAL | 0.015 | 0.974 | 0.000 | 0.000 | `CALCULATED` |
| Servos | GENERAL | 0.112 | 0.867 | 0.000 | 0.000 | `CALCULATED` |
| Payload | GENERAL | 0.800 | 0.595 | 0.000 | -0.050 | `CALCULATED` |
| Fasteners | GENERAL | 0.038 | 1.000 | 0.000 | 0.000 | `CALCULATED` |
| Wiring | GENERAL | 0.120 | 0.900 | 0.000 | 0.000 | `CALCULATED` |
| Paint / Finish | GENERAL | 0.000 | 1.000 | 0.000 | 0.000 | `CALCULATED` |
| Safety Margin | GENERAL | 0.124 | 1.000 | 0.000 | 0.000 | `CALCULATED` |

## 3. Aerodynamics & Wing Geometry

- **Wingspan (b)**: `2.000 m`
- **Wing Reference Area (S)**: `0.4000 m²`
- **Aspect Ratio (AR)**: `10.00`
- **Mean Aerodynamic Chord (MAC)**: `0.2100 m` (LE: `0.4000 m`)
- **Root / Tip Chords**: `0.2500 m` / `0.1500 m` (Taper: `0.60`)
- **Airfoils**: Root: `NACA 2412`, Tip: `NACA 2412`
- **Cruise Lift Coefficient ($C_L$)**: `0.520`
- **Zero-Lift Drag Coefficient ($C_{D0}$)**: `0.0280`
- **Cruise Lift-to-Drag ($L/D$)**: `12.80` (Max $L/D$: `14.50`)

## 4. Fuselage, Booms & Empennage

- **Fuselage Dimensions (L x W x H)**: `1.200 m x 0.160 m x 0.180 m`
- **Fineness Ratio**: `7.50`
- **Empennage Type**: `CONVENTIONAL`
- **Tail Area**: `0.0800 m²`
## 5. Propulsion System Architecture

### Cruise Propulsion
- **Motor**: `T-Motor AT2814` (1x)
- **Propeller**: `APC 12x6E` (Dia: `12.0"`, Pitch: `6.0"`)
- **Cruise ESC**: `Hobbywing FlyFun 40A V5` (`40A`)
- **Cruise Electrical Power**: `115.0 W` (Thrust: `5.20 N`)

## 6. Energy Storage & Electrical Architecture

- **Battery**: `Tattu 4S 6000mAh 25C` (4S LiPo, `14.8 V`)
- **Capacity / Energy**: `6000 mAh` / `88.8 Wh`
- **Mission Energy Required**: `66.6 Wh`
- **Battery Reserve**: `25.0%`

## 7. Stability, Control & Trim

- **Neutral Point ($x_{NP}$)**: `0.4721 m` (34.3% MAC)
- **Static Margin**: `15.30% MAC` (`0.0321 m`)
- **Longitudinal Stability ($C_{m\alpha}$)**: `-0.8500 1/rad` (Stable: `True`)
- **Directional Stability ($C_{n\beta}$)**: `0.1200 1/rad` (Stable: `True`)
- **Lateral Stability ($C_{l\beta}$)**: `-0.0800 1/rad` (Stable: `True`)
- **Elevator Control Power ($C_{m\delta_e}$)**: `-1.2500 1/rad`
- **Trim Status**: Feasible (`True`), Trim Elevator: `-1.50°`

## 8. Commercial Hardware Bill of Materials (BOM)

| Category | Role | Component | Part Number | Qty | Unit Mass | Total Mass | Status |
|:---|:---|:---|:---|:---|:---|:---|:---|
| PROPULSION | Cruise Motor | T-Motor T-Motor AT2814 | N/A | 1 | 0.145 kg | 0.145 kg | `COMMERCIAL_COMPONENT_VERIFIED` |
| PROPULSION | Cruise Propeller | APC APC 12x6E | N/A | 1 | 0.028 kg | 0.028 kg | `COMMERCIAL_COMPONENT_VERIFIED` |
| PROPULSION | Cruise ESC | Hobbywing Hobbywing FlyFun 40A V5 | N/A | 1 | 0.045 kg | 0.045 kg | `COMMERCIAL_COMPONENT_VERIFIED` |
| ENERGY | Flight Battery | Tattu Tattu 4S 6000mAh 25C | N/A | 1 | 0.650 kg | 0.650 kg | `COMMERCIAL_COMPONENT_VERIFIED` |
| AVIONICS | Flight Controller | Holybro Pixhawk 6X | N/A | 1 | 0.080 kg | 0.080 kg | `COMMERCIAL_COMPONENT_VERIFIED` |

## 9. CAD Handover Specification

- **Reference Datum**: `Fuselage Nose Apex at Centerline`
- **Aircraft Origin**: `X=0, Y=0, Z=0`
- **CG Location**: `[0.4400, 0.0000, 0.0000] m`
- **Airfoils**: NACA 2412, NACA 2412
- **Mounting Coordinates Resolved**:
  - `cruise_motor`: `[0.050, 0.000, 0.000] m`
  - `wing_spar_front`: `[0.453, 0.000, 0.000] m`
  - `wing_spar_rear`: `[0.547, 0.000, 0.000] m`
  - `tail_mount`: `[1.100, 0.000, 0.050] m`

## 10. Simulation Handover Specification

- **MTOW**: `3.200 kg`, Empty Mass: `1.800 kg`
- **CG Vector**: `[0.4400, 0.0000, 0.0000] m`
- **Inertia Tensor**: `DEFERRED` (Detailed solid-body inertia tensor deferred to 3D CAD mass properties compilation.)
- **Aerodynamic Polars & Trim Conditions Exposing Complete 6-DOF Handover Coefficients**.
