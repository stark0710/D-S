# Engineering Sizing & Build Package Report
## Multirotor Design Specification V1

This report summarizes the final convergent sizing evaluation for the multirotor UAV platform.

### Sizing Executive Summary
*   **Total Takeoff Weight (MTOW)**: 1.804 kg
*   **Empty Weight**: 0.874 kg
*   **Payload Capacity**: 0.50 kg
*   **Battery Pack Mass**: 0.430 kg
*   **Estimated Endurance**: 17.8 min
*   **Estimated Hover time**: 17.6 min
*   **Estimated Range**: 7.10 km
*   **Hover Throttle percentage**: 23.5%

### Bill of Materials Summary
| Category | Part Name | Qty | Unit Weight (kg) | Total Weight (kg) |
|---|---|---|---|---|
| Frame | Catalog Frame DJI F450 FlameWheel | 1 | 0.282 | 0.282 |
| Motor | T-Motor F40 PRO IV-1950 | 4 | 0.032 | 0.128 |
| Propeller | APC 10x4.7 MR | 4 | 0.015 | 0.060 |
| ESC | T-Motor Flame 60A Pro | 4 | 0.073 | 0.292 |
| Battery | Molicel 4200mAh 6S Li-Ion | 1 | 0.430 | 0.430 |
| Power Distribution | Generic PDB 4-in-1 ESC bus | 1 | 0.035 | 0.035 |
| Flight Controller | Holybro Holybro Pixhawk 6C | 1 | 0.048 | 0.048 |
| GPS | CubePilot Here3 GPS | 1 | 0.035 | 0.035 |
| Telemetry | Holybro Holybro 915MHz Telemetry | 1 | 0.025 | 0.025 |
| Receiver | FrSky FrSky Archer RS | 1 | 0.005 | 0.005 |
| Payload | User Specified Mission Payload (0.50 kg) | 1 | 0.500 | 0.500 |
| Wiring | Generic Wiring Silicone AWG AWG 20 Wiring Set | 1 | 0.045 | 0.045 |
| Connectors | Generic Connectors XT30 Battery/PDB connector set | 1 | 0.015 | 0.015 |
| Mounting Hardware | Generic M3 Standoffs and Carbon Screws Pack | 1 | 0.020 | 0.020 |

### System Layout Build Package
```text
============================================================
AIRCRAFT WIRING & CONNECTIONS BUILD PACKAGE
============================================================

1. POWER HARNESS CONNECTIONS:
   Battery (Molicel 4200mAh 6S Li-Ion)
     ↓ (XT30 Connector)
   Power Distribution Board (4-in-1 ESC bus)
     ↓ (AWG 8 Wire Leads)
   ESCs (Quantity 4 x T-Motor Flame 60A Pro)
     ↓ (AWG 8 Phase Wires)
   Motors (Quantity 4 x T-Motor F40 PRO IV-1950)

2. CONTROL SIGNAL CONNECTIONS:
   Flight Controller (Holybro Pixhawk 6C)
     ↓ (PWM Signal Channels 1-4)
   ESCs (Quantity 4 x T-Motor Flame 60A Pro)

3. AVIONICS ACCESSORIES CONNECTIONS:
   GPS Receiver (Here3 GPS) ── (I2C/Serial Port) ──> Flight Controller (Holybro Pixhawk 6C)
   Telemetry Radio (Holybro 915MHz Telemetry) ── (Telemetry Port 1) ──> Flight Controller (Holybro Pixhawk 6C)
   RC Receiver (FrSky Archer RS) ── (RCIN Port) ──> Flight Controller (Holybro Pixhawk 6C)

4. PAYLOAD INTEGRATION:
   Payload ── (12V BEC Port / AUX Channel) ──> Power Distribution Board (4-in-1 ESC bus)

============================================================
ASSEMBLY SEQUENCE INSTRUCTIONS:
1. Mount the motors to the frame arms using the pattern: 16x16mm.
2. Secure the propellers (APC 10x4.7 MR) only after verifying motor spin directions during autopilot calibration.
3. Solder the ESC branch wires to the center plate Power Distribution Board.
4. Mount the flight controller at the geometric center of gravity on vibration damping standoffs.
5. Calibrate the ESC throttle endpoints using the autopilot setup wizard.
============================================================

```
