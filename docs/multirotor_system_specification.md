# Multirotor Design Studio
## Engineering System Specification (ESS v1.0)

This document defines the requirements, system architecture, sizing equations, design constraints, and schema structures for the **Multirotor Design Studio (V4)** subsystem of the Torq Wings platform.

---

## 1. Executive Mission & Scope

The mission of the Multirotor Design Studio is to automatically synthesize and optimize physically realizable, engineering-valid multirotor UAVs starting from high-level mission profiles and user constraints. The pipeline enforces multidisciplinary sizing loops (aerodynamics, propulsion, structures, and electronics) and outputs a comprehensive vehicle specification suitable for fabrication, certification, and control configuration.

---

## 2. Supported Missions & Categories

The pipeline supports sizing optimization for the following operational mission profiles:

- **Visual Inspections & Mapping**: Photography, Videography, Survey, Mapping, Infrastructure Inspection, Indoor Inspection.
- **Agricultural Operations**: Crop Spraying, Remote Sensing, Vegetation Index Mapping.
- **Public Safety & Logistics**: Security, Surveillance, Search & Rescue, Disaster Assessment, Cargo Delivery, Heavy Lift, Emergency Response.
- **Science & Education**: Research, Flight Test Platforms, Academic Training.

---

## 3. Supported Configurations

The engine sizes geometries, coordinate locations, and rotor orientations for the following configurations:

| Configuration | Rotor Count ($N$) | Geometric Layout | Control Logic Description |
|---|---|---|---|
| **Tricopter** | 3 | $Y$-shape (120° offsets) | Yaw control via tilting servo on tail rotor |
| **Quadcopter X** | 4 | X-shape (symmetric) | Yaw control via differential counter-torque |
| **Quadcopter +** | 4 | Plus-shape (axes aligned) | Yaw control via differential counter-torque |
| **Hexacopter X** | 6 | X-shape (60° offsets) | Redundancy for single motor failures |
| **Hexacopter +** | 6 | Plus-shape (60° offsets) | Redundancy for single motor failures |
| **Octocopter X** | 8 | X-shape (45° offsets) | High reliability, heavy-lift capacity |
| **Octocopter +** | 8 | Plus-shape (45° offsets) | High reliability, heavy-lift capacity |
| **Coaxial X8** | 8 | 4 arms, coaxial pairs | Sized for compact footprint and high thrust |

---

## 4. Input Requirements Schema

The design optimizer accepts the following structured user requirements:

```json
{
  "mission_type": "SURVEY",
  "payload_weight_kg": 1.5,
  "payload_dimensions_m": [0.2, 0.15, 0.1],
  "target_flight_time_min": 35.0,
  "cruise_speed_kmh": 45.0,
  "maximum_speed_kmh": 65.0,
  "operating_altitude_m": 120.0,
  "operating_environment": "URBAN",
  "wind_conditions_kmh": 25.0,
  "budget_usd": 8000.0,
  "redundancy_required": true,
  "maximum_frame_size_m": 0.85,
  "battery_preference": "LiPo",
  "camera_requirement": "4K_GIMBAL",
  "autonomy_level": "FULLY_AUTONOMOUS"
}
```

---

## 5. Multidisciplinary Sizing Pipeline

The Multirotor Design Pipeline runs a convergent sizing loop to resolve weight and power balances:

```
[Requirement Inputs]
        │
        ▼
 1. Mission Translation ───────────► Translates payload, range, environment
        │
        ▼
 2. Configuration Selection ───────► Resolves topology (e.g., Quad X, Hexa X)
        │
┌───────┴────────────────────────┐
│  3. Frame Selection & Sizing   │◄─┐
│       │                        │  │
│  4. Motor Selection & Sizing   │  │
│       │                        │  │
│  5. Propeller Sizing & Aerody  │  │
│       │                        │  │
│  6. ESC Selection & Rating     │  │
│       │                        │  │
│  7. Battery Sizing & Chemistry │  │
│       │                        │  │
│  8. Power Distribution Design  │  │
│       │                        │  │
│  9. Avionics & Comms Selection │  │ (Iterative MTOW Convergence Loop)
│       │                        │  │
│ 10. Payload Packaging Layout   │  │
│       │                        │  │
│ 11. Mass Properties & Inertias │  │
│       │                        │  │
│ 12. CG Balance & Optimization  │  │
│       │                        │  │
│ 13. Flight Performance Analysis│──┘
└───────┬────────────────────────┘
        ▼
 14. Sizing Convergence? ──────────► Checks MTOW delta <= 1.0%
        │
        ▼
 15. Verification Rule Engine ─────► Dynamic safety and margin check validations
        │
        ▼
 16. Certification Audit ──────────► Emits final Airworthiness Certification
        │
        ▼
[MultirotorAircraftSpecification] ─► Validated engineering data spec
```

---

## 6. Sizing & Optimization Physics Equations

The Multirotor pipeline executes the following physics modules to size and validate the design:

### 6.1 Aerodynamics & Propulsion
- **Total Hover Thrust Required ($T_{hover}$)**:
  $$T_{hover} = AUW \cdot g$$
  where $AUW$ is the All-Up Takeoff Weight in kg, and $g = 9.80665 \text{ m/s}^2$.
- **Thrust per Rotor in Hover ($T_{rotor\_hover}$)**:
  $$T_{rotor\_hover} = \frac{T_{hover}}{N}$$
  where $N$ is the number of active rotors.
- **Thrust-to-Weight Ratio ($T/W$)**:
  $$T/W = \frac{N \cdot T_{rotor\_max}}{AUW \cdot g}$$
  Enforced constraint: $T/W \ge 2.0$ (standard), or $T/W \ge 2.5$ (heavy wind/cargo).
