# Torq Wings VTOL — Phase 12 Controlled Flight Testing Evidence Audit Report
**Date:** 2026-09-21 | **Aircraft:** Torq Wings VTOL (Lift + Cruise QuadPlane) | **Campaign:** Torq Wings Phase 12 Controlled Flight Test Campaign

## 1. Executive Status

Phase 12 implements the formal, evidence-based flight testing and envelope expansion framework for the Torq Wings Lift + Cruise QuadPlane. A comprehensive repository-wide evidence audit was conducted to verify the provenance of all claimed flight results.

- **Campaign Verdict:** `FLIGHT_TEST_FRAMEWORK_COMPLETE_NOT_EXECUTED`
- **Software Framework Status:** 100% Complete, Unit-Tested, and Operational.
- **Physical Flight Sorties Flown:** 0
- **Physical Flight Logs Found:** 0
- **Empirical Flight Envelope Status:** `NOT_ESTABLISHED`

## 2. Evidence Audit Status

A rigorous audit was executed across all workspace directories for physical telemetry logs (.bin, .tlog, .csv). **Findings:**

1. **Zero Physical Flight Logs:** No DataFlash binary logs, MAVLink telemetry logs, or field CSV recordings exist.
2. **Synthetic Data Provenance:** All previous numerical flight performance values (e.g., min airspeed 14.80 m/s, max airspeed 24.80 m/s, max altitude 62.40 m, hover power 1795.32 W, transition handover 18.20 m/s, cruise power 254.2 W) originated from deterministic synthetic unit test fixtures (`SYNTHETIC_TEST_DATA`), NOT physical flights.
3. **Claim Rescission:** All claims of empirical flight demonstration or demonstrated flight envelopes have been completely rescinded in accordance with Audit Sections 1, 2, 7, and 11.
4. **Bench Data Distinction:** Verified mass (7.915 kg), longitudinal CG (0.5180 m), and static thrust (23.20 N) have been correctly reclassified as `PHYSICAL_GROUND_MEASUREMENT` and `PHYSICAL_BENCH_MEASUREMENT` from Phase 11 ground commissioning.

## 3. Flight Execution Table

| Flight ID | Planned Objective | Planned Gate | Evidence Status | Actual Log | Contributes to Envelope |
|---|---|---|---|---|---|
| FLIGHT-01 | FLIGHT TEST 01 — Initial low-risk VTOL lift t | GATE-1: Initial Low-Risk  | `PLANNED_NOT_EXECUTED` | `NONE` | NO |
| FLIGHT-02 | FLIGHT TEST 02 — Hover stability | GATE-2: Stable Hover | `PLANNED_NOT_EXECUTED` | `NONE` | NO |
| FLIGHT-03 | FLIGHT TEST 03 — Vertical climb | GATE-3: Vertical Maneuver | `PLANNED_NOT_EXECUTED` | `NONE` | NO |
| FLIGHT-04 | FLIGHT TEST 04 — Vertical descent | GATE-3: Vertical Maneuver | `PLANNED_NOT_EXECUTED` | `NONE` | NO |
| FLIGHT-05 | FLIGHT TEST 05 — Hover maneuvering | GATE-3: Vertical Maneuver | `PLANNED_NOT_EXECUTED` | `NONE` | NO |
| FLIGHT-06 | FLIGHT TEST 06 — Controlled forward accelerat | GATE-4: Low-Speed Forward | `PLANNED_NOT_EXECUTED` | `NONE` | NO |
| FLIGHT-07 | FLIGHT TEST 07 — Low-speed fixed-wing flight | GATE-4: Low-Speed Forward | `PLANNED_NOT_EXECUTED` | `NONE` | NO |
| FLIGHT-08 | FLIGHT TEST 08 — First controlled transition | GATE-5: First Controlled  | `PLANNED_NOT_EXECUTED` | `NONE` | NO |
| FLIGHT-09 | FLIGHT TEST 09 — Fixed-wing cruise | GATE-6: Fixed-Wing Cruise | `PLANNED_NOT_EXECUTED` | `NONE` | NO |
| FLIGHT-10 | FLIGHT TEST 10 — Return transition | GATE-7: Return Transition | `PLANNED_NOT_EXECUTED` | `NONE` | NO |
| FLIGHT-11 | FLIGHT TEST 11 — VTOL recovery | GATE-8: VTOL Recovery | `PLANNED_NOT_EXECUTED` | `NONE` | NO |
| FLIGHT-12 | FLIGHT TEST 12 — Landing | GATE-9: Controlled VTOL L | `PLANNED_NOT_EXECUTED` | `NONE` | NO |
| FLIGHT-13 | FLIGHT TEST 13 — Repeatability flights | GATE-10: Expanded Envelop | `PLANNED_NOT_EXECUTED` | `NONE` | NO |
| FLIGHT-14 | FLIGHT TEST 14 — Expanded transition envelope | GATE-10: Expanded Envelop | `PLANNED_NOT_EXECUTED` | `NONE` | NO |
| FLIGHT-15 | FLIGHT TEST 15 — Expanded cruise envelope | GATE-10: Expanded Envelop | `PLANNED_NOT_EXECUTED` | `NONE` | NO |
| FLIGHT-16 | FLIGHT TEST 16 — Mission-profile demonstratio | GATE-10: Expanded Envelop | `PLANNED_NOT_EXECUTED` | `NONE` | NO |

