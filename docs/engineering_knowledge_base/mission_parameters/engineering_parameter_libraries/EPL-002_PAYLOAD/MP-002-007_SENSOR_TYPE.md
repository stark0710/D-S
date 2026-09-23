# Document Title

Engineering Parameter

Sensor Type

Document ID

MP-002-007

Version

1.0

Status

FROZEN

Project

Torq Wings Design Studio

Owner

Torq Wings Engineering Team

Purpose

Define the reusable Engineering Parameter "Sensor Type" for the Torq Wings Engineering Knowledge Base.

Sensor Type shall be referenced by Mission Categories and consumed by Engineering Engines.

---

## Overview

Sensor Type defines the primary sensing technology carried by the aircraft payload.

It influences mission capability, flight planning, payload integration, power consumption, data generation, communication requirements, onboard processing, and platform recommendation.

Sensor Type is a reusable Engineering Parameter.

Mission Categories shall reference this parameter using its permanent Parameter ID.

---

## Engineering Parameter Definition

| Field | Value |
| --- | --- |
| Parameter ID | MP-002-007 |
| Parameter Name | Sensor Type |
| Mission Parameter Group | MPG-002 Payload Parameters |
| Engineering Library | EPL-002 Payload Library |
| Description | Defines the sensing technology used by the payload during mission execution. |
| Engineering Purpose | Establishes sensor characteristics used for mission planning, aircraft sizing, payload integration, communication analysis, data management, and platform recommendation. |
| Engineering Classification | EC-002 Mission-Specific |
| Data Type | Enumeration |
| Engineering Unit | Not Applicable |

---

## Parameter Constraints

| Field | Value |
| --- | --- |
| Typical Value | Mission Dependent |
| Default Value | None |
| Allowed Values | • RGB Camera<br>• Thermal Camera<br>• Multispectral Camera<br>• Hyperspectral Camera<br>• LiDAR<br>• Radar<br>• Ultrasonic Sensor<br>• Gas Sensor<br>• Environmental Sensor<br>• Magnetometer<br>• Radiation Sensor<br>• Acoustic Sensor<br>• Communication Sensor<br>• Scientific Sensor<br>• Custom Sensor |
| Mandatory | NO |
| Validation Rules | • Sensor Type shall be selected from the approved engineering categories.<br>• Custom Sensor selections shall include an engineering description. |

---

## Parameter Intelligence

| Field | Value |
| --- | --- |
| Inference Capability | Partially Inferable |
| Inference Source | • Mission Category<br>• Mission Objective<br>• Payload Type<br>• User Input |
| Engineering Consumers | • Mission Intelligence Engine<br>• Payload Integration Engine<br>• Mission Planning Engine<br>• Platform Intelligence Engine<br>• Communication Analysis Engine<br>• AI Processing Engine |
| Dependencies | • Payload Type<br>• Mission Objective |
| Derived Parameters | • Camera Resolution<br>• Data Generation Rate<br>• Storage Requirement<br>• Communication Bandwidth<br>• Power Requirement |
| Engineering Impact | High |
| Priority Level | High |

---

## Engineering Traceability

| Field | Value |
| --- | --- |
| Engineering Source | • User Input<br>• Payload Database<br>• Manufacturer Specifications<br>• Engineering Analysis |
| Engineering Confidence | Source Dependent |
| Evidence Level | EEL-003 Industry Best Practice |
| Evidence Source | Manufacturer Technical Specifications |
| Status | ACTIVE |
| Version | 1.0 |

---

## Engineering Notes

Sensor Type identifies the sensing technology used by the payload.

It does not define sensor model, manufacturer, resolution, accuracy, field of view, spectral characteristics, or performance specifications.

Those characteristics shall be defined by separate Engineering Parameters.

---

## Engineering Principles

- Sensor Type shall remain platform independent.
- Sensor Type shall remain reusable across all Mission Domains.
- Sensor Type shall not reference commercial products or manufacturers.
- Mission Categories shall reference this Engineering Parameter rather than redefine it.

---

## Relationship to Other Parameters

**Related Engineering Parameters**

- MP-002-001 Payload Type
- MP-002-004 Payload Power Requirement
- MP-002-008 Camera Resolution
- MP-002-009 Payload Operating Mode
- MP-005-002 Communication Bandwidth

---

## Implementation Status

| Field | Value |
| --- | --- |
| Engineering Parameter | Complete |
| Engineering Review | Approved |
| Repository Status | FROZEN |

Ready for use by Mission Categories and Engineering Engines.
