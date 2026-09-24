# Fixed-Wing Avionics Engineering Framework

## 1. Avionics Engineering Philosophy

The **Fixed-Wing Avionics Engineering Framework** designs and sizes the complete electronics brain, telemetry links, and navigation sensors of the aircraft. By consuming the results of preceding stages (`MissionResult`, `ConfigurationResult`, `WingResult`, `AirfoilResult`, `TailResult`, `FuselageResult`, `PropulsionResult`), the framework implements a decoupled systems boundary:
*   It does **not** conduct payload sensor engineering (which belongs to target payload design).
*   Instead, it determines flight controllers, autopilot firmware, GNSS receivers, telemetry modems, companion computers, and safety-critical flight sensors (such as pitot-static airspeed tubes).

This guarantees that the flight computer has sufficient computing headroom, range, power, and sensor safety redundancy to conduct autonomous missions.

---

## 2. Autopilot & Firmware Selection

Flight controller selections are driven by the mission safety level and computing loads:
*   **Matek H743-WING**: Low-cost, lightweight (30g) controller ideal for training and hobby gliders, running **ArduPilot**.
*   **Holybro Pixhawk 6C**: General utility flight controller for standard survey operations, running **ArduPilot** or **PX4**.
*   **Cube Orange+ / Pixhawk 6X**: High-end industrial flight computers featuring triple-redundant IMUs and isolated sensor boards. Standard choice for Cargo and BVLOS operations, running **ArduPilot** (excellent auto-grid surveying) or **PX4** (optimized gliding modes).

---

## 3. Navigation Architecture

Navigation configurations are sized according to strategy needs:
*   **Single GNSS**: Standard M8N/M9N receiver for local visual line-of-sight flight.
*   **Dual GNSS**: Sized for Cargo and Long Endurance to guard against satellite drops and antenna shadowing.
*   **RTK GNSS**: Center-stage choice for Survey/Mapping. High-precision Real-Time Kinematic corrections deliver centimeter-level photo geotags, eliminating the need for Ground Control Points.
*   **Visual Navigation**: Companion-computer odometry (optical flow or SLAM) for GNSS-denied environments.

---

## 4. Communication Architecture

Data link specifications are selected to match range and video telemetry demands:
*   **RC Control Link**:Sized using ELRS (2.4GHz/915MHz) or TBS Crossfire modems to deliver up to 40km of pilot control loop.
*   **Telemetry modems**:
    *   *SiK 915MHz modems*: Cheap, low-rate links (64kbps) for local 5km flights.
    *   *RFD900ux modems*: Long-range (40km) telemetry.
    *   *Microhard/Silvus high-rate IP radios*: Sized for video streams and companion data transfers (up to 15Mbps).

---

## 5. Companion Computers & Mission Autonomy

Onboard computers are integrated for autonomous processing:
*   **Raspberry Pi 4 Model B**: Sized for camera shutter sync and logging.
*   **NVIDIA Jetson Orin Nano / Orin NX**: Sized for high-rate AI processing, computer vision, and obstacle avoidance during BVLOS flights.
*   Companion computer selections are validated against flight controller interface compatibility (e.g. demanding Ethernet for high-bandwidth video streams).

---

## 6. Redundancy Strategy

Safety redundancy is enforced for long-range and cargo flights:
*   **IMU Redundancy**: Triple-redundant flight controllers vote on sensor telemetry (e.g., if one accelerometer fails, the other two override it automatically).
*   **Power Redundancy**: Dual BECs (Battery Eliminator Circuits) connect separate battery packs to the flight controller, protecting against primary BEC failure.
*   **GNSS Redundancy**: Dual GNSS receivers blend satellite counts to maintain lock.

---

## 7. Validation Assumptions

The validator (`AvionicsValidator`) asserts the following constraints:
*   **Airspeed Sensor Mandate**: Since fixed-wing aircraft depend on airspeed to avoid stalling, the absence of an airspeed sensor triggers a critical validation error.
*   **Navigation Redundancy**: GNSS module counts must satisfy redundancy constraints.
*   **Telemetry Range**: Sized telemetry modems must meet the mission range requirement.
*   **UART vs Ethernet Blockage**: Combining a high-rate companion computer (NVIDIA Jetson) with a serial-only flight controller (Matek H743) triggers a UART speed restriction warning.
*   **Thermal BEC Load**: Avionics power draws exceeding $15.0$ Watts trigger warnings to ensure BECs are fitted with heat-sinks.

---

## 8. Extension Mechanism

To add a new avionics strategy:
1.  Inherit from `BaseAvionicsStrategy` in `avionics_strategy.py`.
2.  Implement:
    *   `select_autopilot(requirements) -> Tuple[str, AutopilotFirmware]`.
    *   `select_navigation(requirements) -> Tuple[GNSSConfiguration, int]`.
    *   `get_communication_targets() -> Tuple[float, bool]`.
    *   `needs_companion_computer() -> Tuple[bool, bool]`.
    *   `get_recommendations() -> List[str]`.
3.  Register the strategy in the registry: `AvionicsStrategyRegistry.register("new_type", NewStrategy)`.