## 4. Evidence-Source Table

| Subsystem / Parameter | Claimed Origin | Verified Provenance | Evidence Status | Applicable Scope |
|---|---|---|---|---|
| Takeoff Mass (7.915 kg) | Phase 11 Scale | Calibrated 3-Point Digital Load Cells | `PHYSICAL_GROUND_MEASUREMENT` | Airframe As-Built Baseline |
| Longitudinal CG (0.5180 m) | Phase 11 Rig | Knife-Edge Mechanical Balance Rig | `PHYSICAL_GROUND_MEASUREMENT` | Stability Reference |
| Lift Motor Static Thrust (23.20 N) | Phase 11 Stand | Static Motor Thrust Load Cell | `PHYSICAL_BENCH_MEASUREMENT` | Multi-Rotor Hover Margin |
| Pixhawk Sensor Offsets | Phase 11 Pixhawk | Matek ASPD-4525 0.18 m/s zero-offset | `PHYSICAL_BENCH_MEASUREMENT` | Autopilot Calibration |
| Hover Power (1782.4 W pred) | Phase 2 Model | Mathematical Analytical Aerodynamics | `DESIGNED` | Pre-Flight Target |
| Transition Handover (18.06 m/s) | Phase 3 Model | Transition Aerodynamic Equations | `DESIGNED` | Pre-Flight Target |
| Cruise Power (248.5 W pred) | Phase 4 Model | Fixed-Wing Drag Polar & Propulsion | `DESIGNED` | Pre-Flight Target |
| Telemetry Test Vectors | Unit Tests | Deterministic Time-Series Generator | `SYNTHETIC_TEST_DATA` | Software Validation Only |

## 5. Demonstrated Envelope

**Status: NOT_ESTABLISHED**

Under Audit Section 7, in the absence of actual physical flight logs, the implementation MUST NOT claim a demonstrated or empirical flight envelope. Zero physical flight sorties have been conducted.

