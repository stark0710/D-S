# Fixed-Wing Propulsion Engineering Framework

## 1. Propulsion Engineering Philosophy

The **Fixed-Wing Propulsion Engineering Framework** designs and validates the aircraft propulsion subsystem. By consuming the results of preceding stages (`MissionResult`, `ConfigurationResult`, `WingResult`, `AirfoilResult`, `TailResult`, `FuselageResult`), the framework implements a decoupled power boundary:
*   It does **not** design the electrical power distribution system or choose batteries (which belongs to the electrical/battery framework).
*   Instead, it determines the propulsion architecture, selects brushless DC motors or gasoline engines, sizes propeller diameter and pitch, and analyzes flight thrust, power, and efficiency margins.

This ensures that the sized propulsion plant provides sufficient takeoff thrust, safe rate of climb, and efficient cruise capability.

---

## 2. Propulsion Architectures & Layouts

The framework supports the following propulsion styles:
*   **Electric**: Quiet, simple, highly reliable, suitable for standard sub-50kg UAVs. Sized using brushless DC motors (KV ratings, cell count).
*   **Internal Combustion Engine (ICE)**: High energy density gasoline engines, suitable for heavy cargo load lifting and extreme long-range profiles.
*   **Hybrid / Fuel Cell**: Combined configurations for extended range.

Layout configurations include:
*   **Single Tractor**: Standard nose mount, pulling the aircraft. Efficient cooling wash over the fuselage, but can turbulate wing airflow.
*   **Single Pusher**: Rear fuselage mount, pushing the aircraft. Leaves the nose clear for cameras and minimizes fuselage skin drag, but has lower prop inflow efficiency.
*   **Twin Tractor / Pusher**: Dual wing-mounted pods to scale power or balance motor torque.

---

## 3. Motor and Engine Selection

Components are chosen dynamically based on estimated maximum takeoff and climb power requirements ($P_{\text{max}}$):
*   **Electric Brushless DC Motors**: The selector queries a database of KV-rated motors, matching the maximum power draw. Sizing prioritizes lightweight motors meeting the wattage.
*   **Internal Combustion Engines**: displacement (cc) and horsepower are matched to Watts:
    $$P_{\text{shaft}} = \text{Horsepower} \times 745.7$$
    Small displacement gas engines (e.g. DLE 20cc, Saito FG-21) are selected for heavier configurations.

---

## 4. Propeller Selection

Propellers are sized using **Actuator Disk Theory** to match target takeoff thrust limits while respecting ground clearance bounds (`max_prop_diameter_m` sized from fuselage landing gear height):
$$T_{\text{static}} = \left( \rho \cdot A \cdot (P_{\text{shaft}} \cdot \eta_{\text{prop}})^2 \right)^{1/3}$$

Where:
*   $\rho$ is the calculated air density at takeoff.
*   $A$ is the propeller disc area ($\frac{\pi}{4} \cdot D^2$).
*   $P_{\text{shaft}}$ is the maximum motor shaft power.
*   $\eta_{\text{prop}}$ is the static thrust propeller efficiency (default 0.65).

The selector matches standard pitch and diameter combinations (e.g. 12x6, 15x10) to deliver the target thrust.

---

## 5. Takeoff and Climb Methodology

Propulsion flight performance parameters are computed dynamically:
*   **Takeoff Distance ($d_{\text{takeoff}}$)**: Estimated using a standard UAV ground run equation:
    $$d_{\text{takeoff}} \approx \frac{20 \cdot \left(\frac{W}{S}\right)}{\left(\frac{T}{W}\right) \cdot C_{L,\text{takeoff}} \cdot g}$$
    Where $W/S$ is the wing loading, and $T/W$ is the actual takeoff thrust-to-weight ratio.
*   **Rate of Climb ($ROC$)**: Calculated from excess climb power:
    $$ROC = \frac{P_{\text{excess}}}{W} = \frac{P_{\text{shaft}} \cdot \eta_{\text{total}} - D_{\text{climb}} \cdot V_{\text{climb}}}{W}$$
    Safe climb bounds are validated ($ROC \ge 0.5$ m/s).

---

## 6. Cruise Optimization

Cruise efficiency is audited by estimating current draw and power consumption rates:
*   **Throttle settings**: Sized cruise power is checked against maximum motor power:
    $$\text{Throttle}_{\text{pct}} = \frac{P_{\text{cruise}}}{P_{\text{motor\_max}}} \times 100$$
    Target throttle settings are $30\%$ to $70\%$ to preserve headwind climb margin without carrying excess motor weight.
*   **Energy depletion rate**: Sized as Wh per kilometer:
    $$\text{Wh/km} = \frac{P_{\text{cruise}}}{V_{\text{cruise\_kmh}}}$$
    This acts as the primary optimization metric for endurance.

---

## 7. Validation Assumptions

The validator (`PropulsionValidator`) asserts the following constraints:
*   **Thrust-to-weight ratio**: Sized static thrust must satisfy takeoff safety limits ($T/W \ge 0.40$ to $0.50$ depending on strategy).
*   **Power limits**: Sized motor max power must exceed climb power demands.
*   **Throttle suitability**: Cruise throttle settings below 28% (oversized) or above 72% (undersized) trigger warnings.
*   **Engine layout compatibility**: Gasoline ICE propulsion cannot be mounted on Tailless/Flying Wing layouts due to CG travel issues.

---

## 8. Extension Mechanism

To add a new propulsion strategy:
1.  Inherit from `BasePropulsionStrategy` in `propulsion_strategy.py`.
2.  Implement:
    *   `select_propulsion_type(requirements) -> PropulsionType`.
    *   `select_propulsion_layout(requirements) -> PropulsionLayout`.
    *   `get_thrust_to_weight_ratio() -> float`.
    *   `get_recommendations(thrust_ratio) -> List[str]`.
3.  Register the strategy in the registry: `PropulsionStrategyRegistry.register("new_type", NewStrategy)`.
