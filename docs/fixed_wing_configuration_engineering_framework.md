# Fixed-Wing Aircraft Configuration Engineering Framework

## 1. Configuration Engineering Philosophy

The **Fixed-Wing Aircraft Configuration Engineering Framework** selects the overall structural layout and propulsion architecture of the aircraft. By treating configuration selection as a decoupled trade-off problem, the framework establishes a clean boundary:
*   It does **not** perform wing sizing or run CFD/aerodynamic analysis.
*   Instead, it maps mission requirements to qualitative design spaces, evaluating layout combinations (e.g. wing placement, propeller location, tail assembly, and gear wheels) for optimal compatibility.

This ensures that the subsequent detailed design engines start from a mathematically sound and aerodynamically consistent base architecture.

---

## 2. Aircraft Architectures

The framework supports layout combinations across four primary sub-assemblies:

### Wing Position
*   **High Wing**: High roll stability due to pendulum effect; great ground clearance; easy belly landings.
*   **Mid Wing**: Aerodynamically cleanest fuselage junction; neutral stability; complex internal spar routing.
*   **Low Wing**: Best ground effect during landing; facilitates short landing gear struts; poor roll stability.
*   **Parasol Wing**: Wing mounted on struts above fuselage. High drag, but leaves center fuselage open.
*   **Shoulder Wing**: Mounted on upper fuselage shoulder; clean airflow.

### Propulsion Layout
*   **Tractor**: Propeller at the nose. Good elevator wash, simple mounting, but obstructs forward cameras.
*   **Pusher**: Rear-mounted engine. Clean nose view for sensors, laminar flow, but propeller strike hazards.
*   **Twin Tractor / Twin Pusher**: Motor nacelles on wings. Distributes bending loads, engine-out safety.
*   **Twin Boom Pusher**: Rear motor mounted between twin booms. High stability, clean payload view.
*   **Distributed Propulsion**: Multiple motors along wings. High redundancy, blown wing lift, complex ESC wiring.

### Tail Configurations
*   **Conventional**: Familiar horizontal stabilizer + vertical tail. Simple, predictable.
*   **T-Tail**: Elevator raised above prop wash. Clean aerodynamics, but high structural tail loads.
*   **V-Tail**: Combined ruddervators. Low wetted area/drag, complex mixing control logic.
*   **Twin Boom**: Dual booms holding tail assembly. Ideal for pushers.
*   **Canard**: Horizontal stabilizer placed forward of wings. Stall-safe design.
*   **Tailless / Flying Wing**: Wings only. Lowest possible drag, but highly sensitive CG range.

### Landing Gear
*   **Tricycle**: Easiest runway steering and landing control.
*   **Taildragger**: Lightest wheels, maximum propeller ground clearance on unpaved ground.
*   **Belly Landing**: No wheel drag. Requires High/Parasol wing to protect tips.
*   **Skid**: Simple skid pads for grass fields.

---

## 3. Configuration Trade-Offs

Choosing an architecture represents a multi-variable trade-off between:
*   **Aerodynamic Efficiency vs. Structural Simplicity**: Flying wings have minimum drag but suffer from pitch instability. Twin booms offer stable pusher setups but add structural mass.
*   **Payload Accommodation vs. Weight**: Twin engines allow lifting heavier cargo payloads but reduce endurance due to battery drag/mass scaling.
*   **Manufacturability vs. Operational Site**: Runway gear (Tricycle) is easy to construct but limits takeoff to flat runways. Belly landing skid gear allows launch in wild rural areas but causes impact wear.

---

## 4. Selection Methodology

The selection engine (`ConfigurationEngine`) runs a three-stage MCDA algorithm:
1.  **Strategy Layout Selection**: The matching strategy selects its optimal layout.
2.  **Trade-Off Scoring**: The selector scores candidate configurations using the `ConfigurationScoringService` weights.
3.  **Alternative Comparison**: Evaluates and ranks alternatives, computing delta values for cost, simplicity, and aerodynamic efficiency.

---

## 5. Validation Assumptions

The validator (`ConfigurationValidator`) asserts the following physical constraints:
*   **Wing vs. Landing**: Low Wing is incompatible with Belly Landing (wing strikes ground).
*   **Gear vs. Landing**: Runway landing requires Tricycle or Taildragger gear.
*   **Propeller vs. Launch**: Hand launch is incompatible with heavy cargo payloads (>5kg) or low-wing pusher layouts.
*   **Tail vs. Propulsion**: Twin Boom tail setups should utilize Pusher propulsion. Tailless wings must not have tail control surfaces.

---

## 6. Extension Mechanism

To add a new aircraft configuration strategy:
1.  Define a class implementing `ConfigurationStrategy` or inheriting from `BaseConfigurationStrategy`.
2.  Implement `select_best_layout(requirements)` to return the layout mapping.
3.  Implement `get_recommendations()` and `get_engineering_rationale()`.
4.  Register the strategy in the registry: `ConfigurationStrategyRegistry.register("new_type", NewStrategy)`.