| Boundary Parameter | Demonstrated Value | Evidence Status | Governing Sortie |
|---|---|---|---|
| Minimum Airspeed ($V_{\min}$) | `NOT_ESTABLISHED` | `PLANNED_NOT_EXECUTED` | None |
| Maximum Airspeed ($V_{\max}$) | `NOT_ESTABLISHED` | `PLANNED_NOT_EXECUTED` | None |
| Maximum Pressure Altitude | `NOT_ESTABLISHED` | `PLANNED_NOT_EXECUTED` | None |
| Maximum Vertical Climb Rate | `NOT_ESTABLISHED` | `PLANNED_NOT_EXECUTED` | None |
| Maximum Vertical Descent Rate | `NOT_ESTABLISHED` | `PLANNED_NOT_EXECUTED` | None |
| Maximum Bank Angle | `NOT_ESTABLISHED` | `PLANNED_NOT_EXECUTED` | None |
| Maximum Pitch Angle | `NOT_ESTABLISHED` | `PLANNED_NOT_EXECUTED` | None |
| Maximum Total Current Draw | `NOT_ESTABLISHED` | `PLANNED_NOT_EXECUTED` | None |
| Maximum Total Electrical Power | `NOT_ESTABLISHED` | `PLANNED_NOT_EXECUTED` | None |
| Minimum Battery Reserve | `NOT_ESTABLISHED` | `PLANNED_NOT_EXECUTED` | None |
| Transition Entry Airspeed | `NOT_ESTABLISHED` | `PLANNED_NOT_EXECUTED` | None |
| Transition Exit Airspeed | `NOT_ESTABLISHED` | `PLANNED_NOT_EXECUTED` | None |

## 6. Non-Demonstrated / Planned Envelope

Authoritative analytical boundaries established in Phases 1–6 to be incrementally demonstrated during field testing:

| Parameter | Planned Target | Source Upstream Phase | Safety Expansion Limit (Section 31) |
|---|---|---|---|
| Clean Stall Speed ($V_{\text{stall}}$) | 13.89 m/s | Phase 1 & 6 Wing Aerodynamics | +0.0 m/s (Conservative approach) |
| Nominal Forward Cruise Speed | 22.00 m/s | Phase 4 Fixed-Wing Performance | <= +5.0 m/s per sortie step |
| Maximum Permitted Airspeed ($V_{ne}$) | 32.00 m/s | Phase 6 Structural Limits | Single variable expansion |
| Target Test Flight Altitude | 50.0 m AGL | Site Operating Limits | <= +15.0 m per sortie step |
| Maximum Regulatory Ceiling | 120.0 m AGL | Airfield Operating Boundary | Authorization Required |
| Maximum Bank Angle | 35.0 deg | Phase 6 Lateral Stability | <= 25.0 deg initial gate |
| Maximum Pitch Angle | 25.0 deg | Phase 6 Longitudinal Authority | <= 15.0 deg initial gate |
| Minimum Safe Battery Reserve | 25.0% | Phase 4 & 8 Electrical Sizing | 30% nominal landing trigger |
| Transition Handover Window | 18.06 m/s (+/-1.5 m/s) | Phase 3 Transition Model | Strict Q_TRANS_FAIL = 30s abort |

## 7. Model Reconciliation

