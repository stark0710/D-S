# VTOL Airfoil Engineering Framework

## 1. Airfoil Engineering Philosophy

The **VTOL Airfoil Engineering Framework** selects, evaluates, and validates the cross-sectional profiles (airfoils) of the wing specifically for VTOL flight regimes. By consuming the outputs of preceding stages (`MissionResult`, `ConfigurationResult`, `WingResult`), it bridges macro geometry and micro aerodynamics across three distinct flight phases: hover, transition, and cruise.
*   It does **not** design the planform layout (wingspan, area, chord distribution), which is frozen in the preceding stage.
*   Instead, it determines the aerodynamic profile: selecting the best candidate airfoil, establishing thickness ratios, camber lines, and leading edge radii, and assessing how the wing section behaves when subjected to rotor downwash and propeller slipstream velocities.

This ensures that the wing produces the required lift coefficient ($C_L$) at cruise altitude with minimal drag, handles flow attachment during transition angles of attack, and accommodates internal carbon spars.

---

## 2. Selection Methodology

Airfoil selection is driven by the mission category and structural constraints through the `AirfoilSelector` and matching strategies:
*   **Long Endurance**: High aspect ratio wings require thin, low-drag, laminar flow profiles (e.g., `MH 32` or `RG 15`) to maximize $L/D$ ratios during wing-borne cruise.
*   **Cargo / Heavy Lift**: Heavy payload transporters require thick, highly cambered, high-lift profiles (e.g., `Selig S1223` or `NACA 4412`) to generate maximum lift coefficients ($C_{L,\text{max}} \ge 1.8$).
*   **Survey / Mapping**: Stable scanning flights use stable cambered profiles (e.g., `Clark Y` or `NACA 4412`) to preserve steady camera paths and predictable stall characteristics.
*   **Military / Speed**: Symmetrical profiles (e.g., `NACA 0012`) or low drag reflexed profiles (e.g., `MH 45`) are used to optimize high-speed transition dynamics and lower radar profiles.

---

## 3. Polar Analysis

Aerodynamic coefficient evaluation is performed by parabolic drag curve approximations:
$$C_d = C_{d0} + K \cdot (C_l - C_{l,\text{opt}})^2$$

Where:
*   $C_{d0}$ is the zero-lift drag coefficient.
*   $K$ is the drag polar curvature constant.
*   $C_{l,\text{opt}}$ is the lift coefficient at minimum drag (typically scaling with camber).

### Propeller Slipstream Interaction
For configurations where forward traction propellers or tilting rotors wash over the wing surface, the local dynamic pressure $q_s$ is scaled:
$$q_s = q_\infty \cdot f_{\text{slipstream}}$$
The required local lift coefficient in the slipstream is reduced, leading to corrected local sectional drag coefficients:
$$C_{l,\text{corrected}} = \frac{C_{l,\text{cruise}}}{f_{\text{slipstream}}}$$
$$C_d = C_{d0} + K \cdot (C_{l,\text{corrected}} - C_{l,\text{opt}})^2$$

---

## 4. Transition Aerodynamics & Rotor Downwash

Transition represents the most complex aerodynamic regime where angles of attack sweep from 0 to 90 degrees:
*   **Flow Detachment**: Evaluated as $\alpha_{\text{detachment}} = 15.0 + 100 \cdot \text{camber}$. Beyond this angle, the boundary layer separates and bluff body drag coefficients ($C_d \approx 1.12$) are applied.
*   **Rotor Downwash**: Hovering rotors push a high-velocity vertical downwash plume over the wing. The downwash velocity is estimated using actuator disk theory:
    $$v_{\text{downwash}} = 4.5 \cdot \sqrt{\frac{\text{MTOW}}{10}}$$
    This vertical velocity vector deflects the effective freestream angle of attack during transition:
    $$\Delta\alpha_{\text{downwash}} = \arctan\left(\frac{v_{\text{downwash}}}{V_{\text{cruise}}}\right)$$

---

## 5. Validation Assumptions

The validator (`AirfoilValidator`) enforces the following boundaries:
*   **Structural Feasibility**: Sized wing root thickness ($C_{\text{root}} \times t_{\text{ratio}}$) must exceed the minimum spar outer diameter ($15$ mm) to accommodate carbon joiners.
*   **Aerodynamic Stability**: Absolute zero-lift pitching moments ($C_{m0}$) must not exceed $0.15$ to avoid oversized horizontal tail surfaces and high trim drag.
*   **Glide Efficiency**: Sectional lift-to-drag ($L/D$) ratios must exceed $10.0$ for all cruise configurations.

---

## 6. Extension Mechanism

To add a new airfoil strategy:
1.  Inherit from `BaseAirfoilStrategy` in `airfoil_strategy.py`.
2.  Implement the required attributes:
    *   `category`: `VTOLMissionCategory`
    *   `preferred_candidates`: `List[str]`
    *   `target_cl`: `float`
    *   `get_recommendations(airfoil_name) -> List[str]`
3.  Register the strategy in the registry: `VTOLAirfoilStrategyRegistry.register(category, strategy_instance)`.
