# Fixed-Wing Airfoil Engineering Framework

## 1. Airfoil Engineering Philosophy

The **Fixed-Wing Airfoil Engineering Framework** selects, evaluates, and validates the cross-sectional profiles (airfoils) of the wing. By consuming the outputs of preceding stages (`MissionResult`, `ConfigurationResult`, `WingResult`), it bridges macro geometry and micro aerodynamics:
*   It does **not** design the planform layout (wingspan, area, chord distribution), which is frozen in the preceding stage.
*   Instead, it determines the aerodynamic profile: selecting root and tip airfoils, establishing chord-wise loft distributions, interpolating drag polars, and conducting spanwise Reynolds flow audits.

This ensures that the wing produces the required lift coefficient ($C_{L,\text{cruise}}$) at cruise altitude with minimal drag and safe, predictable stall characteristics.

---

## 2. Selection Methodology

Airfoil selection is driven by the mission profile and structural layout through the `AirfoilSelector` and matching strategies:
*   **Long Endurance**: High aspect ratio wings require thin, low-drag, laminar flow profiles (e.g., `MH 32`) or reflexed profiles (e.g., `MH 45`) for tailless configurations to minimize induced and profile drag.
*   **Cargo**: Heavy lift transporters require thick, highly cambered, high-lift profiles (e.g., `Selig S1223`) at the root to generate high lift coefficients ($C_L \ge 1.8$).
*   **Survey / Mapping**: Stable mapping flights use cambered, gentle stall profiles (e.g., `Clark Y` or `NACA 4412`) lofted to symmetrical tips (e.g., `NACA 0012`) to preserve control authority during low-speed turns.
*   **Trainer**: Durability and docile stalls are achieved using constant `Clark Y` profiles across the span.
*   **Aerobatic**: Double-symmetric flight tracks require symmetrical profiles (e.g., `NACA 0012`) at both root and tip.

---

## 3. Polar Analysis

Aerodynamic coefficient evaluation is performed by the `PolarAnalysisService` using parabolic polar drag curves:
$$C_D = C_{D0} + K \cdot (C_L - C_{L,\text{opt}})^2$$

Where:
*   $C_{D0}$ is the minimum drag (viscosity-corrected based on Reynolds number).
*   $K$ is the profile drag increment.
*   $C_{L,\text{opt}}$ is the lift coefficient at minimum drag.

The analysis evaluates section lift ($C_L$), section profile drag ($C_D$), pitching moment ($C_{m0}$), section lift-to-drag ($L/D$), and stall angle ($\alpha_{\text{stall}}$) under the target cruise lift coefficient ($C_{L,\text{cruise}}$). It also computes the maximum sectional lift-to-drag ratio ($L/D_{\text{max}}$) across the flight envelope.

---

## 4. Reynolds Number Analysis

Reynolds numbers ($Re = \frac{\rho \cdot V \cdot c}{\mu}$) dictate aerodynamic behavior and are computed across the span (root, tip, and mean chords) using Sutherland's law for air dynamic viscosity ($\mu$):
$$\mu = \mu_0 \cdot \frac{T_0 + S}{T + S} \cdot \left(\frac{T}{T_0}\right)^{1.5}$$

Where:
*   $\mu_0 = 1.7894 \times 10^{-5}$ Pa·s
*   $T_0 = 273.11$ K
*   $S = 110.56$ K
*   $T$ is the absolute ambient temperature.

The computed Reynolds numbers are used to apply viscous corrections to $C_{L,\text{max}}$, stall angles, and minimum drag coefficients.

---

## 5. Performance Mapping

The `PerformanceMapService` compiles a 2D matrix mapping drag coefficients ($C_D$) and sectional lift-to-drag ($L/D$) ratios across a grid of Reynolds number nodes ($Re$) and lift coefficient nodes ($C_L$). This map provides the downstream flight envelope simulator with sectional drag data across all key flight states (stall speed glide, cruise efficiency, and high-speed cruise).

---

## 6. Validation Assumptions

The validator (`AirfoilValidator`) enforces the following physical boundaries:
*   **Endurance Suitability**: High-Lift airfoils (e.g. Selig S1223) must not be selected for Long Endurance missions due to excessive profile drag in cruise.
*   **Lift Suitability**: Symmetrical airfoils must not be used at the root for heavy Cargo designs.
*   **Viscous Compatibility**: Sizing laminar flow airfoils (e.g. MH 32) at low Reynolds numbers ($Re < 120,000$) triggers warnings due to high risks of laminar separation bubble drag.
*   **Structural Compatibility**: Wing designs with aspect ratios $AR \ge 12.0$ must not use root airfoils with thickness ratios $< 9.0\%$ to ensure sufficient room for wing spars.
*   **Aerodynamic Stability**: Absolute zero-lift pitching moments ($C_{m0}$) must not exceed $0.15$ to prevent excessive trim drag on the horizontal tail.

---

## 7. Extension Mechanism

To add a new airfoil strategy:
1.  Inherit from `BaseAirfoilStrategy` in `airfoil_strategy.py`.
2.  Implement:
    *   `select_best_airfoils(requirements) -> Tuple[str, str, str]` to return names of root and tip profiles.
    *   `get_allowed_types() -> List[AirfoilType]`.
    *   `get_recommendations(analysis) -> List[str]`.
3.  Register the strategy in the registry: `AirfoilStrategyRegistry.register("new_type", NewStrategy)`.