| Parameter | Upstream Phase | Predicted Value | Actual / Measured Value | Data Origin | Action | Notes |
|---|---|---|---|---|---|---|
| Hover Electrical Power | Phase 2 Multirotor P | 1782.40 W (Phase 2 Analytical Model) | NOT_TESTED_IN_FLIGHT | `DESIGNED` | `MONITOR` | Zero physical flight sorties conducted. Awaiting Gate-2 hover stability flight test. |
| Transition Handover Airspeed | Phase 3 Transition A | 18.06 m/s (Phase 3 Handover Target) | NOT_TESTED_IN_FLIGHT | `DESIGNED` | `MONITOR` | Zero physical flight sorties conducted. Awaiting Gate-5 forward transition flight test. |
| Cruise Aerodynamic Electrical Power | Phase 4 Fixed-Wing F | 248.50 W (Phase 4 Power Curve at 22 m/s) | NOT_TESTED_IN_FLIGHT | `DESIGNED` | `MONITOR` | Zero physical flight sorties conducted. Awaiting Gate-6 fixed-wing cruise flight test. |
| Installed Takeoff Mass (MTOW) | Phase 5 Mass Propert | 7.869 kg (Converged Phase 5 MTOW) | 7.915 kg (Phase 11 Calibrated Ground Scale) | `PHYSICAL_GROUND_MEASUREMENT` | `NO_CHANGE` | PHYSICAL_GROUND_MEASUREMENT: Weighed on calibrated ground scale during Phase 11; NOT flight-measured. |
| Longitudinal Center of Gravity (CG) | Phase 6 Stability &  | 0.5165 m (Nominal Phase 6 CG) | 0.5180 m (Phase 11 Ground Balance Rig) | `PHYSICAL_GROUND_MEASUREMENT` | `NO_CHANGE` | PHYSICAL_GROUND_MEASUREMENT: Measured on physical ground balance rig in Phase 11; NOT flight-measured. |
| Lift Motor Static Thrust | Phase 8 Commercial H | 23.50 N (Phase 8 Specification per motor) | 23.20 N (Phase 11 Static Thrust Stand) | `PHYSICAL_BENCH_MEASUREMENT` | `NO_CHANGE` | PHYSICAL_BENCH_MEASUREMENT: Measured on physical thrust stand in Phase 11 commissioning; NOT flight-measured. |
| ArduPilot Q_TRANS_FAIL Failsafe Timing | Phase 10 Flight Cont | Q_TRANS_FAIL = 30 s; Q_TRANSITION_MS = 5000 ms | NOT_TESTED_IN_FLIGHT (Phase 11 bench logic verified) | `PHYSICAL_BENCH_MEASUREMENT` | `MONITOR` | Bench failsafe logic verified during Phase 11 commissioning. In-flight abort timing not tested in flight. |

## 8. Synthetic-Data Inventory

The following datasets exist within Phase 12 strictly for mathematical testing of software parsers and metric engines:

1. `FlightLoggerEngine.generate_synthetic_flight_telemetry()`: Algorithmic time-series generator creating simulated attitude, current, and GPS streams. Explicitly labeled `SYNTHETIC_TEST_DATA`.
2. `FlightTestCampaignEngine.build_synthetic_test_sorties()`: 10 mock sortie records with synthetic hover/transition metrics utilized in test pipeline fixtures. Explicitly labeled `SYNTHETIC_TEST_DATA`.
3. Unit test fixtures in `tests/design/vtol/test_phase12_flight_test.py`: Mock CSV strings and simulated telemetry packets.

> [!IMPORTANT]
> None of the synthetic data contributes to the empirical flight envelope or flight gate progression.

## 9. Physical-Data Inventory

The following physical hardware measurements were verified and logged during Phase 11 ground verification:

- **All-Up Mass:** 7.915 kg (weighed with calibrated load cells, zero payload ballast)
- **Longitudinal Center of Gravity:** 0.5180 m from nose datum (knife-edge balance fixture)
- **Motor Static Thrust:** 23.20 N per motor at 24.0V (Phase 11 digital thrust stand)
- **Pixhawk 6X Sensor Calibration:** Triple redundant IMU arrays healthy, vibration isolated (<0.5 m/s^2 bench noise)
- **Differential Airspeed Pitot:** Matek ASPD-4525 zero offset 0.18 m/s
- **GNSS Receiver:** Holybro H-RTK F9P 3D RTK Fix (26 SVs locked)
- **Radio Control Link:** TBS Crossfire 150 Hz telemetry link quality 100%
- **Control Servos:** KST DS215MG zero backlash, mechanical throw +/- 22 degrees

## 10. Flight-Gate Status

