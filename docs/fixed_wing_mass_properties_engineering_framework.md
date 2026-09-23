# Fixed-Wing Mass Properties & Center of Gravity Sizing Framework

## 1. Mass Properties Engineering Philosophy

The **Fixed-Wing Mass Properties & Center of Gravity Sizing Framework** aggregates every physical and structural subsystem (wing, fuselage, tail stabilizers, propulsion units, batteries, autopilot avionics, and mission payloads) to evaluate the mass properties of the aircraft. By executing this aggregation, the framework:
*   Enforces weight budgets and calculates payload-to-weight fractions.
*   Calculates center of gravity in three dimensions ($X, Y, Z$).
*   Estimates principal rolling, pitching, and yawing moments of inertia ($I_{xx}, I_{yy}, I_{zz}$).
*   Audits loading conditions and guarantees positive static stability margin limits.

This ensures that the sized aircraft remains controllable, stable, and structurally within bounds across all phases of flight.

---

## 2. Mass Estimation Methodology

Subsystem masses are aggregated dynamically:
*   **Wing Structure**: Sized based on the reference area:
    $$m_{\text{wing}} = S_{\text{area}} \times 2.8\text{ kg}$$
*   **Tail Structure**: Sized based on horizontal and vertical stabilizer surface areas.
*   **Fuselage Structure**: Sized as a function of the fuselage outer shell envelope:
    $$m_{\text{fuselage}} = l_{\text{fuselage}} \times 1.35\text{ kg}$$
*   **Propulsion/Avionics/Payloads**: Sourced from actual database weights (brushless motors, batteries, autopilots, and photogrammetry cameras).

---

## 3. Center of Gravity (CG) Methodology

The three-dimensional center of gravity is solved relative to the nose (longitudinal coordinate $X$) and the fuselage centerline (lateral $Y$ and vertical $Z$):
$$X_{\text{CG}} = \frac{\sum m_i \cdot x_i}{\sum m_i}$$

$$Y_{\text{CG}} = \frac{\sum m_i \cdot y_i}{\sum m_i}$$

$$Z_{\text{CG}} = \frac{\sum m_i \cdot z_i}{\sum m_i}$$

The framework balance service automatically optimizes the position of the heavy battery pack to counteract motor mounts (nose tractor vs rear pusher) and align the CG with the wing quarter-chord aerodynamic center.

---

## 4. Moments of Inertia Calculation

Principal moments of inertia ($I_{xx}, I_{yy}, I_{zz}$ in $\text{kg}\cdot\text{m}^2$) are computed relative to the centered CG coordinate axes using the parallel axis theorem on point-mass distributions:
$$I_{xx} = \sum m_i \cdot \left( \Delta y_i^2 + \Delta z_i^2 \right)$$

$$I_{yy} = \sum m_i \cdot \left( \Delta x_i^2 + \Delta z_i^2 \right)$$

$$I_{zz} = \sum m_i \cdot \left( \Delta x_i^2 + \Delta y_i^2 \right)$$

Where:
*   $\Delta x_i = x_i - X_{\text{CG}}$
*   $\Delta y_i = y_i - Y_{\text{CG}}$
*   $\Delta z_i = z_i - Z_{\text{CG}}$

---

## 5. Loading Analysis

The framework audits CG travel across the aircraft flight envelope:
*   **Empty Airframe**: Structural shell, wings, tail stabilizers, and propulsion (no payload or battery).
*   **Operational Empty**: Empty structure + battery installed (no cargo/sensors).
*   **Maximum Takeoff Weight (MTOW)**: Fully loaded takeoff state (battery + payload).
*   Sized CG travel limits must not exceed $10\%$ of MAC to protect control authority.

---

## 6. Static Stability Margins

Longitudinal static stability margins are calculated using Mean Aerodynamic Chord ($c_{\text{MAC}}$) and neutral point coordinates ($X_{\text{np}}$):
$$\text{Static Margin} = \frac{X_{\text{np}} - X_{\text{CG}}}{c_{\text{MAC}}}$$

Where:
*   $X_{\text{np}}$ is estimated as $25\%$ of MAC for Tailless flying wings and $42\%$ of MAC for Conventional tailed layouts (the horizontal stabilizer shifts the neutral point aft, increasing pitch stability).
*   Target margins are kept between $8\%$ and $22\%$ MAC to prevent pitch instability (too small) or excessive trim drag (too nose-heavy).

---

## 7. Validation Assumptions

The validator (`MassValidator`) asserts the following constraints:
*   **Takeoff Weight**: Calculated MTOW must not exceed constraints limits.
*   **Physical Bounds**: Calculated CG location must reside within the physical envelope of the fuselage shell.
*   **Stability Margin**: Static margin must meet or exceed target limits (minimum $8\%$, maximum $22\%$).
*   **CG Travel**: Sized loading state CG travel exceeding $10\%$ of MAC triggers warnings for autopilot trims.

---

## 8. Extension Mechanism

To add a new mass strategy:
1.  Inherit from `BaseMassStrategy` in `mass_strategy.py`.
2.  Implement:
    *   `get_target_fractions() -> Tuple[float, float, float]`.
    *   `get_target_static_margin() -> Tuple[float, float]`.
    *   `get_recommendations() -> List[str]`.
3.  Register the strategy in the registry: `MassStrategyRegistry.register("new_type", NewStrategy)`.
