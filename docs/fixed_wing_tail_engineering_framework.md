# Fixed-Wing Tail (Empennage) Engineering Framework

## 1. Empennage Engineering Philosophy

The **Fixed-Wing Tail (Empennage) Engineering Framework** designs and sizes horizontal, vertical, and control surfaces for the aircraft. By taking the results of preceding stages (`MissionResult`, `ConfigurationResult`, `WingResult`, `AirfoilResult`), the framework implements a decoupled stability boundary:
*   It does **not** size the wing or modify fuselage dimensions.
*   Instead, it determines tail areas, aspect ratios, sweep, incidence, and elevator/rudder sizes while checking pitch and yaw control authority and trim stability.

This ensures that the sized empennage provides sufficient passive stability and flight control authority for all flight states.

---

## 2. Tail Sizing Methodology

Tail sizing is driven by the longitudinal tail arm ($l_t$) and target tail volume stability coefficients:

### Tail Arm Sizing
The tail arm $l_t$ represents the distance from the wing Mean Aerodynamic Chord (MAC) quarter-chord to the tail MAC quarter-chord:
*   For conventional boom configurations, it is estimated as:
    $$l_t = \text{default\_tail\_arm\_ratio} \times b$$
    Where $b$ is the wingspan.
*   For Flying Wings and Tailless configurations, $l_t = 0.0$ m.

### Stabilizer Area Sizing
The stabilizer reference areas are calculated directly from target volume coefficients:
*   **Horizontal Tail Area ($S_H$)**:
    $$S_H = \frac{V_H \cdot S \cdot c_{\text{MAC}}}{l_t}$$
*   **Vertical Tail Area ($S_V$)**:
    $$S_V = \frac{V_V \cdot S \cdot b}{l_t}$$
    Where $S$ is wing area, $b$ is wingspan, and $c_{\text{MAC}}$ is the wing MAC.

---

## 3. Tail Volume Coefficients

Tail volume coefficients ($V_H$ and $V_V$) are non-dimensional indicators of pitch and yaw stability:
*   **Horizontal Tail Volume ($V_H$)**: Indicates pitch stability. Typical values are $0.40$ to $0.65$. Higher values increase longitudinal stability and are necessary to counter Center of Gravity (CG) travel in cargo transport.
*   **Vertical Tail Volume ($V_V$)**: Indicates yaw stability and directional tracking. Typical values are $0.03$ to $0.05$. Higher values damp Dutch roll oscillations.

---

## 4. Control Surface Sizing

Elevator and rudder sizes are parameterized relative to their parent surfaces:
*   **Elevator**: Span is equal to horizontal tail span ($b_H$). Chord is sized using the elevator-to-tail chord ratio ($c_e / c_H$, typically 0.25 to 0.35).
*   **Rudder**: Height is equal to vertical fin height ($h_V$). Chord is sized using the rudder-to-fin chord ratio ($c_r / c_V$, typically 0.25 to 0.35).
*   Maximum deflection limits (typically $\pm 25^{\circ}$ for elevators, $\pm 30^{\circ}$ for rudders) are configured.

---

## 5. Tail Configuration Trade-Offs

Choosing an empennage configuration represents a balance of stability, control, and structure:
*   **Conventional**: Prediction-safe, aerodynamically standard, structurally simple. However, it places tail surfaces inside the wake of tractor propellers.
*   **T-Tail**: Elevator raised above wing wake and prop wash, reducing aerodynamic turbulence. However, it increases the structural bending moment on the vertical fin.
*   **V-Tail**: Combined stabilizer surfaces. Reduces wetted area and drag, but requires pitch/yaw control mixers and carries a risk of Dutch roll.
*   **Twin Boom**: Ideal for rear pusher propulsion layouts, providing high structural rigidity, but is complex to manufacture.
*   **Tailless / Flying Wing**: Minimal drag. Stability must be achieved aerodynamically (reflexed airfoils, tip sweep washout) rather than via tail volumes.

---

## 6. Validation Assumptions

The validator (`TailValidator`) asserts the following constraints:
*   **Stability Volume Bounds**: Volume coefficients must fall within `TailConstraints` limits (V_h $\in [0.3, 1.0]$, V_v $\in [0.02, 0.10]$).
*   **Layout Compatibility**:
    *   Tails configured as *Tailless* or *Flying Wing* must have horizontal and vertical areas set to $0.0$.
*   **Trim Matching**: High camber root airfoils with pitching moments $C_{m0} < -0.10$ require a horizontal tail volume $V_H \ge 0.45$ to ensure sufficient elevator trim authority.
*   **Structural Span Bounds**: Horizontal tail span must not exceed 60% of wing span to prevent excessive bending loads.

---

## 7. Extension Mechanism

To add a new tail strategy:
1.  Inherit from `BaseTailStrategy` in `tail_strategy.py`.
2.  Implement:
    *   `get_target_volume_coefficients() -> Tuple[float, float]`.
    *   `get_typical_aspect_ratios() -> Tuple[float, float]`.
    *   `get_control_surface_ratios() -> Tuple[float, float]`.
    *   `get_recommendations(analysis) -> List[str]`.
3.  Register the strategy in the registry: `TailStrategyRegistry.register("new_type", NewStrategy)`.
