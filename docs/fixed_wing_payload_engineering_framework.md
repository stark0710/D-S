# Fixed-Wing Payload Integration Engineering Framework

## 1. Payload Engineering Philosophy

The **Fixed-Wing Payload Integration Engineering Framework** manages the physical, electrical, and thermal packaging of mission-critical hardware (e.g. RGB mapping cameras, multispectral cameras, LiDAR sensors, thermal imagers, cargo boxes) inside the aircraft. Consuming preceding framework results, it implements a decoupled integration model:
*   It does **not** perform payload data processing, photogrammetry stitching, or sensor computer vision analysis.
*   Instead, it determines payload selection, sizing coordinates ($X$-placement), mounting styles, electrical BEC configurations, cooling vents, and center-of-gravity ($CG$) shift boundaries.

This ensures that the integrated payload system is structural, thermal, and aerodynamically compatible.

---

## 2. Payload Integration Methodology

Integration resolves the conflict between camera viewpoints and airframe stability:
*   **Coordinate Placement**: To prevent severe aerodynamic trim issues, the engine places the payload exactly adjacent to the wing center of pressure or quarter-chord aerodynamic center:
    $$X_{\text{payload}} = X_{\text{quarter\_chord}} - 0.015\text{ m}$$
*   ** Fuselage Bay Matching**: Sized dimensions (length, width, height) are audited against the fuselage payload compartment bay. Excessive volumetric utilization ($>80\%$) triggers accessibility warnings.

---

## 3. Mounting & Vibration Strategies

Sensors must be isolated from structural engines/motors frequencies:
*   **Rigid Plate Mounts**: Standard floor mounts fitted with compression rubber grommets or silicon bushings to isolate high-frequency airframe motor noise.
*   **Active Gimbal Mounts**: 2-axis or 3-axis stabilized gimbals with active servos to maintain nadir (downward) or forward orientations during aircraft banking maneuvers.
*   **Foam Cavities**: Lightweight, structural cavities with quick-release lock brackets to hold cargo boxes secure.

---

## 4. Power & Communication Interfaces

Power and data routes are mapped according to load requirements:
*   **Power Interfaces**:
    *   *Low-power sensors (<10W)*: Sized using standard 5.0V bus JST-GH plugs.
    *   *High-power sensors (>=10W)*: Sized using dedicated 12V voltage regulators (BECs) and locking XT30 connectors.
*   **Data Interfaces**:
    *   *Low-bandwidth links*: USB-C or UART serial connections.
    *   *High-bandwidth streams*: RJ45 Ethernet cables for video streams.
    *   *Camera Geotagging*: Integrated camera shutter triggering using Mavlink `CAMERA_FEEDBACK` protocols.

---

## 5. Thermal Considerations

Thermal dissipation checks are conducted to prevent sensor overheating inside closed carbon bays:
*   **Passive Heat-sinks**: Sized for low-draw sensors (<12W) conducting heat directly to structural metal plates.
*   **Forced Convection Scoops**: Sized for high-draw systems (>=12W) calculating intake duct scoop cross-sectional areas:
    $$\text{Area}_{\text{intake\_mm2}} = \text{Power}_{\text{payload}} \times 8.0 \times \text{Safety Factor}$$
    Airflow is routed through the payload compartment and exhausted near low-pressure areas of the tail cone.

---

## 6. Center of Gravity (CG) Impact

Longitudinal balance is audited by calculating the payload's weight contribution to empty CG:
$$CG_{\text{shift\_offset}} = \frac{m_{\text{payload}} \cdot \left(X_{\text{payload}} - CG_{\text{empty}}\right)}{m_{\text{total}}}$$

$$\text{Static Margin Impact} = \frac{CG_{\text{shift\_offset}}}{\text{MAC}} \times 100$$

Sized static margin shifts are validated against safety limits ($CG_{\text{shift}} \le 30$ mm). If the shift exceeds aerodynamic limits, the layout is flagged as unstable.

---

## 7. Validation Assumptions

The validator (`PayloadValidator`) asserts the following constraints:
*   **Weight compatibility**: Sized payload weight must not exceed structural capabilities.
*   **Volumetric fit**: Payload packaging volume must not exceed $90\%$ of fuselage payload bay compartments.
*   **Power limits**: Continuous electrical draw must not exceed constraints limits.
*   **CG shifts bounds**: Absolute CG shift offset must remain within aerodynamic margins ($<30$ mm).
*   **Cooling scoops**: Passively cooled payloads drawing $\ge 12.0$ Watts trigger warnings to add air scoops.

---

## 8. Extension Mechanism

To add a new payload strategy:
1.  Inherit from `BasePayloadStrategy` in `payload_strategy.py`.
2.  Implement:
    *   `select_payloads(requirements) -> List[PayloadType]`.
    *   `get_layout_guidelines() -> Tuple[str, str]`.
    *   `get_mount_style() -> str`.
    *   `get_recommendations() -> List[str]`.
3.  Register the strategy in the registry: `PayloadStrategyRegistry.register("new_type", NewStrategy)`.
