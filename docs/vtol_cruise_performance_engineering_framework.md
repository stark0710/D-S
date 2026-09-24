# VTOL Cruise Performance Engineering Framework

## VTOL Cruise Performance Philosophy
Fixed-wing forward cruise is the most efficient segment of a VTOL flight profile. Minimizing thrust required and optimizing propulsive efficiency enables the aircraft to satisfy long-range and duration targets. The core values of the framework include:
1. **Aerodynamic Optimization**: Maximizing Lift-to-Drag ($L/D$) ratios to minimize forward drag, directly reducing the required battery capacity.
2. **Residual energy management**: Deducting hover and transition energy margins first, ensuring forward cruise calculations utilize only true residual battery capacities.
3. **Envelope constraints compliance**: Actively enforcing stall and high-altitude ceilings to protect control surface effectiveness.

---

## Cruise Analysis Methodology
Forward flight cruise analysis calculates key parameters:
- **Cruise speed**: Sustained forward speed.
- **Best range speed ($V_{br}$)**: Velocity maximizing distance per unit of energy.
- **Best endurance speed ($V_{be}$)**: Velocity minimizing power required to stay airborne.
- **Stall speed limit ($V_{stall}$)**: Minimum safe flight speed.
- **Rate of Climb (ROC)**: Climb rate capacity under full forward throttle.
- **Rate of Descent (ROD)**: Glide capability with zero motor thrust.

---

## Range Estimation & Endurance Estimation
Endurance and range are calculated using the available energy after deducting vertical takeoff hover and conversion segments, with a mandatory safety state-of-charge reserve (typically 15%):
$$E_{avail} = E_{total} - E_{hover} - E_{transition} - E_{reserve}$$
$$Endurance = \frac{E_{avail}}{P_{cruise}}$$
$$Range = Endurance \times V_{cruise}$$
This provides realistic range estimations.

---

## Power Budgeting
Power required ($P_{cruise}$) is sized based on forward aerodynamic drag ($D$) and propulsive efficiency ($\eta_p$):
$$D = \frac{W_{takeoff}}{L/D}$$
$$P_{cruise} = \frac{D \times V_{cruise}}{\eta_p}$$
Current draw ($I_{cruise}$) is sized against system voltage ($V_{sys}$):
$$I_{cruise} = \frac{P_{cruise}}{V_{sys}}$$

---

## Performance Envelope Generation
The flight envelope bounds operational limits:
- **Stall boundary**: Airspeeds below $1.2 \times V_{stall}$ are flagged as unsafe.
- **Service Ceiling**: Sized altitude where climb rate drops below $0.5\text{ m/s}$ (approx. $ROC \to 0$):
  $$H_{service} = 8500 \cdot \ln\left(\frac{P_{avail}}{P_{required}}\right)$$
- **Operational Ceiling**: Safety margin of $300\text{ m}$ below the service ceiling.

---

## Validation Assumptions
The validator checks:
- **Range deficit**: Flags designs where sized range falls below requirements.
- **Endurance deficit**: Flags designs where endurance falls below limits.
- **Climb rate margin**: Confirms that maximum rate of climb exceeds $2.0\text{ m/s}$.
- **Power margin warning**: Warns if required cruise power exceeds cruise motor ratings.

---

## Extension Mechanism
To extend the framework:
1. **Refine Sizing calculations**: Modify drag or ceiling models in `cruise_power_analysis.py` or `performance_envelope_analysis.py` to add drag polar curves.
2. **Add Custom Sizing strategies**: Implement the `CruisePerformanceStrategy` interface in `cruise_strategy.py` and register it in `cruise_registry.py`.
