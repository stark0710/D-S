---
title: "Fixed-Wing UAV Engineering Report — SURVEY Mission"
author: "Torq Wings Design Studio"
date: "2026-09-21 16:30:15 UTC"
---

# Executive Summary

This engineering document describes the parametric sizing and configuration results for the Torq Wings fixed-wing UAV, optimized for 'SURVEY' operations.

Key metrics for the proposed design:
*   **Wingspan**: 2.00 meters
*   **Aspect Ratio**: 10.0
*   **Takeoff Mass**: 5.50 kg
*   **Production Cost Estimate**: 850.00 USD
*   **Verification Rating**: 90.0%
*   **Sizing Status**: Verified


---

# Mission Overview

The UAV design is governed by the following operational constraints:
*   **Category**: SURVEY
*   **Target Payload**: 2.00 kg
*   **Flight Time Limit**: 60.0 minutes
*   **Cruise Speed Target**: 95.0 km/h
*   **Stall Speed Boundary**: 45.0 km/h
*   **Launch & Recovery**: CATAPULT launch and PARACHUTE recovery.


---

# Configuration Layout

The layout selection process identified the following optimal structural configuration:
*   **Wing Placement**: High Wing
*   **Propulsion Layout**: Tractor
*   **Tail Assembly**: Conventional
*   **Landing Gear**: Tricycle

**Engineering Rationale**:
Rationale


---

# Geometry Sizing

### Wing Dimensions
*   **Wingspan**: 2.00 m
*   **Root Chord**: 0.25 m
*   **Tip Chord**: 0.15 m
*   **Reference Area**: 0.40 m^2
*   **Aspect Ratio**: 10.0
*   **Dihedral**: 2.0 deg

### Fuselage Outer Envelope
*   **Total Length**: 1.50 m
*   **Maximum Width**: 0.20 m
*   **Maximum Height**: 0.40 m

### Tail Stabilizers
*   **Configuration**: Conventional
*   **Horizontal stabilizer span**: 0.50 m
*   **Vertical fin height**: 0.40 m


---

# Propulsion Powertrain

The sized propulsion system has the following features:
*   **Power Unit**: SunnySky X2820
*   **Propeller**: 12x6 APC
*   **Static Thrust**: 35.00 N
*   **Thrust-to-Weight Ratio (T/W)**: 0.55
*   **Required Cruise Thrust**: 10.00 N
*   **Required Cruise Power**: 200.0 W
*   **Maximum Power**: 600.0 W
*   **Takeoff Acceleration Force**: 15.0 N
*   **Cruise Current Draw**: 15.0 A
*   **Estimated Cruise Throttle**: 50.0%


---

# Electrical & Power Distribution System

The onboard electrical power architecture is summarized below:
*   **Battery Pack Mass**: 3.50 kg
*   **Chemistry**: Lithium Polymer (LiPo)
*   **Specific Energy**: 200.0 Wh/kg
*   **Regulated Avionics Bus Voltage**: 5.0 V via continuous UBEC
*   **Power telemetry monitoring**: Sized airspeed & continuous BEC current links


---

# Onboard Avionics Systems

The flight control configuration consists of the following modules:
*   **Flight Controller Hardware**: Pixhawk 6C (firmware: ArduPilot)
*   **GPS/GNSS Module**: Standard GNSS
*   **RC Control Receiver**: ELRS
*   **Telemetry Data Link**: Sik Modem
*   **Continuous power BEC draw**: 8.0 W


---

# Payload Subsystem Integration

The sized cargo and sensor configurations include:
*   **Selected Sensor**: Sony RX1R II (RGB)
*   **Compartment Volume**: 200mm x 150mm x 150mm
*   **Orientation & Hatch**: Nadir Downward orientation via Bottom hatch.
*   **Mount Type**: Rigid floor plate with vibration damping via Grommets.


---

# Mass Properties & Weight Distribution

The aircraft weight breakdown is summarized below:
*   **Empty Structure weight**: 2.00 kg
*   **Battery weight**: 3.50 kg
*   **Useful Payload weight**: 5.50 kg
*   **Takeoff Mass (MTOW)**: 11.00 kg

### Center of Gravity & Inertia
*   **Center of Gravity (CG)**: X=0.576 m, Y=0.000 m, Z=-0.020 m (relative to nose)
*   **Moments of Inertia**: Ixx=0.200 kg*m^2, Iyy=0.180 kg*m^2, Izz=0.350 kg*m^2
*   **Static Pitch Stability Margin**: 18.0%


---

# Flight Performance

Aerodynamic flight envelope parameters are detailed below:
*   **Takeoff ground roll**: 25.0 meters
*   **Stall Speed**: 56.9 km/h (landing configuration: 49.5 km/h)
*   **Rate of Climb (ROC)**: 3.5 m/s
*   **Max Range**: 251.0 km
*   **Max Endurance**: 188.0 minutes
*   **Service Ceiling**: 2900 meters
*   **Maximum Turn G-Load**: 1.15 G


---

# Mission Verification & Compliance Checklist

The design was verified against required bounds:
*   **Compliance Score**: 90.0%
*   **Qualitative Risk Level**: Medium
*   **Risk Score**: 20.0
*   **Verification Status**: Verified

### Active Warnings / Mitigations:
*   No active verification warnings.


---

# Optimization Results

No optimization pass was executed for this design iteration. The aircraft was sized using direct analytical methods only.


---

# CAD Model Outputs

The parametric 3D CAD model was generated with the following characteristics:
*   **Generating Backend**: CadQuery
*   **Bounding Box**: 1.50 m × 2.00 m × 0.40 m (length × span × height)
*   **Total Solid Volume**: 0.15000 m³
*   **Assembly Components**: 3 parts positioned
*   **Generation Time**: 120.0 ms

### Exported File Formats
*   No CAD files were exported.


---

# Manufacturing Package

The production package was compiled with the following deliverables:
*   **BOM Items**: 1 line items
*   **Unit Cost Estimate**: 850.00 USD
*   **Engineering Drawings**: 1 sheets
*   **Assembly Guides**: 1 documents
*   **Fabrication Files**: 1 exports (3D Printing)
*   **QA Checklist Items**: 2


---

# Appendices

## A.1  Lift Equation Reference

The lift force at stall is given by:
    L = 0.5 × ρ × V² × S × CL_max

Where:
*   ρ = air density (kg/m³)
*   V = airspeed (m/s)
*   S = reference wing area (m²)
*   CL_max = maximum lift coefficient

## A.2  Drag Polar

    CD = CD0 + K × CL²

Where K = 1 / (π × AR × e) is the induced drag factor.

## A.3  Design Parameters Summary

*   Wing Reference Area S = 0.400 m²
*   Aspect Ratio AR = 10.0
*   Mean Aerodynamic Chord MAC = 0.220 m


---

