# VTOL Wing Engineering Framework

## 1. Wing Engineering Philosophy

The **VTOL Wing Engineering Framework** designs and sizes the primary lifting wing surface of VTOL aircraft. It takes the `MissionResult` and `ConfigurationResult` to establish the macro planform geometry:
*   It does **not** select airfoils (which is handled in the airfoil stage).
*   Instead, it determines the planform dimensions: wingspan, wing planform area, aspect ratio, root and tip chords, sweep, dihedral, incidence, and washout.
*   Crucially, for VTOL, it must also design **propulsion integration**: motor mounting locations, boom structures, pylon masses, and vectoring tilt servo mechanical demands.

The framework supports both fixed wing (e.g. QuadPlane, Lift + Cruise) and movable wing (e.g. Tilt Wing) architectures.

---

## 2. Wing Sizing Methodology

Wing area ($S$) sizing is driven directly by cruise wing loading ($W/S$) targets. In VTOL systems, stall speed during conventional takeoff/landing is bypassed by vertical takeoff, meaning the wing area is sized for **cruise flight efficiency** and **transition capture stability**:
$$S = \frac{\text{MTOW}}{\left(\frac{W}{S}\right)_{\text{target}}}$$

Once the area is solved, the wingspan ($b$) is calculated:
$$b = \sqrt{S \cdot AR}$$

Chords are solved using linear taper distributions:
$$c_{\text{root}} = \frac{2 \cdot S}{b \cdot (1 + \lambda)}$$
$$c_{\text{tip}} = \lambda \cdot c_{\text{root}}$$
Where $\lambda$ is the `taper_ratio`.

If the computed wingspan exceeds the transport or safety limits (`constraints.max_wingspan_m`), the span is capped at 5.5m and the Aspect Ratio is re-adjusted:
$$AR_{\text{adjusted}} = \frac{b_{\text{max}}^2}{S}$$

---

## 3. Hover and Cruise Load Cases

VTOL wings experience distinct structural load cases:
*   **Hover Loading**: The wing structure does not generate aerodynamic lift. Instead, wing booms must support the gravity and inertial shear loads of the vertical lift motors and pylons.
*   **Cruise Loading**: The aircraft flies wing-borne. The wing spars absorb conventional aerodynamic lift bending moments ($N_{\text{limit}} = 4.0$ G, $N_{\text{ultimate}} = 6.0$ G).
*   **Transition Loading**: During the transition phase, the wing is subjected to combined aerodynamic lift and vertical thrust torque vectors. The peak transition bending moment at the wing root is estimated as:
    $$M_{\text{bending, transition}} = \left(\frac{\text{MTOW} \cdot g}{2}\right) \cdot \left(\frac{b}{4}\right) \cdot f_{\text{dynamic}}$$

---

## 4. Motor Integration & Mounting

The framework translates configuration layouts into wing-mounted structural interfaces:
*   **Boom Clamps**: For dedicated lift motors (such as in QuadPlane or Lift+Cruise configurations), the engines are mounted on booms clamped under or over the wing spar.
*   **Tilt Pivots**: For tilt-rotor or tilt-wing configurations, the motor mounts house mechanical pivot tubes and tilt servos. The required tilt servo torque is evaluated based on MTOW.
*   **Mount coordinate validation**: Sized motor mount spanwise offsets ($Y_{\text{mount}}$) must not exceed the wing semi-span ($b/2.0$), preventing outboard overhangs.

---

## 5. Validation Assumptions

The validator (`WingValidator`) enforces the following boundaries:
*   **Geometric limits**: Wing loading must reside within `constraints.min_wing_loading_kg_m2` (10.0) and `constraints.max_wing_loading_kg_m2` (120.0). Aspect ratio must be between 5.0 and 18.0.
*   **Structural Stiffness**: Root chord must be strictly greater than tip chord to maintain torsional stiffness against motor thrust reactions.
*   **Configuration Match**: If the configuration is a `Tilt Wing` VTOL, the wing geometry type must be configured as `Tilt Wing` to allow rotation clearance.

---

## 6. Extension Mechanism

To add a new wing strategy:
1.  Inherit from `BaseWingStrategy` in `wing_strategy.py`.
2.  Implement the required attributes:
    *   `category`: `VTOLMissionCategory`
    *   `default_aspect_ratio`: `float`
    *   `default_wing_loading_kg_m2`: `float`
    *   `structural_concept`: `str`
    *   `default_wing_position`: `str` (e.g. High Wing, Low Wing)
    *   `get_recommendations(geometry) -> List[str]`
3.  Register the strategy in the registry: `VTOLWingStrategyRegistry.register(category, strategy_instance)`.
