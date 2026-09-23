# Fixed-Wing Flight Performance Sizing Framework

## 1. Flight Performance Engineering Philosophy

The **Fixed-Wing Flight Performance Sizing Framework** serves as the final analytical check in the Fixed-Wing design loop. Consuming all preceding framework outputs (`MissionResult`, `ConfigurationResult`, `WingResult`, `AirfoilResult`, `TailResult`, `FuselageResult`, `PropulsionResult`, `AvionicsResult`, `PayloadResult`, `MassResult`), it computes:
*   Standard flight speeds (stall, maximum, cruise).
*   Runway performance (takeoff roll and landing braking distance).
*   vertical climb and descent angles.
*   glide efficiencies and turn load factors.
*   ranges, endurances, and service ceilings.

It serves as the definitive gatekeeper validating whether the sized aircraft is physically capable of completing the target mission profile.

---

## 2. Aerodynamic Analysis Methodology

Aerodynamic lift and drag coefficients are modeled using standard drag polars:
$$C_D = C_{D0} + K \cdot C_L^2$$

Where:
*   $C_{D0}$ is the zero-lift parasite drag coefficient (baseline 0.023 for clean utility fixed wing UAVs).
*   $K$ is the induced drag coefficient factor resolved from aspect ratio and Oswald efficiency ($e = 0.82$):
    $$K = \frac{1}{\pi \cdot AR \cdot e}$$
*   The cruise lift coefficient ($C_{L,\text{cruise}}$) is solved directly from cruise dynamic pressure ($q$) and aircraft MTOW:
    $$C_{L,\text{cruise}} = \frac{2 \cdot W}{\rho \cdot V_{\text{cruise}}^2 \cdot S}$$
*   Aerodynamic efficiency is represented by the lift-to-drag ratio ($L/D = C_L / C_D$).

---

## 3. Performance Prediction Methodology

Operational speeds and distances are solved using standard aeronautical equations:
*   **Stall Speeds**: Sized in clean and landing configurations (flaps deflected increases $C_{L,\text{max}}$ by 0.35):
    $$V_{\text{stall}} = \sqrt{\frac{2 \cdot W}{\rho \cdot S \cdot C_{L,\text{max}}}}$$
*   **Maximum Top Speed**: Solved from peak shaft power at full throttle:
    $$V_{\text{max}} = \left( \frac{2 \cdot P_{\text{shaft\_max}} \cdot \eta_{\text{prop}}}{\rho \cdot S \cdot C_{D0}} \right)^{1/3}$$
*   **Gliding Range**: best glide ratio is solved from drag polar limits:
    $$(L/D)_{\text{max}} = \frac{1}{2 \cdot \sqrt{C_{D0} \cdot K}}$$
*   **Rate of Climb ($ROC$)**: Sized from excess power:
    $$ROC = \frac{P_{\text{shaft\_max}} \cdot \eta_{\text{total}} - D_{\text{cruise}} \cdot V_{\text{climb}}}{W}$$

---

## 4. Range and Endurance Estimation

Ranges and flight endurances are computed dynamically from battery weights and continuous power draws:
*   **Battery Capacity**: Solved using LiPo energy density:
    $$E_{\text{battery\_wh}} = m_{\text{battery}} \times 200.0\text{ Wh/kg}$$
*   **continuous Power Draw**: Sum of cruise propulsion power, flight controller avionics, and payload camera draws.
*   **Flight Endurance**: Sized in minutes:
    $$\text{Endurance}_{\text{min}} = \frac{E_{\text{battery\_wh}}}{P_{\text{continuous}}} \times 60.0$$
*   **Maximum Range**:
    $$\text{Range}_{\text{km}} = \text{Endurance}_{\text{hours}} \times V_{\text{cruise\_kmh}}$$
*   Operational range includes a $15\%$ safety reserve battery boundary.

---

## 5. Environmental Model & Assumptions

Flight envelopes are evaluated at the target mission operational altitude using standard atmospheric profiles:
*   **Standard Atmosphere**: Senses lapse rates for absolute temperature, pressure, and air density ($\rho$) from sea level up to Stratosphere.
*   Performance margin calculations accounts for air density degradation at high operational altitudes.

---

## 6. Validation Assumptions

The validator (`FlightValidator`) asserts the following constraints:
*   **Runway Rolls**: Sized takeoff and landing rolls must not exceed $100.0$ meters.
*   **Climb margins**: Sized rate of climb must meet or exceed target limits (minimum $1.0$ to $3.0$ m/s).
*   **Feasibility**: Range and endurance must meet or exceed mission requirements.
*   **Stall Margin**: Cruise speed must exceed clean stall speed by at least the strategy's stall speed margin percentage (e.g. $30\%$).
*   **Range Reserve**: Cruise range must exceed target mission range by at least $15\%$ reserve margin.

---

## 7. Extension Mechanism

To add a new flight strategy:
1.  Inherit from `BaseFlightStrategy` in `flight_strategy.py`.
2.  Implement:
    *   `get_performance_margins() -> Tuple[float, float]`.
    *   `get_stall_speed_margin_pct() -> float`.
    *   `get_recommendations() -> List[str]`.
3.  Register the strategy in the registry: `FlightStrategyRegistry.register("new_type", NewStrategy)`.
