# VTOL Hover Performance Engineering Framework

## VTOL Hover Engineering Philosophy
Hover flight is the most energy-intensive segment of any VTOL flight mission. Sizing the vertical lift system requires a balance between thrust safety margins, control responsiveness, and battery voltage sag limits. The core values of the framework include:
1. **Control authority Headroom**: Ensuring that at least 15% of actuator headroom is maintained under crosswinds and gust responses to prevent attitude deviations.
2. **Environmental Tolerance**: Estimating performance limits (e.g. ceilings) under variable atmospheric temperatures and air densities (hot-and-high conditions).
3. **Fail-Safe Redundancy (OEI)**: Assessing whether control margins and thrust authority are sufficient to maintain a level position or execute a safe emergency landing if a single motor/rotor fails.

---

## Hover Sizing Methodology
Every lift layout undergoes a multi-stage sizing evaluation:
- **Thrust Sizing**: Calculating total disk area and disk loading ($N/m^2$). Thrust margin is evaluated as the Thrust-to-Weight (T/W) ratio.
- **Power Sizing**: Sizing induced power, profile drag power, and estimating battery voltage sag coefficients.
- **Stability Sizing**: Sizing roll, pitch, and yaw damping rates ($N \cdot m / (rad/s)$) and rotor-wing wake interactions.
- **Control Margin**: Estimating max angular acceleration rates ($rad/s^2$) under full actuator deflection.
- **Ceiling Sizing**: Calculating density altitude offsets to estimate maximum hover ceilings.

---

## Ground Effect Modeling
Hovering near the ground (within 1 to 1.5 times the rotor diameter height) reduces induced drag and increases vertical thrust. The framework models Ground Effect (IGE) relative to Out-of-Ground Effect (OGE) using Hayden's empirical correction:
$$\frac{T_{IGE}}{T_{OGE}} = \frac{1}{1 - 0.99 \left(\frac{R}{4h}\right)^2}$$
where $R$ is the rotor radius and $h$ is the hover height above the surface.

---

## Hover Stability Analysis
Hover stability evaluates damping rates and gust response ratios:
- **Damping Derivatives**: Roll, pitch, and yaw damping rates represent the aircraft's physical resistance to angular rotation.
- **Rotor Wake Interactions**: Sizing the aerodynamic interference penalties between hover rotor downwash and wing structures (typically estimated as a loss of 8.0% lift efficiency).
- **Gust Response**: Modeled using standard damping ratios (tuned to 0.70 - 0.75 for stability).

---

## Rotor Failure Handling (OEI)
For multi-rotor configurations, the framework evaluates One Engine Inoperative (OEI) states:
- **OEI Thrust Margin**: Sized as:
  $$T/W_{OEI} = \frac{N_{rotors} - 1}{N_{rotors}} \times T/W_{Nominal}$$
- **Safety Rating**: If $T/W_{OEI} \ge 1.05$, the aircraft can maintain level hover and attitude control. If not, it flags warning states and estimates emergency descent rates.

---

## Environmental Corrections
Ceiling and thrust parameters adjust based on local atmospheric properties:
- **Air Density**: Density ratios ($\sigma$) scale thrust capacity ($\text{Thrust} \propto \rho$).
- **Ceiling Estimation**: Hover ceiling (OGE) is computed as the density altitude where $T/W_{Nominal} \to 1.0$:
  $$H_{ceiling\_oge} = 8500 \cdot \ln(T/W_{Nominal})$$

---

## Validation Assumptions
The validator checks and flags:
- **Thrust margin deficit**: Flags designs where nominal $T/W$ falls below 1.30.
- **Excessive Power draw**: Ensures the continuous power draw does not exceed battery discharge limits.
- **Control authority headroom deficit**: Flags roll, pitch, or yaw control margins below 15% under wind disturbances.
- **Wind velocity limit violation**: Flags designs unable to hover stably under 25-knot crosswinds.

---

## Extension Mechanism
To extend the framework:
1. **Refine Sizing Formulas**: Modify equations in `hover_thrust.py` or `hover_power.py` to incorporate specialized blade element momentum (BEM) theories.
2. **Add Custom Sizing Strategies**: Implement the `HoverStrategy` interface in `hover_strategy.py` and register it inside `hover_registry.py`.
