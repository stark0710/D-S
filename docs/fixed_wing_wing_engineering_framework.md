# Fixed-Wing Wing Engineering Framework

## 1. Wing Engineering Philosophy

The **Fixed-Wing Wing Engineering Framework** designs and sizes the primary lifting wing surface of the aircraft. By taking the `MissionResult` and `ConfigurationResult`, it establishes a clean boundary:
*   It does **not** select airfoils (which is handled in the next sprint).
*   Instead, it determines the macro wing dimensions: wingspan, wing planform area, aspect ratio, root and tip chords, sweep, dihedral, incidence, and Mean Aerodynamic Chord (MAC).

This translates abstract mission constraints (payload, range, stall speed targets) into a deterministic lifting surface geometry that matches structural weight limits and flight physics.

---

## 2. Planform Selection

The framework supports the following wing planform geometries:
*   **Rectangular**: Easiest to manufacture, docile stall behavior (stalls at root first, preserving aileron roll authority).
*   **Tapered / Trapezoidal**: Excellent compromise between structural efficiency (reduces tip bending moments and spar weight) and lift distribution.
*   **Elliptical**: Best aerodynamic efficiency (produces an ideal elliptical lift distribution with minimum induced drag). However, it is very complex to fabricate.
*   **Swept**: Used for higher speeds or to balance aircraft Center of Gravity (CG) locations.
*   **Delta**: Large sweep, low aspect ratio wing suitable for supersonic flight or compact structural configurations (such as tailsitters).
*   **Cranked / Custom**: Variable sweep or custom chords.

---

## 3. Wing Sizing Methodology

Wing area ($S$) sizing is driven directly by stall speed safety limits ($V_{\text{stall}}$) and dynamic pressure. The stall lift equation is:
$$V_{\text{stall}} = \sqrt{\frac{2 \cdot W}{\rho \cdot S \cdot C_{L,\text{max}}}}$$

Solving for maximum wing loading ($W/S$):
$$\left(\frac{W}{S}\right)_{\text{stall}} = \frac{1}{2} \cdot \rho \cdot V_{\text{stall}}^2 \cdot C_{L,\text{max}}$$

From this, the framework:
1.  Computes standard air density ($\rho$) at target cruise altitude.
2.  Assumes a conservative maximum wing lift coefficient ($C_{L,\text{max}} = 1.3$) for a clean wing.
3.  Calculates the required wing area:
    $$S = \frac{\text{MTOW}}{\left(\frac{W}{S}\right)_{\text{stall}}}$$
    Where MTOW is estimated from the mission constraints.
4.  Ensures that the wing loading does not exceed the strategy's operational limit.

---

## 4. Aspect Ratio Trade-Offs

The Aspect Ratio ($AR = b^2 / S$) represents a balance between aerodynamic efficiency and structural mass:
*   **High Aspect Ratio**: Minimizes induced drag ($C_{Di} = C_L^2 / (\pi \cdot e \cdot AR)$), which is critical for **Long Endurance** or glider configurations. However, it increases the root bending moment, leading to a heavier wing structure.
*   **Low Aspect Ratio**: Reduces the root bending moment, facilitating a lighter wing structure. It also increases roll rate, but increases induced drag, making it unsuitable for long-range cruise.

If the calculated wingspan ($b = \sqrt{S \cdot AR}$) exceeds the regulatory or transport limit (`constraints.max_wingspan_m`), the wingspan is capped, and the Aspect Ratio is re-adjusted:
$$AR_{\text{adjusted}} = \frac{b_{\text{max}}^2}{S}$$

---

## 5. Wing Loading

Wing loading ($W/S$, in kg/m²) dictates flight characteristics:
*   **Low Wing Loading**: Low stall speeds, docile takeoff and landings, excellent climb rates. However, it is highly sensitive to wind gusts and turbulence.
*   **High Wing Loading**: Stable cruise in turbulent air and smaller wing area (which reduces drag at high speed). However, it requires longer runways or high-energy launch systems due to elevated stall speeds.

---

## 6. Validation Assumptions

The validator (`WingValidator`) asserts the following constraints:
*   **Aero Limits**: Sized wing loading and aspect ratio must fall within `WingConstraints` bounds.
*   **Structural Feasibility**: Estimated wing structural weight (calculated using cantilever lift-load approximations) must not exceed 25% of the total MTOW.
*   **Configuration Compatibility**:
    *   *Twin Boom tail* configurations are structurally incompatible with Delta or Elliptical planforms.
    *   *Belly Landing* configurations must have a wing dihedral angle $\ge 1.0$ degree (preferably $\ge 2.0$ degrees) to prevent wingtip strikes.

---

## 7. Extension Mechanism

To add a new wing strategy:
1.  Inherit from `BaseWingStrategy` in `wing_strategy.py`.
2.  Implement:
    *   `get_target_aspect_ratio() -> float`.
    *   `get_typical_wing_loading_kg_m2() -> float`.
    *   `get_recommendations(geometry) -> List[str]`.
3.  Register the strategy in `wing_registry.py` under the name: `WingStrategyRegistry.register("new_type", NewStrategy)`.
