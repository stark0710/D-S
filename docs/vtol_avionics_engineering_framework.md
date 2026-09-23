# VTOL Avionics Engineering Framework

## VTOL Avionics Engineering Philosophy
The Torq Wings Design Studio VTOL Avionics subsystem acts as the central nervous system of every designed vertical takeoff and landing aircraft. Unlike traditional fixed-wing aircraft, VTOL platforms present complex stabilization challenges during hover, transition phases, and cruise. Thus, the framework prioritizes:
1. **Multi-Regime Control**: Sizing flight controllers that support both PX4 and ArduPilot VTOL configurations.
2. **Deterministic Computing**: Selecting companion computers that can interface safely without compromising real-time flight stabilization loops.
3. **Safety-first Redundancy**: Enforcing sensor and bus redundancy based on mission critical profiles (e.g. triple-redundant flight controllers and dual-GPS for Cargo and Military operations).

---

## Navigation Architecture
Our navigation subsystem integrates:
- **EKF2 and EKF3 State Estimation**: Fusing IMU, Magnetometer, Barometer, and GPS/GNSS receiver outputs.
- **RTK (Real-Time Kinematic) Sizing**: Auto-configuring RTK GPS units for Surveying and Mapping mission categories, providing centimeter-level precision.
- **Visual Positioning & Odometry**: Activating visual positioning on companion processors for GPS-denied navigation.

---

## Communication Architecture
The communication system configures:
- **RF Telemetry Links**: Standard 915 MHz or 433 MHz telemetry transceivers, matching range targets and power restrictions.
- **Data Bus Topologies**:
  - **CAN Bus**: Leveraged for ESC telemetry, actuator feedback, and sensor voting, including dual CAN bus redundancy in safety-critical layouts.
  - **Ethernet**: Configured as the high-bandwidth backbone between flight controllers (e.g. Pixhawk 6X) and companion computers.
  - **UART/I2C/SPI**: Used for short-range point-to-point peripheral communication.

---

## Companion Computer Integration
Companion computers (e.g., Jetson Orin NX, Raspberry Pi 4) are sized based on required AI throughput (TOPS) and vision requirements:
- **Low Autonomy (Level 1-2)**: Standalone Flight Controller or lightweight Raspberry Pi 4 (UART interface).
- **Medium Autonomy (Level 3-4)**: Jetson Xavier NX/RK3588 (CAN or Ethernet interface).
- **High Autonomy / Vision-Based (Level 5)**: Jetson Orin NX/Intel NUC connected via high-speed Ethernet with PTP (Precision Time Protocol) clock alignment.

---

## Redundancy Philosophy
The framework enforces three levels of redundancy:
- **Single**: Baseline single-controller setup for light/hobbyist aircraft.
- **Dual**: High availability with dual-GPS, dual-IMU, and secondary BEC power routing.
- **Triple**: Fail-operational hardware setup featuring triple-redundant IMUs, dual RTK GNSS, dual redundant CAN buses, and isolated power backup rails.

---

## Health Monitoring
The sized avionics stack supports real-time health diagnostics:
- **Pre-flight Checklists**: Validating battery health, sensor calibration, and telemetry link budget before takeoff.
- **In-flight Sensor Voting**: Real-time cross-checking of triple IMU sensors to identify and isolate drift or failure.
- **Vibration Monitoring**: Active vibration diagnostics to warn operators of mechanical failures in lift rotors or structural booms.

---

## Validation Assumptions
The validator checks and flags:
- **CPU Overload**: Warns if expected CPU load exceeds 85%.
- **Memory Footprint**: Warns if software memory needs exceed 80% of total onboard RAM.
- **Power Surcharge**: Ensures the avionics stack does not draw power exceeding the power budget.
- **Bus Incompatibility**: Verifies the selected Flight Controller has the physical buses (e.g. Ethernet) required by the chosen Companion Computer.

---

## Extension Mechanism
To add new flight controllers, companion computers, or sensor suites:
1. Extend the databases inside `flight_controller_selector.py` or `companion_computer.py` with the new hardware specs.
2. If a new mission category requires a unique setup, implement a new `AvionicsStrategy` in `avionics_strategy.py` and register it inside `avionics_registry.py`.
