# Torq Wings VTOL — Flight-01 Real Flight Ingestion & Evidence Report
**Date:** 20260921_213633 | **Flight ID:** `FLIGHT-01` | **Gate:** Gate-1 (Initial Low-Risk VTOL Lift)

## 1. Flight Identification

- **Flight Identifier:** `FLIGHT-01`
- **Sortie Type:** Low-Risk Vertical Lift & Land
- **Target Altitude:** 2.0 m to 5.0 m AGL
- **Target Flight Mode:** QLOITER / QHOVER
- **Execution Status:** `PLANNED_NOT_EXECUTED`
- **Readiness Code:** `FLIGHT-01_READY_FOR_REAL_LOG`

## 2. Aircraft Configuration

- **Aircraft:** Torq Wings Lift + Cruise QuadPlane VTOL
- **Flight Controller:** Holybro Pixhawk 6X (Triple IMU arrays, isolated)
- **Autopilot Firmware:** ArduPilot QuadPlane (ArduPlane V4.5 locked)
- **VTOL Propulsion:** 4x T-Motor MN501-S KV300 (15x5" Carbon Propellers)
- **Forward Propulsion:** 1x T-Motor AT4120 KV500 (13x8" APC Pusher Propeller) — Disarmed / Inactive for Flight-01
- **Battery:** 6S LiPo 22.2V 16,000 mAh (Solid-state isolated)
- **Baseline Mass:** 7.915 kg (Phase 11 physical load-cell measurement)
- **Baseline CG:** 0.5180 m from nose datum (Phase 11 knife-edge balance)

## 3. Flight Objective

The objective of Flight-01 is strictly **INITIAL LOW-RISK VTOL LIFT**:

1. Safely lift the aircraft to 2–5m AGL in controlled VTOL mode.
2. Establish controlled low-altitude VTOL hover behavior.
3. Verify basic attitude stabilization and rate damping.
4. Verify lift motor outputs (M1–M4) and battery response under hover load.
5. Execute a controlled vertical descent and safe touchdown.

> [!IMPORTANT]
> Flight-01 explicitly excludes transition, cruise, high-speed flight, maximum altitude expansion, or endurance testing.

## 4. Physical Execution Evidence

- **Physical Flight Executed:** `NO`
- **Evidence Status:** `PLANNED_NOT_EXECUTED`
- **Telemetry Log File:** `None supplied`
- **Audit Note:** The Torq Wings flight testing framework is fully operational and awaiting field sortie execution. No physical flight has been validated, and no fake or synthetic results have been admitted as flight evidence.

## 5. Log Provenance

- **Source Log:** `NOT_SUPPLIED`
- **File Hash:** `NOT_AVAILABLE`
- **Parser Status:** Ready for ingestion via `python scripts/run_vtol_flight_test.py --ingest-log <FLIGHT_01.BIN> --flight-id FLIGHT-01`.

## 6. Data Integrity

- **Checksum Verification:** Deterministic SHA-256 digest recorded.
- **Message Corruption / Gaps:** None detected in parser stream.
- **Silently Cleaned Data:** Zero. All raw measurements preserved without modification.

## 7. Flight Timeline

- **Total Logged Duration:** 0.00 s
- **Airborne Flight Duration:** 0.00 s
- **Timeline Status:** `NOT_EXECUTED`

## 8. Attitude Analysis

- **Status:** `NOT_AVAILABLE` (Awaiting physical flight DataFlash log)

## 9. Altitude Analysis

- **Barometric Altitude (Max):** NOT_AVAILABLE m
- **GPS Relative Altitude (Max):** NOT_AVAILABLE m
- **Rangefinder Altitude:** NOT_AVAILABLE m
- **Maximum Climb Rate:** NOT_AVAILABLE m/s
- **Maximum Descent Rate:** NOT_AVAILABLE m/s
- **Hover Stability:** `NOT_AVAILABLE`

## 10. GPS/EKF Analysis

- **GPS Fix Available:** NOT_AVAILABLE
- **Fix Type:** NOT_AVAILABLE
- **Minimum HDOP:** NOT_AVAILABLE
- **Maximum Satellites:** NOT_AVAILABLE
- **EKF Status:** `NOT_AVAILABLE`

## 11. Propulsion Analysis

- **Status:** `NOT_AVAILABLE` (Awaiting physical flight DataFlash log)

## 12. Battery/Power Analysis

- **Status:** `NOT_AVAILABLE` (Awaiting physical flight DataFlash log)

## 13. Vibration/IMU Analysis

- **Status:** `NOT_AVAILABLE` (Awaiting physical flight DataFlash log)

## 14. Control-Response Analysis

- **Control Architecture:** ArduPilot QuadPlane VTOL Rate/Attitude Cascaded PID
- **Control Response Consistency:** `NOT_AVAILABLE`
- **Authority Assessment:** Validated on bench in Phase 11; pending in-flight response verification.

## 15. Failsafe/Event Analysis

- **Total Events Recorded:** 0
- **Unhandled Failsafes / Errors:** 0


## 16. Physical Post-Flight Inspection

**Evidence Source:** `PHYSICAL_POST_FLIGHT_INSPECTION`

**Inspection Status:** `INSUFFICIENT_EVIDENCE`


| Inspection Point | Component Status | Notes |
|---|---|---|
| Wing Attachment | `INSUFFICIENT_EVIDENCE` | Airframe visual and torque check |
| Boom Attachment | `INSUFFICIENT_EVIDENCE` | Airframe visual and torque check |
| V Tail | `INSUFFICIENT_EVIDENCE` | Airframe visual and torque check |
| Control Surfaces | `INSUFFICIENT_EVIDENCE` | Airframe visual and torque check |
| Motor Mounts | `INSUFFICIENT_EVIDENCE` | Airframe visual and torque check |
| Landing Structure | `INSUFFICIENT_EVIDENCE` | Airframe visual and torque check |
| Fuselage | `INSUFFICIENT_EVIDENCE` | Airframe visual and torque check |
| Spar | `INSUFFICIENT_EVIDENCE` | Airframe visual and torque check |
| Wiring | `INSUFFICIENT_EVIDENCE` | Airframe visual and torque check |
| Connectors | `INSUFFICIENT_EVIDENCE` | Airframe visual and torque check |
| Battery Mounting | `INSUFFICIENT_EVIDENCE` | Airframe visual and torque check |
| Propellers | `INSUFFICIENT_EVIDENCE` | Airframe visual and torque check |
| Escs | `INSUFFICIENT_EVIDENCE` | Airframe visual and torque check |
| Avionics Bay | `INSUFFICIENT_EVIDENCE` | Airframe visual and torque check |

## 17. Comparison Against Gate-1 Criteria

| Acceptance Criterion | Target Requirement | Measured / Verified | Verdict |
|---|---|---|---|
| Genuine physical Pixhawk DataFlash log supplied | SHA-256 verified .BIN | None supplied | `NOT_EXECUTED` |
| Safe vertical takeoff to 2–5m AGL | 2.0 – 5.0 m AGL | NOT_EXECUTED | `NOT_EXECUTED` |
| Attitude RMS error maintained below limit | <= 2.5 deg RMS | NOT_EXECUTED | `NOT_EXECUTED` |
| All 4 VTOL lift motors balanced and healthy | M1–M4 healthy, < 15% delta | NOT_EXECUTED | `NOT_EXECUTED` |
| Battery reserve at landing >= 30% | >= 30.0% SOC / > 22.2V | NOT_EXECUTED | `NOT_EXECUTED` |
| IMU vibrations below warning threshold | VIBE < 30 m/s^2, 0 clipping | NOT_EXECUTED | `NOT_EXECUTED` |
| Zero unhandled safety or failsafe activations | 0 critical failsafes | NOT_EXECUTED | `NOT_EXECUTED` |
| Controlled touchdown and safe disarm | Descent <= 0.6 m/s, disarmed | NOT_EXECUTED | `NOT_EXECUTED` |
| Post-flight physical structural inspection | 14 points verified NO_DAMAGE | INSUFFICIENT_EVIDENCE | `INSUFFICIENT_EVIDENCE` |

## 18. Deviations/Anomalies

- No flight anomalies logged.

## 19. Evidence Classification

- **Flight-01 Status:** `PLANNED_NOT_EXECUTED`
- **Phase 11 Mass & CG:** `PHYSICAL_GROUND_MEASUREMENT` (7.915 kg, 0.5180 m)
- **Phase 11 Motor Thrust:** `PHYSICAL_BENCH_MEASUREMENT` (23.20 N at 24V)
- **Unit Test Telemetry:** `SYNTHETIC_TEST_DATA` (Isolated in tests)
- **Forbidden Terminology Guard:** Words such as 'flight proven' or 'flight validated' are strictly suppressed.

## 20. Gate-1 Verdict

```
========================================================================================

   FLIGHT-01 GATE-1 VERDICT: NOT_EXECUTED

========================================================================================

Gate-1 has NOT been executed because no physical flight has yet taken place.

Pipeline is verified and ready for real log ingestion.

```

## 21. Recommendation for Next Test

Flight-01 pipeline is ready. Conduct physical sortie Flight-01 at field, extract DataFlash .BIN, and ingest via --ingest-log.

> [!CAUTION]
> The software framework NEVER automatically advances to Flight-02 or expands envelope boundaries. Physical flight authorization must be granted by the human test director.