- **Disc Loading ($DL$)**:
  $$DL = \frac{T_{hover}}{N \cdot A_{disk}}$$
  where $A_{disk} = \frac{\pi}{4} D_p^2$ and $D_p$ is the propeller diameter.
- **Blade Tip Speed ($V_{tip}$)**:
  $$V_{tip} = \pi \cdot RPM \cdot \frac{D_p}{60}$$
  Constraint: $V_{tip} \le 220 \text{ m/s}$ (to minimize compressibility losses and acoustic noise).

### 6.2 Electrical & Power
- **Induced Hover Power ($P_{induced}$)**:
  $$P_{induced} = \sqrt{\frac{T_{hover}^3}{2 \rho (N \cdot A_{disk})}}$$
  where $\rho$ is the atmospheric air density at altitude.
- **Shaft Power Required ($P_{shaft}$)**:
  $$P_{shaft} = \frac{P_{induced}}{\eta_{prop}}$$
  where $\eta_{prop}$ is the propeller aerodynamic efficiency factor.
- **Electrical Input Power ($P_{electrical}$)**:
  $$P_{electrical} = \frac{P_{shaft}}{\eta_{motor} \cdot \eta_{esc}}$$
- **Required Battery Discharge Rate (C-Rating)**:
  $$I_{max} = \frac{P_{max}}{V_{batt}}$$
  $$C_{required} = \frac{I_{max}}{Capacity_{Ah}}$$
  Constraint: $C_{required} \le 0.85 \cdot C_{discharge\_limit}$.

### 6.3 Mass & Center of Gravity (CG)
- **All-Up Takeoff Weight ($AUW$)**:
  $$AUW = m_{frame} + N \cdot (m_{motor} + m_{esc} + m_{prop}) + m_{battery} + m_{payload} + m_{avionics} + m_{wiring}$$
- **Center of Gravity Location ($X_{CG}$, $Y_{CG}$, $Z_{CG}$)**:
  $$X_{CG} = \frac{\sum m_i \cdot x_i}{\sum m_i}$$
  Constraint: $X_{CG}, Y_{CG}$ must lie within the **CoG tolerance circle** of radius $0.05 \cdot Wheelbase$ centered on the geometric center of thrust.

---

## 7. Operational Design Constraints

Every design synthesized by the pipeline must satisfy the following quality gates:

- **Minimum T/W Ratio**: $\ge 2.0$ under standard conditions, $\ge 2.3$ for heavy wind environments.
- **Propeller Clearance**: Minimum gap between propeller tips of adjacent rotors $\ge 0.15 \cdot D_p$ to prevent aerodynamic interference.
- **Motor Current Margin**: Max continuous current draw $\le 80\%$ of motor manufacturer rated limit.
- **ESC Current Margin**: Max current draw during peak takeoff $\le 85\%$ of ESC continuous rating.
- **Battery Discharge Depth**: Sized capacity must leave $\ge 20\%$ reserve capacity (80% Depth of Discharge) at the end of the target mission duration.

---

## 8. Database Catalog Dependencies

The pipeline queries a consolidated hardware catalog under `backend/database/` structured as follows:

1. **Frame Catalog**: Structuring arm lengths, masses, structural load limits, and maximum propeller size bounds.
2. **Motor Catalog**: KV ratings, mass, winding resistance, idle current, max current, and max voltage limits.
3. **Propeller Catalog**: Diameter, pitch, mass, and thrust/torque coefficient curves.
4. **ESC Catalog**: Ampere ratings, weight, operating voltage, and internal resistance.
5. **Battery Catalog**: Nominal voltage, capacity (mAh), mass, discharge C-ratings, and physical dimensions.
6. **Avionics & Comms**: Flight controllers (mass, current limits), GPS modules, telemetry transmitters (mass, range, power draw).

---

## 9. Output Model Schema (`MultirotorAircraftSpecification`)

Successful pipeline executions yield the following structured specification:

```python
@dataclass
class MultirotorAircraftSpecification:
    # 1. Mission context
    mission: MissionRequirements
    
    # 2. Geometry & configuration
    configuration: str  # e.g., "Quadcopter X"
    wheelbase_mm: float
    motor_positions_xy: list[tuple[float, float]]
    
    # 3. Component list
    motor_name: str
    propeller_name: str
    esc_name: str
    battery_name: str
    flight_controller_name: str
    telemetry_name: str
    
    # 4. Mass breakdown
    total_mass_kg: float
    empty_mass_kg: float
    battery_mass_kg: float
    payload_mass_kg: float
    
    # 5. Performance outputs
    hover_throttle_pct: float
    hover_time_min: float
    max_flight_time_min: float
    thrust_to_weight_ratio: float
    max_speed_kmh: float
    max_climb_rate_ms: float
    
    # 6. Verification and diagnostics
    static_margin_mm: float
    is_certified: bool
    certification_report: dict[str, Any]
    diagnostics: dict[str, Any]
```

---

## 10. Verification & Certification Audits

Verification is driven by the dynamic common rule engine. The certification check evaluates:
1. **Structural Margin**: Sized arm loading does not exceed yield limits under a $4.0g$ structural safety factor.
2. **Thermal Safety**: Motors and ESCs do not exceed maximum temperature ratings under a continuous 5-minute maximum hover climb simulation.
3. **Control Authority**: Sized yaw, pitch, and roll control authority are positive under a simulated 20 km/h wind gust.
4. **Electrical Health**: Sized battery voltage drop does not trigger low-battery warning limits before target mission duration.
