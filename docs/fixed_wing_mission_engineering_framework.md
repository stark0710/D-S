# Fixed-Wing Mission Engineering Framework

## 1. Mission Engineering Philosophy

The Torq Wings Design Studio treats mission requirements as the foundational physics boundary of the entire aircraft design process. The philosophy of the **Fixed-Wing Mission Engineering Framework** is to capture, sanitize, and analyze operational constraints before any geometry or propulsion sizing is attempted. By analyzing requirements analytically up-front, the framework prevents downstream code from trying to optimize physically impossible designs (e.g. attempting to achieve a 10-hour flight time on a hand-launched 1kg battery-electric glider).

The framework separates the acquisition of raw intent from the calculated engineering constants, producing a structured and immutable `MissionProfile` that serves as the official operational record.

---

## 2. Mission Categories

The framework supports the following predefined mission categories:
*   **Survey**: Operational profiles focused on high roll stability and path coverage. Emphasizes steady flight states and camera protection.
*   **Mapping**: High overlap, steady glide, and altitude-hold mapping tracks.
*   **Long Endurance**: Minimal payloads, lightweight structures, glider-like aspect ratios to maximize flight time.
*   **Cargo**: Heavy payload mass fractions, wide structural fuselage sections, dual-engine layouts.
*   **Agriculture**: Low-altitude spraying, low speeds, rugged takeoff/landing gear.
*   **Research**: Modular instrumentation bays, low EMI, atmospheric sampling.
*   **Surveillance**: Long persistence flight, low acoustic signature, high aerodynamic lift-to-drag.
*   **Training**: Dihedral-stabilized wings, cheap repair materials (EPP foam), simple tricycle gear.
*   **Racing**: High speeds, high drag tolerances, low flight time, short battery life.
*   **Custom**: General multi-role profiles that do not map directly to standard heuristics.

---

## 3. Mission Scoring

Mission scoring consists of three decoupled numerical engines within `MissionScoringService`:

1.  **Complexity Score (0.0 to 100.0)**:
    Evaluated by summing points for payload mass, range targets, flight time, and operational environments:
    *   *Payload limits*: Heavy payloads increase wing loading.
    *   *Endurance*: Flight times > 3 hours scale up battery mass significantly.
    *   *Environment*: Urban, mountain, or marine terrains carry a high complexity index.
    The final score is classified as **Low**, **Medium**, **High**, or **Very High**.

2.  **Feasibility Score (0.0 to 100.0)**:
    An engineering sanity index. The score starts at 100.0 and is penalized for highly challenging parameter bounds:
    *   Endurance targets > 5 hours.
    *   Payload weights > 20 kg.
    *   Stall margins < 15 km/h.
    *   Insufficent budget allocations.
    *   Urban obstacle risks.

3.  **Consolidated Mission Score**:
    Combines feasibility and complexity:
    $$\text{Mission Score} = \text{Feasibility} \times \left(1.0 - \frac{\text{Complexity}}{200.0}\right)$$

---

## 4. Validation Methodology

The validation pipeline enforces raw constraints using `MissionValidator`:
1.  **Physical Feasibility**: Disallows negative payloads, speeds, or ranges.
2.  **Boundary Checks**: Checks that target limits (like maximum takeoff weight) are physically compatible with requested payloads.
3.  **Safety Consistency**:
    *   *Cruise vs. Stall speed*: Stall speed must be lower than cruise speed by a safe margin to avoid in-flight stall.
    *   *Range vs. Cruise and Endurance*: Target range cannot exceed $1.5 \times$ the theoretical distance covered at cruise speed in the given flight time.
    *   *Launch and Landing Safety*: Hand launching heavy aircraft (>12kg) or belly landing heavy structures (>20kg) raises validation errors to prevent field accidents.

---

## 5. Extension Mechanism

To add a new fixed-wing mission category:
1.  Define a new member in the `MissionCategory` enum inside `mission_requirements.py`.
2.  Create a subclass of `BaseMissionStrategy` in `mission_strategy.py`.
3.  Override:
    *   `category` property.
    *   `get_target_payload_fraction() -> float`.
    *   `get_lift_to_drag_ratio() -> float`.
    *   `get_recommendations() -> List[str]`.
4.  Register the strategy in the registry by calling `MissionStrategyRegistry.register(MissionCategory.NEW_CAT, NewStrategy)` inside `mission_registry.py`.
