# VTOL Fuselage Engineering Framework

## 1. Fuselage Engineering Philosophy

The **VTOL Fuselage Engineering Framework** designs and sizes the primary fuselage structure and internal packaging layout for VTOL aircraft. It takes the `MissionResult`, `ConfigurationResult`, `WingResult`, `AirfoilResult`, and `TailResult` to establish the internal compartmental boundaries:
*   It does **not** design lifting wings or stabilizers (which are handled in their respective stages).
*   Instead, it determines the fuselage geometry (length, width, height), compartmental layout (battery, payload, and avionics bays), structural construction type (monocoque composite overlays), mounting reinforcements (wing attachments, tail boom sleeves, landing gears), and thermal cooling pathways.

This translates mission requirements into a structurally efficient, crashworthy, and aerodynamically clean fuselage shell that houses all critical electronics and payloads.

---

## 2. Supported Fuselage Types

The framework supports layout combinations across the primary VTOL families:
*   **Pod-and-Boom**: Short, compact central pod for payload/avionics, connected to a thin tail boom holding the tail assembly. Aerodynamically efficient and lightweight.
*   **Box Fuselage**: Rectangular cross sections optimized for boxy cargo packing and ease of mechanical load operations.
*   **Composite Shell Monocoque**: Highly streamlined circular/oval monocoque carbon shells designed for minimum wetted drag and maximum strength.
*   **Modular**: Segmented fuselage parts allowing simple payload swaps or multi-mission research pods.

---

## 3. Compartment Layout & Packaging Methodology

The fuselage is divided into three core compartmental bays:
*   **Battery Bay**: Typically occupies 30% to 60% of the volume. Placed close to the wing main spar to align battery mass centroids with the wing aerodynamic center, keeping CG travel neutral.
*   **Payload Bay**: Placed forward (for survey/mapping camera gimbals) or centered (for cargo containers) with quick-access hatches.
*   **Avionics Bay**: Located in low-EMF zones to isolate autopilot IMUs from high-current power routing lines.

---

## 4. Cooling Layout & Thermal Strategy

Power routing for hover vertical lift draws high currents, causing severe thermal loads in the batteries and ESCs. The cooling layout sizes:
*   **NACA Intake Ducts**: Surface intakes feeding cooling airflow over internal heat sinks during forward flight.
*   **Active Fan Ventilation**: Auto-triggered dynamic fan cooling for stationary hover segments.

---

## 5. Subsystem & Structural Interfaces

The framework defines load paths for pylon boom sleeves, landing gears, and wing box attachments:
*   **Wing joint**: Reinforced bulkhead interfaces secured by dual-bolt metal clevis attachments.
*   **Boom attachments**: Carbon sleeves and clamping ring collars distributing vertical thrust load paths to the fuselage.
*   **Landing gear tracks**: Skids or tricycle wheels hardpoints bolted to reinforced structural ribs.

---

## 6. Validation Assumptions

The validator (`FuselageValidator`) asserts the following boundaries:
*   **Volumetric Utility**: Sum of all internal subsystem volumes must not exceed 95% of the total fuselage volume to ensure physical assembly feasibility.
*   **Static CG Margin**: Sized center-of-gravity offset ($X_{\text{cg}}$) must not travel beyond the maximum target percentage of wing Mean Aerodynamic Chord (MAC).
*   **Duct Intakes**: Total cooling inlet surface area must be positive to ensure thermal dissipation adequacy.

---

## 7. Extension Mechanism

To add a new fuselage strategy:
1.  Inherit from `BaseFuselageStrategy` in `fuselage_strategy.py`.
2.  Implement the required attributes:
    *   `category`: `VTOLMissionCategory`
    *   `default_fuselage_type`: `str`
    *   `default_shape`: `str`
    *   `get_compartment_shares() -> Dict[str, float]`
    *   `get_recommendations() -> List[str]`
3.  Register the strategy in the registry: `VTOLFuselageStrategyRegistry.register(category, strategy_instance)`.
