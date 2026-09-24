# VTOL Aircraft Configuration Engineering Framework

## 1. Configuration Engineering Philosophy

The **VTOL Aircraft Configuration Engineering Framework** selects the overall structural layout, flight mode allocations, and propulsion architecture of a VTOL aircraft. It maps mission requirements to qualitative design spaces, evaluating layout combinations (e.g. lift systems, cruise engines, vectoring, and flight control authority) for optimal compatibility.

This ensures that subsequent detailed sizing engines start from a mathematically sound and aerodynamically consistent base architecture.

---

## 2. Supported VTOL Architectures

The framework supports layout combinations across the primary VTOL families:
*   **QuadPlane**: Classic fixed-wing with 4 vertical lift motors mounted on booms. Predictable flight controls but carries deadweight in cruise.
*   **Lift + Cruise**: Dedicated vertical lift rotors combined with a separate rear pusher propeller for forward flight. Simple transition physics, but high parasitic drag.
*   **Tilt Rotor**: Main rotors tilt 90 degrees to act as lift rotors in hover and tractors in cruise. High cruise efficiency, but complex vectoring servos.
*   **Tilt Wing**: Entire wing pivots 90 degrees. Simplifies rotor-wing downwash drag, but highly sensitive to wing-stall transitions in crosswinds.
*   **Tail Sitter**: Aircraft pitches 90 degrees. Vertically takeoff and pitches forward to cruise. Sized aerodynamically clean with no extra tilt linkages, but extremely challenging hover landing stability.
*   **Vectored Thrust**: Internal or vectoring nozzles direct flow. High speed, low radar profile, but mechanically complex.
*   **Twin Boom VTOL**: Dedicated booms integrated into the tail structures housing vertical rotors. Excellent stability.
*   **Box Wing VTOL**: Box wing structures providing hover stability and high stall angles.
*   **Hybrid VTOL**: Range-extended powertrain integrating combustion engines to charge batteries or directly run propulsion.

---

## 3. Flight Mode Configuration

VTOL designs are sized to operate across 8 mandatory flight modes:
*   **Hover**: Zero forward speed, vertical thrust balancing weight.
*   **Vertical Takeoff**: Ascent profile from ground waypoint.
*   **Vertical Landing**: Descent and land positioning.
*   **Transition to Cruise**: Forward acceleration blending thrust from lift rotors to wing lift.
*   **Cruise**: Wing-borne forward flight with vertical lift systems deactivated.
*   **Transition to Hover**: Deceleration and vertical capture at target waypoint.
*   **Emergency Mode**: Safe glide profiles or high-thrust hover capture during actuator failure.
*   **Recovery Mode**: Home-return profile under degraded avionics states.

---

## 4. Lift System Selection & Transition Concepts

Choosing an architecture represents a multi-variable trade-off between:
*   **Tilt vs. Dedicated Lift**: Tilt systems remove the dead weight and drag of vertical lift rotors during cruise but add heavy servo pivot linkages. Dedicated systems (QuadPlanes) are structurally simpler but less efficient for long-range tasks.
*   **Transition Complexity**: Moving rotors or wing surfaces require sophisticated autopilot mixers to manage blending lift and control authority during transition stall regimes.

---

## 5. Validation Assumptions

The validator (`ConfigurationValidator`) asserts the following physical constraints:
*   **Takeoff Method vs. Lift**: A vertical takeoff method requires a layout with active lift motors (`lift_motor_count > 0`) or tilt rotor servos.
*   **Redundancy Requirements**: If a "Single Motor Out" redundancy level is specified, the motor count must be $\ge 6$ (e.g. hexacopters or octacopters) to guarantee controllability during rotor loss.
*   **Motor Count Boundaries**: Overall motor count must be positive and not exceed 32.

---

## 6. Extension Mechanism

To add a new VTOL configuration strategy:
1.  Define a class implementing `ConfigurationStrategy` or inheriting from `BaseConfigurationStrategy` in `configuration_strategy.py`.
2.  Implement:
    *   `score_vtol_type(vtol_type) -> float` to return compatibility ratings.
    *   `get_analysis_weights() -> Dict[str, float]` for trade-off scoring weights.
    *   `get_recommendations(profile) -> List[str]`.
3.  Register the strategy in the registry: `VTOLConfigurationStrategyRegistry.register(category, strategy_instance)`.