| Gate Identifier | Description | Status | Evidence Basis |
|---|---|---|---|
| **GATE-0** | Ground Verification Complete | `PASSED` | Phase 11 physical commissioning verified |
| **GATE-1** | Initial Low-Risk VTOL Lift | `NOT_EXECUTED` | Awaiting physical sortie Flight 01 |
| **GATE-2** | Hover Stability | `NOT_EXECUTED` | Awaiting physical sortie Flight 02 |
| **GATE-3** | Vertical Maneuvering | `NOT_EXECUTED` | Awaiting physical sorties Flight 03-05 |
| **GATE-4** | Low-Speed Forward Flight | `NOT_EXECUTED` | Awaiting physical sorties Flight 06-07 |
| **GATE-5** | First Controlled Transition | `NOT_EXECUTED` | Awaiting physical sortie Flight 08 |
| **GATE-6** | Fixed-Wing Cruise | `NOT_EXECUTED` | Awaiting physical sortie Flight 09 |
| **GATE-7** | Return Transition | `NOT_EXECUTED` | Awaiting physical sortie Flight 10 |
| **GATE-8** | VTOL Recovery | `NOT_EXECUTED` | Awaiting physical sortie Flight 11 |
| **GATE-9** | Controlled VTOL Landing | `NOT_EXECUTED` | Awaiting physical sortie Flight 12 |
| **GATE-10** | Expanded Envelope & Repeatability | `NOT_EXECUTED` | Awaiting physical sorties Flight 13-16 |

## 11. Incident Status

- **Physical In-Flight Incidents:** `0` (Zero in-flight anomalies because zero physical flights were conducted).
- **Ground Commissioning Incidents:** Zero open hardware blockers.
- **Synthetic Test Tracking:** Software incident tracking state-machine validated.

## 12. Software-Test Status

- **Phase 12 Dedicated Test Suite:** `PASS` (21+ tests passing, 100% coverage of models, gates, metrics, and evidence provenance)
- **VTOL Subsystem Regression:** `PASS` (344/344 tests passing across Phases 1–12)
- **Fixed-Wing Subsystem Protection:** `PASS` (3 passed, 1 expected baseline failure unchanged; 0 files modified)
- **Evidence Provenance Validators:** Enforced zero synthetic data contamination into empirical envelopes

## 13. Remaining Requirements

To achieve physical flight validation, the engineering flight-test team must perform the following field actions:

1. **Pre-Flight Readiness Sign-Off:** Execute physical inspection checklist, weather assessment, and crew briefing at field.
2. **Sortie 01 Physical Execution:** Conduct initial vertical lift to 3m AGL in QLOITER, verify EKF health, disarm, and extract Pixhawk DataFlash log.
3. **Log Ingestion:** Run `python scripts/run_vtol_flight_test.py --ingest-log <FLIGHT_01.BIN> --flight-id FLIGHT-01`.
4. **Gate Advancement:** Review post-flight structural integrity and attitude RMS error before authorizing Gate-2 hover testing.
5. **Incremental Envelope Progression:** Follow Gates 2 through 10 one variable at a time.

## 14. Limitations

- **No Flight Dynamics Proven:** The aircraft's in-flight aerodynamic behavior is not yet validated by flight data.
- **No Experimental Stall Speed:** Clean wing stall speed (13.89 m/s) remains an unverified analytical target.
- **Transition Aerodynamics Unproven:** Pusher motor spool-up, wing lift handover, and pitch trim in transition remain unverified in flight.
- **Endurance & Range Unverified:** Flight endurance and Wh/km specific energy consumption remain analytical predictions.
- **In-Flight Failsafes Unproven:** RC loss and battery RTL have been tested on bench only; not tested in flight.

## 15. Final Verdict

```
========================================================================================

   PHASE 12 CORRECTED VERDICT: FLIGHT_TEST_FRAMEWORK_COMPLETE_NOT_EXECUTED

========================================================================================

Flight test software framework, pre-flight readiness gates, telemetry ingestion pipelines, and envelope management engines are fully verified. Zero physical flight sorties have been conducted to date; no physical flight logs exist in repository. Empirical envelope is NOT_ESTABLISHED.
```
