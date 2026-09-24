# Fixed-Wing Fuselage Engineering Framework

## 1. Fuselage Engineering Philosophy

The **Fixed-Wing Fuselage Engineering Framework** designs and sizes the fuselage outer envelope and internal systems integration layout. By consuming results of preceding stages (`MissionResult`, `ConfigurationResult`, `WingResult`, `AirfoilResult`, `TailResult`), the framework acts as the central packaging coordinator:
*   It does **not** conduct detailed structural stress analysis.
*   Instead, it determines fuselage geometry, cross-sections, compartment bounds, landing gear and engine firewall mounting coordinates, internal component layouts, and cooling ventilation paths.

This ensures that all payload, battery, propulsion, and avionics systems are accommodated while maintaining stability and balance.

---

## 2. Internal Packaging Methodology

The framework sizes internal compartments based on safety clearance guidelines:
*   **Payload Bay**: Sized to fit the mission-specific payload package with standard side clearances (`profile.clearance_margin_m`).
*   **Battery Bay**: Sized based on estimated battery weight and width constraints.
*   **Avionics Bay**: Holds the flight controller, GPS, telemetry, and receivers.
*   **Volume Utilization**: Computes the volume ratio ($V_{\text{ratio}} = \frac{V_{\text{payload}} + V_{\text{battery}} + V_{\text{avionics}}}{V_{\text{total}}}$). High utilization ($>50\%$) triggers packaging density warnings due to thermal separation and accessibility limits.

---

## 3. Component Placement Strategy

Longitudinal positioning is calculated dynamically using a moments-balancing equation to align the Center of Gravity (CG) with the wing's center of pressure (typically 25% MAC):
$$\text{CG}_{\text{calculated}} = \frac{\sum m_i \cdot x_i}{\sum m_i}$$

*   **Tractor Configurations**: The heavy battery is placed slightly aft of the wing to offset the nose motor.
*   **Pusher Configurations**: The battery is placed far forward in the nose to counter the heavy rear pusher motor.
*   **Avionics placement**: Flight controllers are placed precisely at the target CG to minimize gyro acceleration offsets. GPS and receivers are placed aft or away from high-current battery and ESC wires to prevent electromagnetic interference (EMI).

---

## 4. Mounting Interfaces

Physical connection zones are determined based on layout selections:
*   **Wing Attachment**: Saddle mounts with fasteners or tube sleeves.
*   **Tail Boom Attachment**: Carbon tube boom clamps or direct rear bulkheads.
*   **Propulsion Firewall**: Carbon fiber or plywood front panels (Tractor) or rear cone bulkheads (Pusher).
*   **Landing Gear Blocks**: Spring steel plates or retract mounting blocks placed forward of CG (Taildragger) or aft of CG (Tricycle) to prevent tipping.

---

## 5. Cooling Considerations

Electronic Speed Controllers (ESCs) and batteries generate heat during high-power takeoff and climb phases:
*   Intake ducts are located in high-pressure nose zones.
*   Cooling airflow guides route air past the ESC and battery bay, venting through low-pressure tail vents.
*   Cramped packing densities ($>50\%$) trigger warnings to suggest duct area increases.

---

## 6. Validation Assumptions

The validator (`FuselageValidator`) asserts the following constraints:
*   **Aerodynamic blockages**: Sized fuselage width must not exceed the wing root chord ($c_{\text{root}}$) to prevent severe wing drag blockage.
*   **Tail booms compatibility**: Twin-boom structures must only be combined with compatible tail booms.
*   **Payload volumes**:Sized payload compartment volume must satisfy the constraint minimums.
*   **Thermal clearances**: Lack of ventilation ducts or excessively cramped packing volume ratios trigger safety warnings.

---

## 7. Extension Mechanism

To add a new fuselage strategy:
1.  Inherit from `BaseFuselageStrategy` in `fuselage_strategy.py`.
2.  Implement:
    *   `select_fuselage_type(requirements) -> FuselageType`.
    *   `get_typical_fineness_ratio() -> float`.
    *   `get_cross_section_type() -> str`.
    *   `get_recommendations(analysis) -> List[str]`.
3.  Register the strategy in the registry: `FuselageStrategyRegistry.register("new_type", NewStrategy)`.
