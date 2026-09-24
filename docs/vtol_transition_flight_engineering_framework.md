# VTOL Transition Flight Engineering Framework

## VTOL Transition Engineering Philosophy
Transition is the most complex flight phase, where lift generation dynamically transfers between active vertical rotors and fixed-wing surfaces. If conversion occurs too quickly, the wing may stall. If conversion is too slow, excess power draw drains batteries and increases drag penalties. The core objectives of the framework include:
1. **Continuous Lift Blending**: Coordinating rotor unloading and wing lift build-up to maintain a constant vertical load factor ($n_z \approx 1.0$) during acceleration and deceleration.
2. **Control surface Handover**: Scheduling control allocations such that control surface effectiveness increases as airspeed grows, while rotor differential thrust inputs fade.
3. **Flight envelope Safety (OEI)**: Modeling conversion limits under engine shutdowns to ensure safe abort paths or glide margins are maintained.

---

## Transition Scheduling Methodology
Transition schedules partition conversion segments into discrete stages over airspeed increments:
- **Hover**: 100% rotor-supported lift, aerodynamic control surfaces inactive.
- **Pitch Blend (Acceleration)**: Forward propulsion builds speed, lift rotors start unloading, wing lift grows, and control surfaces begin gaining control authority.
- **Wing-Borne**: Wing generates enough lift to sustain takeoff mass.
- **Rotor Shutdown**: Lift motors shut down and align to limit drag, leaving the aircraft in 100% cruise flight mode.

---

## Lift Transfer Analysis
Lift transfer is modeled as a function of forward velocity ($V$) relative to target conversion speed ($V_{conv}$):
$$L_{wing}(V) = L_{takeoff} \times \left(\frac{V}{V_{conv}}\right)^2$$
The remaining takeoff mass is supported by vertical thrust:
$$T_{vertical}(V) = W_{takeoff} - L_{wing}(V)$$
This prevents altitude losses during pitch blends.

---

## Control Allocation
Control surface effectiveness scales quadratically with airspeed. Actuator command weights ($u$) are allocated dynamically:
$$u_{composite} = (1 - w(V)) \cdot u_{rotors} + w(V) \cdot u_{surfaces}$$
where $w(V) \approx (V/V_{conv})^2$ is the blend weighting. This limits actuator saturation risks.

---

## Flight Mode Synchronization
Synchronization registers flight controller state switches:
- **Transition Entry**: Arming forward propulsion, initiating pitch blends.
- **Transition Exit**: Aligning and locking vertical rotors once airspeed exceeds the stall limit ($1.20 \times V_{stall}$).
- **Transition Abort**: Quick-reversal triggers to return to hover flight mode if forward speed fails to build within 30 seconds.

---

## Failure Handling
The framework sizes behavior under OEI (One Engine Inoperative) conditions:
- **OEI Abort Decision Speed**: Speed threshold below which a transition abort is executed, and above which conversion is completed on fixed-wing power.
- **Glide Envelope**: Sizing wing glide distances ($L/D$ ratios) to execute emergency landings.

---

## Validation Assumptions
The validator checks:
- **Conversion speed bounds**: Verifies conversion speed lies between 40 km/h and 90 km/h.
- **Transition Duration limit**: Asserts that transition duration does not exceed 30 seconds to prevent battery current overloads.
- **Stability margins**: Confirms longitudinal stability margins exceed 5.0% MAC across the transition flight profile.

---

## Extension Mechanism
To extend the framework:
1. **Incorporate transition dynamics models**: Edit `transition_dynamics.py` to add tilt-rotor gyroscopic torque calculations.
2. **Add Custom Sizing strategies**: Implement the `TransitionStrategy` interface in `transition_strategy.py` and register it in `transition_registry.py`.
