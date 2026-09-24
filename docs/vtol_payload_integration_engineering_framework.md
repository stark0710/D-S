# VTOL Payload Integration Engineering Framework

## VTOL Payload Engineering Philosophy
VTOL aircraft present a unique design challenge due to their dynamic transitions between hover flight, transitioning, and forward flight. The payload subsystem must be designed not just as an auxiliary weight but as an integrated component that impacts structural integrity, thermal loading, center of gravity (CG), aerodynamics, and power distribution. The framework's core philosophies are:
1. **Dynamic CG Compensation**: Sizing and locating payloads such that the resulting CG remains strictly within the aircraft's stability margin (expressed as % of Mean Aerodynamic Chord).
2. **Modular Interfacing**: Promoting fast operational reconfigurations via standardized electrical and mechanical quick-release connectors.
3. **Rigid Structural Isolation**: Mitigating vibration from lift rotors and forward propulsion systems to secure clean data capture for sensitive cameras, LiDARs, and sensor payloads.

---

## Payload Integration Methodology
Every selected payload goes through a multi-step sizing and validation pipeline:
1. **Selection**: Identifying the ideal camera, LiDAR, cargo pod, or sprayer system based on mission strategy.
2. **Mounting**: Sizing the appropriate fixed, 2-axis, or 3-axis gimbals or cargo rails, including drag calculations.
3. **Interfacing**: Mapping required power limits and high-speed data buses.
4. **CG Sizing**: Calculating the shift in composite aircraft CG (in x, y, and z planes).
5. **Validation**: Enforcing constraint checks (max mass, power budget, packaging space fit).

---

## Structural Interfaces
The framework models mechanical mounting structures:
- **Gimbal Assemblies**: Auto-calculated weight and aerodynamic drag coefficients ($C_d$) for exposed cameras.
- **Cargo Bay Rails**: Standard mounting track alignments in the fuselage compartment.
- **Vibration Damping Isolators**: Damping bushings sized to suppress vibration from rotors during high-power hover.
- **Quick-Release Interfaces**: Lightweight mechanical latch structures enabling field swap-out times under 2 minutes.

---

## Electrical Interfaces
Electrical connections are sized according to voltage and bandwidth criteria:
- **Power Sizing**: Determining peak/continuous current and routing to BEC rails (5V, 12V) or directly to main bus batteries (24V/48V) with active fuse sizing.
- **Data Connections**: Mapping interfaces to USB3, HDMI, CAN, UART, or high-bandwidth Ethernet cables to communicate with companion processors and telemetry modems.

---

## Thermal Management
Heat dissipation is validated for enclosed compartments:
- **Passive Dissipation**: Grounded heat sink paths for low-draw cameras.
- **Active Cooling**: Sizing forced-induction airflows (required CFM) for high-draw equipment (e.g. LiDAR, radar, communication relays).
- **Clearance Safety**: Tracking local compartment temperatures to ensure a cooling margin above 10°C is preserved.

---

## Mission Adaptability
Supported strategies cater to specialized profiles:
- **Survey & Mapping**: Stabilized gimbals, RTK precision, and high-speed image logging.
- **Cargo & Delivery**: Aerodynamic pods, release rail latches, and GPIO-linked emergency release systems.
- **Agricultural Sprayers**: Tank-slosh damping, high-power pump relays, and GPIO valve timing.
- **Military / Tactical**: Radar systems, active cooling, EMI shielded cabling, and secure Ethernet loops.

---

## Validation Assumptions
The validator checks and flags:
- **Mass limit violation**: Warns if payload weight exceeds structural capabilities.
- **Power limit violation**: Warns if total power draw exceeds the designated payload budget.
- **CG Shift violation**: Flags shifts greater than +/- 5.0% of Mean Aerodynamic Chord (MAC).
- **Physical fit envelope**: Flags if payload length, width, or height exceeds fuselage bay dimensions.

---

## Extension Mechanism
To extend the framework:
1. **Add new Payloads**: Update the database inside `payload_selector.py` with the physical and electrical specifications of the new hardware.
2. **Add Custom Strategies**: Implement the `PayloadStrategy` interface in `payload_strategy.py` and register it inside `payload_registry.py`.
