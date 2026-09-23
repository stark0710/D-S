# Document Title

Engineering Parameter

Payload Center of Gravity

Document ID

MP-002-006

Version

1.0

Status

FROZEN

Project

Torq Wings Design Studio

Owner

Torq Wings Engineering Team

Purpose

Define the reusable Engineering Parameter "Payload Center of Gravity" for the Torq Wings Engineering Knowledge Base.

Payload Center of Gravity shall be referenced by Mission Categories and consumed by Engineering Engines.

---

## Overview

Payload Center of Gravity defines the location of the payload's mass center relative to the aircraft reference coordinate system.

It influences aircraft stability, controllability, structural loading, trim requirements, payload integration, and overall flight safety.

Payload Center of Gravity is a reusable Engineering Parameter.

Mission Categories shall reference this parameter using its permanent Parameter ID.

---

## Engineering Parameter Definition

| Field | Value |
| --- | --- |
| Parameter ID | MP-002-006 |
| Parameter Name | Payload Center of Gravity |
| Mission Parameter Group | MPG-002 Payload Parameters |
| Engineering Library | EPL-002 Payload Library |
| Description | Defines the location of the payload center of gravity relative to the aircraft reference coordinate system. |
| Engineering Purpose | Establishes payload mass distribution requirements used for stability analysis, structural design, aircraft sizing, payload integration, and flight dynamics. |
| Engineering Classification | EC-002 Mission-Specific |
| Data Type | Three-Dimensional Coordinate |
| Engineering Unit | • Primary: Millimetres (mm)<br>• Supported: Centimetres (cm), Metres (m) |

---

## Parameter Constraints

| Field | Value |
| --- | --- |
| Typical Value | Mission Dependent |
| Default Value | None |
| Minimum Value | Reference Coordinate Dependent |
| Maximum Value | Aircraft Geometry Dependent |
| Valid Range | Valid Aircraft Coordinate System |
| Mandatory | NO |
| Validation Rules | • Payload Center of Gravity shall be defined relative to the aircraft reference coordinate system.<br>• Coordinates shall be internally normalized to millimetres.<br>• Payload Center of Gravity shall remain within the allowable installation envelope. |

---

## Parameter Intelligence

| Field | Value |
| --- | --- |
| Inference Capability | Partially Inferable |
| Inference Source | • Payload Dimensions<br>• Payload Weight<br>• Aircraft Geometry<br>• Engineering Analysis |
| Engineering Consumers | • Mission Intelligence Engine<br>• Aircraft Sizing Engine<br>• Center of Gravity Analysis Engine<br>• Structural Design Engine<br>• Flight Dynamics Engine<br>• Platform Intelligence Engine |
| Dependencies | • Payload Weight<br>• Payload Dimensions<br>• Payload Mounting Method |
| Derived Parameters | • Aircraft Center of Gravity<br>• Static Stability Margin<br>• Trim Requirement<br>• Structural Load Distribution<br>• Payload Placement Recommendation |
| Engineering Impact | Critical |
| Priority Level | Critical |

---

## Engineering Traceability

| Field | Value |
| --- | --- |
| Engineering Source | • Engineering Analysis<br>• CAD Model<br>• Payload Database<br>• User Input |
| Engineering Confidence | Source Dependent |
| Evidence Level | EEL-005 Engineering Judgment |
| Evidence Source | Professional Aerospace Engineering Practice |
| Status | ACTIVE |
| Version | 1.0 |

---

## Engineering Notes

Payload Center of Gravity defines the location of the payload mass center only.

It does not represent the aircraft center of gravity.

Engineering Engines shall combine payload center of gravity with aircraft mass properties to determine the overall aircraft center of gravity.

---

## Engineering Principles

- Payload Center of Gravity shall remain platform independent.
- Payload Center of Gravity shall remain reusable across all Mission Domains.
- Payload Center of Gravity shall not assume any aircraft configuration.
- Mission Categories shall reference this Engineering Parameter rather than redefine it.

---

## Relationship to Other Parameters

**Related Engineering Parameters**

- MP-002-002 Payload Weight
- MP-002-003 Payload Dimensions
- MP-002-005 Payload Mounting Method
- MP-007-003 Structural Load Capacity
- MP-007-004 Aircraft Center of Gravity

---

## Implementation Status

| Field | Value |
| --- | --- |
| Engineering Parameter | Complete |
| Engineering Review | Approved |
| Repository Status | FROZEN |

Ready for use by Mission Categories and Engineering Engines.
