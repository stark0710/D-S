# VTOL Electrical Power Engineering Framework

## 1. Electrical Engineering Philosophy

The **VTOL Electrical Power Engineering Framework** designs and sizes the complete electrical power architecture of the aircraft. It manages high-voltage ESC main power buses, low-voltage avionics buses (BECs), battery packaging (series/parallel configuration), circuit breakers, fuses protection, thermal heat dissipation, balance charging, and mission energy allocation.

---

## 2. Battery Sizing & Pack Sizing Methodology

The battery pack capacity and S/P cell configuration is determined from the target energy demand:
$$\text{Energy}_{\text{required}} = \text{Energy}_{\text{mission}} \cdot (1.0 + f_{\text{reserve}})$$

Where $f_{\text{reserve}}$ (defined by Strategy) is typically between $0.15$ and $0.30$.
*   **Series Cell Count ($S$)**: Sized to match ESC voltage specifications. For larger MTOW aircraft (>15 kg), a 12S layout is standard; otherwise, a 6S layout is used.
*   **Parallel Cell Count ($P$)**: Sized based on cell capacity to meet the overall Wh rating:
    $$P = \left\lceil \frac{\text{Energy}_{\text{required}}}{\text{Nominal Voltage} \cdot \text{Capacity}_{\text{cell}}} \right\rceil$$
*   **Chemistry Selection**: Optimized using a rule-based selection database:
    *   **LiPo**: Sized for high discharge rates (e.g. Cargo/Heavy Lift VTOLs).
    *   **Li-Ion**: Sized for ultra-long range wing flight where discharge C-rates are low.
    *   **LiHV**: Sized for survey/mapping operations balancing specific energy and discharge currents.

---

## 3. Mission Energy Budgeting & Power Distribution

### Power Budget
Draws are compiled across three primary operational states (Hover, Cruise, Transition):
*   **Vertical Lift Motors**: Sized under hover load; inactive in cruise; blended in transition.
*   **Forward Propulsion**: Sized under cruise load; inactive in hover; active during transition.
*   **Avionics & Servos**: Continuous background load.

### Power Distribution Buses
*   **HV ESC Bus**: Runs at battery nominal pack voltage to supply power to all speed controllers. Sized wire AWG gauge scales with maximum current demands:
    *   $I > 150\text{ A}$: 8 AWG.
    *   $80\text{ A} < I \le 150\text{ A}$: 10 AWG.
    *   $I \le 80\text{ A}$: 12 AWG.
*   **LV Avionics Rail**: Runs at 5.0V regulated via BECs.

---

## 4. Protection & Redundancy

*   **Protective Fuses**: Fuses are sized on the main battery lead and ESC branches to safeguard against current spikes:
    $$\text{Fuse rating} = 1.25 \cdot I_{\text{continuous}}$$
*   **BEC Redundancy**: A primary and secondary opto-isolated BEC supply the avionics rail. If the primary BEC experiences a fault, a dual-bus switchover failover takes place within $2.5$ ms.

---

## 5. Thermal & Charging Calculations

*   **Thermal Losses**: Sized cell resistance $R_{\text{int}} = \frac{S}{P} \cdot R_{\text{cell}}$ is used to calculate heat dissipation:
    $$P_{\text{heat}} = I^2 \cdot R_{\text{int}}$$
    If pack temperatures exceed $50^\circ\text{C}$, active cooling ventilation is requested.
*   **Charging Time**: Standard balancing charger rates default to 1C, requiring approximately $1.15$ hours to charge.

---

## 6. Validation Assumptions

The validator (`ElectricalValidator`) checks:
*   **Capacity reserve**: Sized battery Wh must exceed the mission energy demand plus reserve.
*   **Discharge C-rate limit**: Max hover current must not exceed cell peak discharge limits.
*   **Voltage compatibility**: Sized nominal pack voltage must be between $11.1$V and $60.0$V.

---

## 7. Extension Mechanism

To add a new electrical strategy:
1.  Inherit from `BaseElectricalStrategy` in `electrical_strategy.py`.
2.  Implement the required strategy attributes:
    *   `category`: `VTOLMissionCategory`
    *   `default_chemistry`: `str`
    *   `default_reserve_factor`: `float`
    *   `get_recommendations() -> List[str]`
3.  Register the strategy in the registry: `VTOLElectricalStrategyRegistry.register(category, strategy_instance)`.
