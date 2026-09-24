# VTOL Forward Propulsion Engineering Framework

## 1. Forward Propulsion Philosophy

The **VTOL Forward Propulsion Engineering Framework** designs and sizes the propulsion system responsible for wing-borne cruise flight, climb gradients, and forward transition acceleration. It consumes preceding stage outputs (`MissionResult`, `ConfigurationResult`, `WingResult`, `AirfoilResult`, `TailResult`, `FuselageResult`, `LiftSystemResult`) and is responsible for:
*   Estimating aerodynamic drag force at cruise speed.
*   Sizing required electric cruise power.
*   Selecting optimal brushless cruise motors (Kv, power limits, current draws), props, and ESCs.
*   Mapping installation placements and thrust vectors.
*   Calculating dynamic climb rates and level flight maximum airspeed boundaries.

---

## 2. Aerodynamic Drag & Sizing Methodology

Total drag coefficient is sized as:
$$C_{D,\text{total}} = C_{d0,\text{wing}} + C_{Di} + C_{D0,\text{fuse}}$$

Where:
*   $C_{d0,\text{wing}}$ is the airfoil sectional cruise drag.
*   $C_{Di} = \frac{C_L^2}{\pi \cdot e \cdot AR}$ is the induced drag.
*   $C_{D0,\text{fuse}}$ is the bare fuselage drag.

Required cruise thrust balances this drag force:
$$T_{\text{required}} = \frac{1}{2} \cdot \rho \cdot V_{\text{cruise}}^2 \cdot S \cdot C_{D,\text{total}}$$

Required input electrical power is calculated as:
$$P_{\text{electrical}} = \frac{T_{\text{required}} \cdot V_{\text{cruise}}}{\eta_{\text{prop}} \cdot \eta_{\text{motor}}}$$
Where $\eta_{\text{prop}} = 0.70$ and $\eta_{\text{motor}} = 0.85$.

---

## 3. Propeller & ESC Sizing Methodology

*   **Propeller Selection**: Propellers are matched based on Kv ratings and diameters to avoid exceeding the available fuselage clearance margins.
*   **ESC Sizing**: Cruise ESCs are sized to support the motor's maximum current draw with at least a 20% safety margin:
    $$I_{\text{ESC, rating}} \ge 1.2 \cdot I_{\text{motor, max}}$$

---

## 4. Climb & Airspeed Performance

*   **Rate of Climb (RoC)**: Continuous climb performance is evaluated based on excess power available:
    $$\text{RoC} = \frac{P_{\text{available, mech}} - f_{\text{climb}} \cdot P_{\text{cruise, mech}}}{\text{MTOW} \cdot g}$$
*   **Maximum Airspeed**: Sized terminal level-flight speed is approximated based on power scaling:
    $$V_{\text{max}} = V_{\text{cruise}} \cdot \left(\frac{P_{\text{max, total}}}{P_{\text{cruise, required}}}\right)^{0.33}$$

---

## 5. Validation Assumptions

The validator (`ForwardPropulsionValidator`) asserts the following boundaries:
*   **Propeller clearance**: Propeller tips must not strike the side of the fuselage. Sized nacelle distance $Y_{\text{nacelle}} - R_{\text{prop}}$ must exceed $0.5 \cdot \text{width}_{\text{fuse}} + 0.01$.
*   **Climb Capability**: Rate of climb must exceed $1.5$ m/s to ensure safe transition climb gradients.
*   **ESC Sizing**: ESC continuous current ratings must support maximum motor power draws.

---

## 6. Extension Mechanism

To add a new cruise strategy:
1.  Inherit from `BaseCruiseStrategy` in `forward_propulsion_strategy.py`.
2.  Implement the required attributes:
    *   `category`: `VTOLMissionCategory`
    *   `default_propulsion_architecture`: `str`
    *   `default_climb_power_factor`: `float`
    *   `get_recommendations() -> List[str]`
3.  Register the strategy in the registry: `VTOLForwardPropulsionStrategyRegistry.register(category, strategy_instance)`.
