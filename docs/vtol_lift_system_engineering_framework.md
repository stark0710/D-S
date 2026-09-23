# VTOL Lift System Engineering Framework

## 1. Lift System Engineering Philosophy

The **VTOL Lift System Engineering Framework** designs and sizes the vertical propulsion components of a VTOL aircraft. It consumes preceding stages (`MissionResult`, `ConfigurationResult`, `WingResult`, `TailResult`, `FuselageResult`) and is responsible for:
*   Sizing required hover thrust margins ($T/W \ge 1.30$).
*   Selecting optimal brushless motors (KV, max thrust, current limits) and matching carbon fiber propellers.
*   Generating layout positioning and CW/CCW torque configurations.
*   Evaluating electrical draws, ESC currents, and battery C-rate discharge capability.
*   Providing failure redundancy checks for engine-out safe controllability.

---

## 2. Rotor Sizing & Hover Sizing Methodology

Thrust requirements are calculated relative to maximum takeoff weight (MTOW) under ISA sea level settings:
$$T_{\text{required}} = \text{MTOW} \cdot g \cdot f_{\text{safety}}$$

Where:
*   $f_{\text{safety}}$ is the target safety factor margin ($1.35$ to $1.65$) matching the selected strategy.

For coaxial configurations, downstream rotors operate in the slipstream of upstream rotors, leading to a lift degradation penalty:
$$T_{\text{available}} = N_{\text{rotors}} \cdot T_{\text{motor,max}} \cdot (1 - 0.5 \cdot \text{loss}_{\text{coaxial}})$$
Where $\text{loss}_{\text{coaxial}} = 0.15$ (15% lift loss).

---

## 3. Electrical Power & Battery Sizing

Total power consumption during hover is derived from propeller efficiency indices:
$$P_{\text{total}} = N_{\text{rotors}} \cdot \left( \frac{T_{\text{motor, hover}}}{\text{hover\_g\_w}} \right) \cdot \frac{1}{1000}$$
Where:
*   $\text{hover\_g\_w}$ is the hover efficiency (ranging from $6.2$ g/W for small props to $8.5$ g/W for larger props).

Required battery discharge C-rate is checked against hover currents:
$$C_{\text{rate, required}} = \frac{I_{\text{hover}}}{C_{\text{battery\_ah}}}$$

---

## 4. Redundancy & Fault Tolerance

Fault tolerance is critical for vertical flight phases. The framework models One Engine Inoperative (OEI) scenarios:
*   **OEI Controllability**: Controllability is checked by asserting if remaining motors ($N_{\text{rotors}} - 1$) can maintain a thrust-to-weight ratio $\ge 1.0$.
*   **Aero Authority**: Multirotor control mixer margins are flagged if motor count is $< 6$ (quadcopters lose yaw control during motor failure).

---

## 5. Validation Assumptions

The validator (`LiftSystemValidator`) asserts the following boundaries:
*   **Rotor overlap**: Props must not overlap. Sized tip clearance must exceed $2.5\%$ of the propeller diameter.
*   **Discharge limits**: Required C-rate must not exceed $45.0$ C to prevent thermal thermal battery runaways.
*   **Disk Loading**: Disk loading must stay within $5.0$ and $150.0$ N/m² limits (though overridden for heavy lifts).

---

## 6. Extension Mechanism

To add a new vertical lift strategy:
1.  Inherit from `BaseLiftStrategy` in `lift_system_strategy.py`.
2.  Implement the required attributes:
    *   `category`: `VTOLMissionCategory`
    *   `default_safety_factor`: `float`
    *   `target_disk_loading_n_m2`: `float`
    *   `get_recommendations() -> List[str]`
3.  Register the strategy in the registry: `VTOLFiftSystemStrategyRegistry.register(category, strategy_instance)`.
