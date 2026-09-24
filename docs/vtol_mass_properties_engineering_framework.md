# VTOL Mass Properties & Center of Gravity Engineering Framework

## VTOL Mass Engineering Philosophy
Weight is the most critical constraint in vertical flight design. For a VTOL aircraft to hover safely, transition efficiently, and maintain high-speed cruise stability, the distribution of its structural, electrical, and payload masses must be sized with precision. The core values of the framework include:
1. **Rotor Symmetry**: Aligning the composite center of gravity as close as possible to the center of thrust of the vertical lifting rotors to minimize differential motor workloads.
2. **Dynamic Margin Compensation**: Sizing dynamic ballast layout adjustments (e.g. movable battery rails) to offset weight changes during cargo drops or multi-sensor switches.
3. **Weight growth control**: Actively enforcing margins (typically 10% weight growth buffer) to ensure downstream component additions do not cause structural or flight violations.

---

## Weight Budgeting Methodology
Every VTOL design sizes and tracks component categories:
- **Wing Structure**: Wing skins, ribs, spars, and motor mounting structural reinforcements.
- **Fuselage Structure**: Avionics bay housing, payload compartment, and structural landing gear frames.
- **Tail Structure**: Vertical and horizontal stabilizer weights.
- **Propulsion**: Sized ESCs, hover rotors, forward flight motor, and propellers.
- **Electrical/Power**: Sized primary lithium battery pack mass and wire harnesses.
- **Avionics**: Flight controllers, GPS, telemetry modems, companion computers, and sensors.
- **Payload**: Mission payload weights (gimbals, cameras, spray systems, delivery boxes).

---

## Center-of-Gravity (CG) Methodology
Longitudinal and lateral CG calculations are performed relative to coordinate datums (e.g., nose coordinate zero):
- **Empty CG**: base structure, propulsion, and electronics without payload.
- **takeoff CG**: fully loaded configuration ready for launch.
- **CG Shift**: delta shift tracking. The longitudinal shift is evaluated relative to the Mean Aerodynamic Chord (MAC) of the wing:
  $$\Delta X_{cg\_pct} = \frac{X_{cg\_composite} - X_{cg\_base}}{MAC} \times 100$$
- **Lateral Offset**: tracked to limit lateral torque loops ($Y_{cg} \approx 0.0$).

---

## Inertia Analysis
Moments of inertia ($I_{xx}, I_{yy}, I_{zz}$) and cross-products of inertia ($I_{xy}, I_{xz}, I_{yz}$) are estimated by treating major components as point masses distributed in the 3D aircraft envelope:
$$I_{xx} = \sum m_i(y_i^2 + z_i^2)$$
$$I_{yy} = \sum m_i(x_i^2 + z_i^2)$$
$$I_{zz} = \sum m_i(x_i^2 + y_i^2)$$
This provides a representative inertia tensor for attitude control loop tuning.

---

## Hover Balance & Transition Balance
- **Hover Balance**: Computes the offset distance between the composite CG and the geometric center of hover thrust. Perfect balance (alignment) minimizes roll/pitch motor adjustments.
- **Transition Balance**: Slices flight envelopes to ensure the neutral point (NP) lies behind the CG at all transition stages, maintaining longitudinal pitch stability.
- **Cruise Static Margin**: Enforces a positive static margin of at least 5.0% MAC during forward wing-borne flight.

---

## Validation Assumptions
The validator enforces:
- **Max takeoff weight limit**: takeoff weight (empty weight + payload) must be below MTOW constraints.
- **CG Envelope range**: longitudinal CG must lie between 15% and 35% of Mean Aerodynamic Chord (MAC).
- **Static margin limit**: cruise static margin must exceed 5%.
- **Lateral boundary limit**: lateral CG offset must not exceed 2 cm.

---

## Extension Mechanism
To extend the framework:
1. **Extend Sizing databases**: Add or edit component mass entries in `component_mass.py` to refine weight breakdowns.
2. **Add custom sizing strategies**: Implement the `MassStrategy` interface in `mass_strategy.py` and register it inside `mass_registry.py`.
