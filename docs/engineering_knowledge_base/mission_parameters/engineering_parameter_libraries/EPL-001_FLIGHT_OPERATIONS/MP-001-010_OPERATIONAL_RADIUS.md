# Document Title

Engineering Parameter

Operational Radius

Document ID

MP-001-010

Version

1.0

Status

FROZEN

Project

Torq Wings Design Studio

Owner

Torq Wings Engineering Team

Purpose

Define the reusable Engineering Parameter "Operational Radius" for the Torq Wings Engineering Knowledge Base.

Operational Radius shall be referenced by Mission Categories and consumed by Engineering Engines.

---

## Overview

Operational Radius defines the maximum horizontal distance between the mission operating area and the aircraft launch or recovery location during normal mission execution.

Operational Radius influences platform selection, endurance estimation, communication planning, mission feasibility, emergency recovery planning, and operational safety.

Operational Radius is a reusable Engineering Parameter.

Mission Categories shall reference this parameter using its permanent Parameter ID.

---

## Engineering Parameter Definition

| Field | Value |
| --- | --- |
| Parameter ID | MP-001-010 |
| Parameter Name | Operational Radius |
| Mission Parameter Group | MPG-001 Operational Parameters |
| Engineering Library | EPL-001 Flight Operations Library |
| Description | Defines the maximum horizontal operating distance between the aircraft and its launch or recovery location during mission execution. |
| Engineering Purpose | Establishes operational range requirements used for mission planning, communication analysis, endurance estimation, platform recommendation, and safety assessment. |
| Engineering Classification | EC-002 Mission-Specific |
| Data Type | Float |
| Engineering Unit | • Primary: Kilometres (km)<br>• Supported: Meters (m), Miles (mi), Nautical Miles (NM) |

---

## Parameter Constraints

| Field | Value |
| --- | --- |
| Typical Value | Mission Dependent |
| Default Value | None |
| Minimum Value | Greater than zero |
| Maximum Value | Mission Dependent |
| Valid Range | Positive Distance |
| Mandatory | NO |
| Validation Rules | • Operational Radius shall be greater than zero.<br>• Engineering calculations shall internally normalize all values into kilometres.<br>• Operational Radius shall satisfy mission safety and communication requirements. |

---

## Parameter Intelligence

| Field | Value |
| --- | --- |
| Inference Capability | Partially Inferable |
| Inference Source | • Mission Objective<br>• Mission Planning Data<br>• Area of Operation<br>• Coverage Area |
| Engineering Consumers | • Mission Intelligence Engine<br>• Platform Intelligence Engine<br>• Mission Planning Engine<br>• Communication Analysis Engine<br>• Battery Sizing Engine<br>• Safety Assessment Engine |
| Dependencies | • Area of Operation<br>• Coverage Area<br>• Mission Duration<br>• Communication Requirements |
| Derived Parameters | • Communication Link Requirement<br>• Battery Capacity<br>• Mission Feasibility<br>• Emergency Return Margin<br>• Estimated Flight Distance |
| Engineering Impact | Critical |
| Priority Level | High |

---

## Engineering Traceability

| Field | Value |
| --- | --- |
| Engineering Source | • Mission Planning Software<br>• User Input<br>• AI Inference<br>• Engineering Analysis |
| Engineering Confidence | Source Dependent |
| Evidence Level | EEL-005 Engineering Judgment |
| Evidence Source | Professional Aerospace Engineering Practice |
| Status | ACTIVE |
| Version | 1.0 |

---

## Engineering Notes

Operational Radius defines the maximum mission operating distance from the launch or recovery point.

Operational Radius is distinct from Area of Operation and Coverage Area.

Area of Operation defines the overall geographical boundary.

Coverage Area defines the portion of the mission requiring work.

Operational Radius defines how far the aircraft must safely travel from its operating base.

---

## Engineering Principles

- Operational Radius shall remain platform independent.
- Operational Radius shall remain reusable across all Mission Domains.
- Operational Radius shall not contain aircraft-specific assumptions.
- Mission Categories shall reference this Engineering Parameter rather than redefine it.

---

## Relationship to Other Parameters

**Related Engineering Parameters**

- MP-001-001 Area of Operation
- MP-001-004 Mission Duration
- MP-001-006 Coverage Area
- MP-001-007 Number of Sorties
- MP-005-001 Communication Range

---

## Implementation Status

| Field | Value |
| --- | --- |
| Engineering Parameter | Complete |
| Engineering Review | Approved |
| Repository Status | FROZEN |

Ready for use by Mission Categories and Engineering Engines.
