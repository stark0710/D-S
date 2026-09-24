# Fixed-Wing Design Pipeline — Phase 3 Forensic Validation Report

**Project**: Torq Wings Design Studio V3  
**Phase**: Phase 5.5 – Fixed-Wing Design Studio  
**Sprint**: Sprint 17 – Fixed-Wing Design Pipeline  
**Phase Target**: Phase 3 — Engineering Forensic Validation  
**Status**: `DIAGNOSTIC COMPLETED`  
**Date**: July 30, 2026  

---

## 1. Executive Summary

This forensic audit evaluates the current fixed-wing engineering capabilities and explains the anomalous results observed in Phase 2 for a nominal mapping mission requirement (Payload: 2.0 kg, Range: 60 km, Endurance: 90 min, Cruise speed: 95 km/h). 

The nominal sizing run converges to:
* **MTOW**: 24.9730 kg (excessively heavy for a 2 kg payload).
* **Wing span & Area**: 4.3874 m and 1.8332 m² (oversized).
* **Fuselage length**: 3.2910 m (oversized).
* **Static margin**: 139.2% of MAC (extremely nose-heavy, yet approved as "Verified").

This forensic validation traced every calculation through the pipeline to locate the root causes. We identified three primary engineering and software integration defects:
1. **Verification Engine Integration Defect**: The orchestrator checks compliance by querying the non-existent field `overall_compliance` on the `ComplianceReport` object, which default-falls back to `True`, silently bypassing all safety violations.
2. **CG Coordinate Datum Mismatch**: The battery placement balancing routine calculates a target CG relative to the wing leading edge, but treats it as nose-relative. This causes the target CG to be located near the nose, forcing the heavy battery (11.85 kg) to be clamped at the forward limit (0.10 m from nose), resulting in a genuine 139.2% static margin.
3. **Battery Sizing Feedback Loop**: The battery weight is sized using a static fraction of MTOW (48% for 90 min) rather than actual electrical energy required, producing a runaway compounding feedback loop.

---

## 2. Reproduction of the Nominal Diagnostic

Running the nominal mission requirements reproduces the exact diagnostic values reported in Phase 2:
* **Input Mission**: Mapping | Takeoff: Runway | Landing: Runway | Environment: Rural
* **Inputs**: Payload = 2.0 kg | Range = 60 km | Endurance = 90 min | Cruise speed = 95 km/h

### Sizing Outputs Summary
| Parameter | Sized Value | Status / Sanity Check |
| :--- | :--- | :--- |
| **MTOW** | **24.9730 kg** | Highly inflated for a 2.0 kg payload |
| **Wing Span** | **4.3874 m** | Extremely large for a small mapping UAV |
| **Wing Area** | **1.8332 m²** | Oversized |
| **Fuselage Length** | **3.2910 m** | Sized purely via wing span heuristic ($0.75 \times b$) |
| **Static Margin** | **139.20%** | Aerodynamically unstable/heavy trim drag (should be 5–15%) |
| **Verification Status** | **Verified / SUCCESS** | **FAILED SANITY CHECK** (should be Rejected) |
| **Iterations** | **19** | Converged under the 1% delta threshold |

---

## 3. MTOW Sizing Loop Trace

The table below traces the mass build-up and convergence across all 19 iterations of the synthesis loop. 

| Iter | Input MTOW (kg) | Wing Mass (kg) | Fuse Mass (kg) | Tail Mass (kg) | Struct Mass (kg) | Motor Mass (kg) | Prop Mass (kg) | ESC Mass (kg) | Prop Mass (kg) | Batt Mass (kg) | Avionics Mass (kg) | Payload Mass (kg) | Raw MTOW (kg) | Relaxed MTOW (kg) | Rel Delta (%) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5.0000 | 1.0396 | 1.9994 | 0.1216 | 3.1610 | 0.1400 | 0.0650 | 0.0000 | 0.2050 | 2.4000 | 0.2600 | 2.0000 | 8.0260 | 7.2695 | 45.3900% |
| 2 | 7.2695 | 1.5114 | 2.4111 | 0.1769 | 4.0990 | 0.2100 | 0.0650 | 0.0000 | 0.2750 | 3.4890 | 0.2600 | 2.0000 | 10.1230 | 9.4096 | 29.4394% |
| 3 | 9.4096 | 1.9564 | 2.7419 | 0.2290 | 4.9270 | 0.3100 | 0.0650 | 0.0000 | 0.3750 | 4.5170 | 0.2600 | 2.0000 | 12.0790 | 11.4116 | 21.2761% |
| 4 | 11.4116 | 2.3724 | 3.0200 | 0.2776 | 5.6700 | 0.3100 | 0.0650 | 0.0000 | 0.3750 | 5.4780 | 0.2600 | 2.0000 | 13.7830 | 13.1901 | 15.5850% |
| 5 | 13.1901 | 2.7423 | 3.2468 | 0.3210 | 6.3100 | 0.6200 | 0.0650 | 0.0000 | 0.6850 | 6.3310 | 0.2600 | 2.0000 | 15.5860 | 14.9870 | 13.6231% |
| 6 | 14.9870 | 3.1158 | 3.4614 | 0.3647 | 6.9420 | 0.6200 | 0.0650 | 0.0000 | 0.6850 | 7.1940 | 0.2600 | 2.0000 | 17.0810 | 16.5575 | 10.4791% |
| 7 | 16.5575 | 3.4423 | 3.6383 | 0.4030 | 7.4840 | 0.6200 | 0.0650 | 0.0000 | 0.6850 | 7.9480 | 0.2600 | 2.0000 | 18.3770 | 17.9221 | 8.2416% |
| 8 | 17.9221 | 3.7262 | 3.7854 | 0.4360 | 7.9480 | 0.6200 | 0.0650 | 0.0000 | 0.6850 | 8.6030 | 0.2600 | 2.0000 | 19.4960 | 19.1025 | 6.5863% |
| 9 | 19.1025 | 3.9715 | 3.9069 | 0.4646 | 8.3430 | 0.6200 | 0.0650 | 0.0000 | 0.6850 | 9.1690 | 0.2600 | 2.0000 | 20.4570 | 20.1184 | 5.3182% |
| 10 | 20.1184 | 4.1829 | 4.0095 | 0.4897 | 8.6820 | 0.6200 | 0.0650 | 0.0000 | 0.6850 | 9.6570 | 0.2600 | 2.0000 | 21.2840 | 20.9926 | 4.3453% |
| 11 | 20.9926 | 4.3646 | 4.0959 | 0.5109 | 8.9710 | 0.6200 | 0.0650 | 0.0000 | 0.6850 | 10.0760 | 0.2600 | 2.0000 | 21.9920 | 21.7421 | 3.5703% |
| 12 | 21.7421 | 4.5203 | 4.1688 | 0.5291 | 9.2180 | 0.6200 | 0.0650 | 0.0000 | 0.6850 | 10.4360 | 0.2600 | 2.0000 | 22.5990 | 22.3848 | 2.9560% |
| 13 | 22.3848 | 4.6539 | 4.2296 | 0.5448 | 9.4280 | 0.6200 | 0.0650 | 0.0000 | 0.6850 | 10.7450 | 0.2600 | 2.0000 | 23.1180 | 22.9347 | 2.4566% |
| 14 | 22.9347 | 4.7684 | 4.2809 | 0.5581 | 9.6070 | 0.6200 | 0.0650 | 0.0000 | 0.6850 | 11.0090 | 0.2600 | 2.0000 | 23.5610 | 23.4044 | 2.0480% |
| 15 | 23.4044 | 4.8661 | 4.3254 | 0.5696 | 9.7610 | 0.6200 | 0.0650 | 0.0000 | 0.6850 | 11.2340 | 0.2600 | 2.0000 | 23.9400 | 23.8061 | 1.7163% |
| 16 | 23.8061 | 4.9496 | 4.3619 | 0.5793 | 9.8910 | 0.6200 | 0.0650 | 0.0000 | 0.6850 | 11.4270 | 0.2600 | 2.0000 | 24.2630 | 24.1488 | 1.4395% |
| 17 | 24.1488 | 5.0207 | 4.3929 | 0.5878 | 10.0010 | 0.6200 | 0.0650 | 0.0000 | 0.6850 | 11.5910 | 0.2600 | 2.0000 | 24.5370 | 24.4399 | 1.2054% |
| 18 | 24.4399 | 5.0812 | 4.4199 | 0.5949 | 10.0960 | 0.6200 | 0.0650 | 0.0000 | 0.6850 | 11.7310 | 0.2600 | 2.0000 | 24.7720 | 24.6890 | 1.0192% |
| 19 | 24.6890 | 5.1330 | 4.4428 | 0.6008 | 10.1770 | 0.6200 | 0.0650 | 0.0000 | 0.6850 | 11.8510 | 0.2600 | 2.0000 | 24.9730 | 24.9020 | 0.8627% |

*Note: ESC mass is not modeled as a separate ComponentMass; ESC weight is absorbed into the Propulsion Pack or structural margins.*

### Analysis of Growth
The payload (2.0 kg), avionics (0.26 kg), and propeller (0.065 kg) are static. The growth is dominated by three main feedback terms:
1. **Battery Mass**: Sized as a fixed $48\%$ of the estimated MTOW.
2. **Wing Mass**: Sized linearly to wing area $S$, which in turn is sized linearly to MTOW due to the constant wing loading constraint (stall speed target = 45 km/h). This yields a wing mass fraction of **$20.5\%$ of MTOW**.
3. **Tail Mass**: Direct volume coefficient scaling ties horizontal and vertical tail area directly to wing area, creating another linear fraction of **$2.4\%$ of MTOW**.

Combined, the aircraft has a mass scaling coefficient of **$70.9\%$** ($0.48 + 0.205 + 0.024$). Adding the fuselage shell's non-linear scaling ($1.35 \times \text{length}$, which accounts for another $17.3\%$ at 25 kg), the aircraft has a total mass growth sensitivity multiplier of $\frac{1}{1 - 0.882} \approx 8.5$. 

---

## 4. Battery Forensics

### Sized Useful Load Composition
The useful load is calculated at **13.8510 kg**, which contains:
* **Payload Mass**: 2.0000 kg
* **Battery Mass**: 11.8510 kg
* **Fuel / Mission Equipment / Other**: 0.0000 kg

### Sizing and Performance Parameters
The parameters used or calculated by the pipeline for the battery and electrical systems are:
* **Required endurance**: 90 min (1.5 hours)
* **Cruise electrical power**: 934.7 W
* **Payload power draw**: 15.0 W
* **Avionics power draw**: 16.85 W
* **Total continuous power draw**: 966.55 W
* **Motor efficiency**: 82.0%
* **Propeller efficiency**: 65.0%
* **Propulsion efficiency (total)**: 53.3%
* **Battery usable fraction**: 85.0% (15% reserve margin applied in range/endurance calculations)
* **Specific energy**: 200.0 Wh/kg
* **Sized Battery Capacity**: $11.851\text{ kg} \times 200\text{ Wh/kg} = 2370.2\text{ Wh}$

### Core Findings
1. **Positive Feedback Sizing Defect**: The battery mass is calculated as `batt_mass = mtow_est * effective_batt_frac` in `MassPropertiesEngine.process_mass_design`. It is sized based on an arbitrary mission-category fraction (35% base, scaled to 48% due to flight time) rather than actual continuous power draw ($P_{\text{continuous}}$). This creates the severe positive feedback loop that balloons MTOW.
2. **Physical Sizing Comparison**: Sizing the battery based on physics yields:
   $$\text{Required Energy} = \frac{966.55\text{ W} \times 1.5\text{ hrs}}{0.85\text{ (usable fraction)}} = 1705.7\text{ Wh}$$
   $$\text{Required Battery Mass} = \frac{1705.7\text{ Wh}}{200.0\text{ Wh/kg}} = 8.528\text{ kg}$$
   *(If no reserve fraction is applied, required energy is $1449.8\text{ Wh}$, requiring a **$7.249\text{ kg}$** battery).*
   The engine selects a battery that is **$11.851\text{ kg}$** (63.5% heavier than physically required).
3. **Dimensional Consistency**: Wh / (Wh/kg) = kg is dimensionally correct. Efficiency is not applied twice in the performance calculations. Endurance minutes are correctly converted to hours. Reserve margins are applied consistently.

---

## 5. Structural Mass Forensics

The total structural mass in the converged run is **10.1770 kg**, which breaks down as:
* **Wing structure**: 5.1330 kg
* **Fuselage structure**: 4.4428 kg
* **Horizontal tail**: 0.3320 kg
* **Vertical tail**: 0.2680 kg
* **Landing gear / Reinforcements / Misc**: 0.0000 kg

### Sizing Equations Audit
The structural masses are sized via the following linear equations in `MassPropertiesEngine`:

```
Wing Mass:
W_wing = S * 2.8
Inputs: S = 1.8332 m2
Expected units: Area (m2), Density (kg/m2)
Actual units supplied: reference_area_m2 (1.8332), multiplier (2.8)
Output: 5.1330 kg

Tail Mass:
W_h = S_h * 2.2
W_v = S_v * 2.2
Inputs: S_h = 0.151 m2, S_v = 0.122 m2
Expected units: Area (m2), Density (kg/m2)
Actual units supplied: area_m2, multiplier (2.2)
Output: W_h = 0.332 kg, W_v = 0.268 kg (Sum = 0.601 kg)

Fuselage Mass:
W_fuse = L_fuse * 1.35
Inputs: L_fuse = 3.2910 m
Expected units: Length (m), linear density (kg/m)
Actual units supplied: length_m, multiplier (1.35)
Output: 4.4430 kg
```

### Critical Unit Findings
* **No Imperial Unit Conversions**: The equations are not Raymer or Roskam statistical formulations (which expect imperial units like lbs, ft, knots). The Raymer equations described in the Phase 1 Audit were **never actually implemented in the codebase**. 
* **Simplified Heuristics**: The code uses simplified metric mass density constants ($2.8\text{ kg/m²}$ wing, $2.2\text{ kg/m²}$ tail, $1.35\text{ kg/m}$ fuselage). Because they are simple linear factor multiplications, no imperial-to-metric unit errors occur.

---

## 6. Wing Sizing Trace

The table below traces the wing planform parameters across the loop:

| Iter | MTOW (kg) | Wing Loading (kg/m) | Target Stall (km/h) | CLmax | Air Density (kg/m) | Wing Area (m) | Aspect Ratio | Span (m) | Root Chord (m) | Tip Chord (m) | MAC (m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5.0000 | 13.4674 | 45.0 | 1.4 | 1.2075 | 0.3713 | 10.50 | 1.9744 | 0.2507 | 0.1254 | 0.1950 |
| 2 | 7.2695 | 13.4674 | 45.0 | 1.4 | 1.2075 | 0.5398 | 10.50 | 2.3807 | 0.3023 | 0.1512 | 0.2351 |
| 3 | 9.4096 | 13.4674 | 45.0 | 1.4 | 1.2075 | 0.6987 | 10.50 | 2.7086 | 0.3439 | 0.1720 | 0.2675 |
| 4 | 11.4116 | 13.4674 | 45.0 | 1.4 | 1.2075 | 0.8473 | 10.50 | 2.9828 | 0.3788 | 0.1894 | 0.2946 |
| 5 | 13.1901 | 13.4674 | 45.0 | 1.4 | 1.2075 | 0.9794 | 10.50 | 3.2068 | 0.4072 | 0.2036 | 0.3167 |
| 6 | 14.9870 | 13.4674 | 45.0 | 1.4 | 1.2075 | 1.1128 | 10.50 | 3.4183 | 0.4341 | 0.2170 | 0.3376 |
| 7 | 16.5575 | 13.4674 | 45.0 | 1.4 | 1.2075 | 1.2294 | 10.50 | 3.5929 | 0.4562 | 0.2281 | 0.3549 |
| 8 | 17.9221 | 13.4674 | 45.0 | 1.4 | 1.2075 | 1.3308 | 10.50 | 3.7381 | 0.4747 | 0.2373 | 0.3692 |
| 9 | 19.1025 | 13.4674 | 45.0 | 1.4 | 1.2075 | 1.4184 | 10.50 | 3.8592 | 0.4901 | 0.2450 | 0.3812 |
| 10 | 20.1184 | 13.4674 | 45.0 | 1.4 | 1.2075 | 1.4939 | 10.50 | 3.9605 | 0.5029 | 0.2515 | 0.3912 |
| 11 | 20.9926 | 13.4674 | 45.0 | 1.4 | 1.2075 | 1.5588 | 10.50 | 4.0456 | 0.5137 | 0.2569 | 0.3996 |
| 12 | 21.7421 | 13.4674 | 45.0 | 1.4 | 1.2075 | 1.6144 | 10.50 | 4.1172 | 0.5228 | 0.2614 | 0.4066 |
| 13 | 22.3848 | 13.4674 | 45.0 | 1.4 | 1.2075 | 1.6621 | 10.50 | 4.1776 | 0.5305 | 0.2652 | 0.4126 |
| 14 | 22.9347 | 13.4674 | 45.0 | 1.4 | 1.2075 | 1.7030 | 10.50 | 4.2286 | 0.5370 | 0.2685 | 0.4176 |
| 15 | 23.4044 | 13.4674 | 45.0 | 1.4 | 1.2075 | 1.7379 | 10.50 | 4.2717 | 0.5424 | 0.2712 | 0.4219 |
| 16 | 23.8061 | 13.4674 | 45.0 | 1.4 | 1.2075 | 1.7677 | 10.50 | 4.3082 | 0.5471 | 0.2735 | 0.4255 |
| 17 | 24.1488 | 13.4674 | 45.0 | 1.4 | 1.2075 | 1.7931 | 10.50 | 4.3391 | 0.5510 | 0.2755 | 0.4286 |
| 18 | 24.4399 | 13.4674 | 45.0 | 1.4 | 1.2075 | 1.8147 | 10.50 | 4.3652 | 0.5543 | 0.2772 | 0.4311 |
| 19 | 24.6890 | 13.4674 | 45.0 | 1.4 | 1.2075 | 1.8332 | 10.50 | 4.3874 | 0.5571 | 0.2786 | 0.4333 |

### Mathematical Consistency Check
The wing loading equation is:
$$\frac{W}{S} = \frac{0.5 \cdot \rho \cdot V_{\text{stall}}^2 \cdot C_{L,\text{max}}}{g}$$
Using $\rho = 1.2075\text{ kg/m³}$ (density at 150m), $V_{\text{stall}} = \frac{45}{3.6} = 12.5\text{ m/s}$, $C_{L,\text{max}} = 1.4$, and $g = 9.80665\text{ m/s²}$:
$$\frac{W}{S} = \frac{0.5 \times 1.2075 \times 12.5^2 \times 1.4}{9.80665} = 13.4674\text{ kg/m²}$$
The wing area is:
$$S = \frac{\text{MTOW}}{\frac{W}{S}} = \frac{24.6890\text{ kg}}{13.4674\text{ kg/m²}} = 1.83323\text{ m²}$$
The wingspan is:
$$b = \sqrt{S \cdot AR} = \sqrt{1.83323 \times 10.5} = 4.38736\text{ m}$$
This is 100% mathematically consistent. The $1.833\text{ m²}$ wing is physically correct for a $24.7\text{ kg}$ aircraft stalling at $45\text{ km/h}$. The large size is a direct consequence of the inflated MTOW.

---

## 7. Fuselage Sizing Trace

The fuselage length converged to **3.2910 m** because of the following heuristic in `FuselageSizer.size_fuselage_envelope`:
```python
else:
    length = wing_geom.span_m * 0.75
```
Since the wing span $b = 4.3874\text{ m}$, the length is $4.3874 \times 0.75 = 3.29055\text{ m}$, which rounds to **$3.291\text{ m}$**. 
* **Driver**: Sizing is driven purely by a wing geometry heuristic (75% of wingspan). It is not driven by packaging or tail volume.
* **Dependencies**: The fuselage length depends on wingspan, which depends on wing area, which depends on MTOW, creating a sequential downstream dependency but no circular math inside the fuselage module itself.

---

## 8. Propulsion Forensics

The propulsion parameters for the nominal converged iteration are:
* **MTOW (Input)**: 24.6890 kg (Sizing MTOW)
* **Required Cruise Thrust**: 18.88 N
* **Required Maximum Thrust**: 84.74 N
* **Thrust-to-Weight (T/W) actual**: 0.48 (takeoff thrust capability)
* **Cruise Velocity**: 26.39 m/s (95.0 km/h)
* **Lift-to-Drag Ratio (L/D)**: 11.89
* **Propulsive Efficiency**: 65.0%
* **Motor Efficiency**: 82.0%
* **Total System Efficiency**: 53.3%
* **Required Cruise Electrical Power**: 934.7 W
* **Selected Motor**: KDE Direct 7215XF (Motor mass: 0.620 kg)
* **Selected Propeller**: 18x10 APC
* **Battery Voltage**: 44.4 V
* **Current Draw**: 21.05 A

### Independent Verification
1. **Cruise Thrust**:
   $$T_{\text{cruise}} = \frac{W}{\frac{L}{D}} = \frac{24.9730\text{ kg} \times 9.80665\text{ m/s²}}{11.89} = 20.60\text{ N}$$
   *The engine outputs $18.88\text{ N}$. The difference is because the propulsion engine uses an estimated L/D ($S_{\text{eff}} \times 0.18 = 12.82$) instead of the actual performance polar ($11.89$), and sizes using the iteration's input MTOW ($24.6890\text{ kg}$).*
2. **Cruise Power**:
   $$P_{\text{cruise, elec}} = \frac{T_{\text{cruise}} \cdot V}{\eta_{\text{total}}} = \frac{18.88\text{ N} \times 26.39\text{ m/s}}{0.533} = 934.79\text{ W}$$
   This matches the engine's output power of **$934.7\text{ W}$** exactly. No unit conversion bugs exist in this part of the propulsion engine.

---

## 9. Center of Gravity (CG) Forensics

The coordinate system is defined with $X = 0$ at the fuselage nose, moving aft.

### Component Mass and Moment Table (Nominal Sized Aircraft)
| Component | Mass $m_i$ (kg) | $X_i$ Coordinate (m) | $Y_i$ (m) | $Z_i$ (m) | Moment $m_i X_i$ (kg·m) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Wing Structure** | 5.1330 | 1.1610 | 0.000 | 0.000 | 5.9594 |
| **Tail Structure** | 0.6010 | 3.1710 | 0.000 | 0.050 | 1.9058 |
| **Fuselage Shell** | 4.4430 | 1.5140 | 0.000 | -0.020 | 6.7267 |
| **Propulsion Pack** | 0.6850 | 3.2310 | 0.000 | 0.000 | 2.2132 |
| **Avionics Payload** | 0.2600 | 1.1610 | 0.000 | 0.020 | 0.3019 |
| **Energy Battery** | 11.8510 | 0.1000 | 0.000 | -0.040 | 1.1851 |
| **Mission Payload** | 2.0000 | 0.0930 | 0.000 | -0.050 | 0.1860 |
| **Sum / CG** | **24.9730** | **0.7400** | **0.000** | **-0.022** | **18.4781** |

$$\text{Calculated } X_{\text{CG}} = \frac{\sum m_i X_i}{\sum m_i} = \frac{18.4781\text{ kg·m}}{24.9730\text{ kg}} = 0.7400\text{ m from nose}$$

### Geometrical References
* Fuselage Length ($L$): 3.2910 m
* Wing Attachment position from nose ($X_{\text{LE, root}}$): 1.0530 m
* Mean Aerodynamic Chord ($MAC$): 0.4333 m
* Wing Quarter-Chord relative to Root LE ($X_{\text{qc, root}}$): 0.1083 m ($0.25 \times MAC$)
* Wing Global Quarter-Chord ($X_{\text{qc, global}}$): $1.0530 + 0.1083 = 1.1613$ m from nose

### CG % MAC Calculations
* CG relative to Wing LE: $0.7400 - 1.0530 = -0.3130$ m
* **CG X expressed as % MAC**:
  $$\text{CG}_{\% MAC} = \frac{X_{\text{CG}} - X_{\text{LE, root}}}{MAC} \times 100 = \frac{0.7400 - 1.0530}{0.4333} \times 100 = \mathbf{-72.24\%}$$

### Root Cause of Forward CG
The target CG for battery balancing in `MassPropertiesEngine` was calculated as:
$$\text{target\_cg\_x} = X_{\text{qc, root}} + 0.24 \cdot MAC = 0.1083 + 0.24 \times 0.4333 = 0.2123\text{ m from nose}$$
This formula **neglects the wing attachment coordinate ($wing\_x = 1.053\text{ m}$)**. This coordinate system bug caused the solver to try to place the CG at **$0.212\text{ m}$** from the nose. To try to pull the CG this far forward, the calculated battery position `batt_x` resulted in a negative coordinate, which was then clamped to the minimum limit of **$0.100\text{ m}$**. 

Because the heavy battery (11.851 kg) and payload (2.000 kg) are placed at the very front of the aircraft (at $X = 0.10$ m and $0.093$ m respectively), they pull the actual CG forward to $0.74\text{ m}$, placing it **$31.3\text{ cm}$ in front of the wing leading edge**.

---

## 10. Neutral Point Forensics

The inputs used in the neutral point calculation are:
* Wing leading edge position ($X_{\text{LE}}$): 1.0530 m
* Wing mean aerodynamic chord ($MAC$): 0.4333 m
* Wing quarter-chord location relative to root LE: 0.1083 m
* Wing global quarter-chord: 1.1613 m
* Conventional Tail neutral point shift coefficient (`np_pct`): 0.42 (applied because Conventional tail exists)

### Calculation
Since $wing\_x > 0$:
$$X_{\text{NP}} = X_{\text{qc, global}} + (0.42 \cdot MAC) = 1.1613 + (0.42 \times 0.4333) = 1.3433\text{ m}$$
Expressed as a percentage of MAC from the wing leading edge:
$$\text{NP}_{\% MAC} = \frac{X_{\text{NP}} - X_{\text{LE}}}{MAC} \times 100 = \frac{1.3433 - 1.0530}{0.4333} \times 100 = \mathbf{66.99\%}$$

---

## 11. Static Margin Calculation

The static margin is computed as:
$$\text{Static Margin} = \frac{X_{\text{NP}} - X_{\text{CG}}}{MAC} \times 100$$
Using $X_{\text{NP}} = 1.3433\text{ m}$ and $X_{\text{CG}} = 0.7400\text{ m}$:
$$\text{Static Margin} = \frac{1.3433 - 0.7400}{0.4333} \times 100 = \frac{0.6033}{0.4333} \times 100 = \mathbf{139.23\%}$$

### Sanity Check
This value is a **genuine calculated value (A)** caused by a **coordinate datum bug (C)** and a **CG-position bug (E)**. The coordinate mismatch forced the battery to be placed at the extreme nose of the aircraft, shifting the CG to $0.74$ m and leading to the $139.2\%$ static margin.

---

## 12. Verification Engine Forensics

The verification engine incorrectly reported a status of **Verified** despite the excessive $139.2\%$ static margin due to two main defects:

### 1. The `overall_compliance` Attribute Bug
In `fixed_wing_design_pipeline.py` (lines 381-382), the orchestrator checks:
```python
verif_report = getattr(context.verification_result, "compliance_report", None)
verif_passed = getattr(verif_report, "overall_compliance", True) if verif_report else True
```
However, the `ComplianceReport` class (`backend/design/fixed_wing/verification/compliance_report.py`) defines the compliance flag as **`is_fully_compliant`**, not `overall_compliance`. Because `overall_compliance` does not exist, `getattr` falls back to the default of `True`, causing the pipeline to assume verification passed.

### 2. Stability Checker Logic Gap
In `backend/design/fixed_wing/verification/stability_checker.py`, the `check_stability_suitability` method contains:
```python
if mass_res.static_margin < 0.05:
    failures.append(...)
elif mass_res.static_margin > 0.25:
    # excessive stability is a warning, not failure
    pass
```
Excessive static margin (> 25%) only triggers a warning in the `MassValidator` but is treated as a `pass` by the verification engine's `StabilityChecker`. Since it is not added to the `violations` list, `is_fully_compliant` remains `True` (compliance score is 100.0% because mass properties warnings are not pulled into the verification engine warnings).

---

## 13. Convergence Contract Audit

* **Production Contract**: The numerical convergence contract requires the relative MTOW change to be $\le 1\%$ (defined as `DEFAULT_CONVERGENCE_TOLERANCE: float = 0.01` in `convergence.py`).
* **Test Suite Inconsistency**: In `tests/design/fixed_wing/pipeline/test_fixed_wing_pipeline.py`, line 196:
  `pipeline = FixedWingDesignPipeline(tolerance=0.05) # 5% tolerance`
  But the docstring of the test asserts: `"Verify pipeline terminates as soon as relative MTOW change is <= 1%."`
  The test overrides the tolerance to 5% while the docstring claims to test 1%. The actual production pipeline uses 1%.

---

## 14. Independent Hand Calculations

We perform independent calculations using the final converged aircraft parameters ($24.973\text{ kg}$ MTOW) to evaluate the percentage difference from the engine outputs:

| Parameter | Engine Output | Independent Physics Sizing | % Difference | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **Wing Area ($S$)** | 1.8332 m² | 1.8543 m² (from $V_{\text{stall}}$) | **-1.14%** | Engine uses final iteration input MTOW (24.689 kg) |
| **Wing Loading ($W/S$)** | 13.47 kg/m² | 13.47 kg/m² | **0.00%** | Consistent |
| **Aspect Ratio ($AR$)** | 10.50 | 10.50 | **0.00%** | Consistent |
| **Cruise $C_L$** | 0.380 | 0.380 | **0.00%** | Consistent |
| **Cruise Thrust ($T$)** | 18.88 N | 20.60 N | **-8.35%** | Engine uses estimated L/D (12.82) instead of polar L/D (11.89) |
| **Cruise Power ($P_{\text{elec}}$)**| 934.70 W | 1019.77 W | **-8.34%** | Propulsion thrust mismatch cascades to power |
| **Required Energy** | 2370.2 Wh | 1449.8 Wh (no reserve)<br>1705.7 Wh (with reserve) | **+63.48%**<br>**+38.96%** | Compounding feedback loop inflation |
| **Battery Mass ($M_b$)** | 11.851 kg | 7.249 kg (no reserve)<br>8.528 kg (with reserve) | **+63.48%**<br>**+38.96%** | Sized as 48% MTOW fraction instead of energy equation |
| **Center of Gravity ($X_{\text{CG}}$)**| 0.740 m | 0.740 m | **0.00%** | Moments match coordinates exactly |
| **Static Margin ($SM$)** | 139.20% | 139.25% | **-0.04%** | Consistent with forward CG position |

---

## 15. Control Mission Sizing Results

We executed the pipeline under 4 distinct control missions to evaluate scaling behavior:

| Parameter | CONTROL A | CONTROL B | CONTROL C (Nominal) | CONTROL D |
| :--- | :---: | :---: | :---: | :---: |
| **Payload (kg)** | 0.5 | 1.0 | 2.0 | 5.0 |
| **Range (km)** | 20.0 | 40.0 | 60.0 | 100.0 |
| **Endurance (min)** | 30.0 | 60.0 | 90.0 | 120.0 |
| **Cruise Speed (km/h)** | 60.0 | 75.0 | 95.0 | 100.0 |
| **Final MTOW (kg)** | **FAILED** | **10.6950** | **24.9730** | **FAILED** |
| **Payload Fraction** | — | 9.35% | 8.01% | — |
| **Battery Fraction** | — | 34.59% | 47.46% | — |
| **Structural Fraction** | — | 50.13% | 40.75% | — |
| **Wing Span (m)** | — | 2.8705 | 4.3874 | — |
| **Fuselage Length (m)** | — | 2.1530 | 3.2910 | — |
| **CG % MAC (wing LE)** | — | -29.28% | -72.24% | — |
| **NP % MAC (wing LE)** | — | 67.01% | 66.99% | — |
| **Static Margin** | — | 96.40% | 139.20% | — |
| **Verification Result** | — | Verified | Verified | — |
| **Iterations** | — | 15 | 19 | — |

### Failure Analysis
* **CONTROL A**: Failed with `SIZING_INFEASIBLE` at iteration 1. The cruise speed (60 km/h) is below the minimum safe cruise boundary (80.4 km/h). Because the stall speed target is hardcoded to $45\text{ km/h}$ in the mission engine translation, the airfoil's actual low maximum lift coefficient ($C_{L,\text{max}}$) raises the stall speed to $67\text{ km/h}$. Cruising at $60\text{ km/h}$ is aerodynamically impossible.
* **CONTROL D**: Failed with `SIZING_INFEASIBLE` at iteration 1. The telemetry data link range limit in the avionics database is $80\text{ km}$, which violates the $100\text{ km}$ communication range constraint for the mission. This is a component database limitation.

---

## 16. Defect Classification and Severity Matrix

All identified anomalies are classified below by severity and type:

| ID | Issue Description | Classification | Severity | Status |
| :--- | :--- | :--- | :---: | :---: |
| **BUG-01** | Pipeline verification checks non-existent `overall_compliance` attribute | PIPELINE INTEGRATION BUG | **CRITICAL** | Identified |
| **BUG-02** | Coordinate datum mismatch in battery placement CG balancing | CG-POSITION / DATUM BUG | **HIGH** | Identified |
| **BUG-03** | Stability margin exceeding 25% is ignored by the stability checker | VALIDATOR GAP | **HIGH** | Identified |
| **BUG-04** | Battery sized via MTOW fraction instead of required energy | BAD DEFAULT ASSUMPTION | **HIGH** | Identified |
| **BUG-05** | Takeoff roll equation is missing air density ($\rho$) and has unit errors | EQUATION IMPLEMENTATION BUG | **MEDIUM** | Identified |
| **BUG-06** | Landing roll equation is missing gravity ($g$) in numerator | EQUATION IMPLEMENTATION BUG | **MEDIUM** | Identified |
| **BUG-07** | Test 9 convergence tolerance and docstring mismatch | RESULT-MAPPING BUG | **LOW** | Identified |
| **BUG-08** | Propulsion engine uses estimated L/D instead of actual polar L/D | COMPONENT INTEGRATION BUG | **LOW** | Identified |

---

## 17. Defect Locations

The table below lists the files and functions responsible for each defect:

| ID | File Path | Class / Function | Line Numbers |
| :--- | :--- | :--- | :--- |
| **BUG-01** | [fixed_wing_design_pipeline.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/pipeline/fixed_wing_design_pipeline.py) | `FixedWingDesignPipeline.execute` | L381-382 |
| **BUG-02** | [mass_properties_engine.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/mass_properties/mass_properties_engine.py) | `MassPropertiesEngine.process_mass_design` | L126-138 |
| **BUG-03** | [stability_checker.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/verification/stability_checker.py) | `StabilityChecker.check_stability_suitability` | L30-32 |
| **BUG-04** | [mass_properties_engine.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/mass_properties/mass_properties_engine.py) | `MassPropertiesEngine.process_mass_design` | L124-125 |
| **BUG-05** | [flight_performance_engine.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/flight_performance/flight_performance_engine.py) | `FlightPerformanceEngine.process_performance_design` | L158 |
| **BUG-06** | [flight_performance_engine.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/flight_performance/flight_performance_engine.py) | `FlightPerformanceEngine.process_performance_design` | L172 |
| **BUG-07** | [test_fixed_wing_pipeline.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/tests/design/fixed_wing/pipeline/test_fixed_wing_pipeline.py) | `test_9_pipeline_terminates_on_convergence` | L185-203 |
| **BUG-08** | [propulsion_engine.py](file:///c:/Users/acer/Documents/torqwings%20studio%20v2/backend/design/fixed_wing/propulsion/propulsion_engine.py) | `PropulsionEngine.process_propulsion_design` | L100-102 |

---

## 18. Recommended Corrections

To secure the engineering correctness of the pipeline, we recommend implementing the following modifications:

### Correction for BUG-01 (Pipeline Verification Check)
Update `fixed_wing_design_pipeline.py` to query `is_fully_compliant` instead of `overall_compliance`:
```python
# In fixed_wing_design_pipeline.py:
verif_report = getattr(context.verification_result, "compliance_report", None)
verif_passed = getattr(verif_report, "is_fully_compliant", False) if verif_report else False
```

### Correction for BUG-02 (CG Coordinate Datum)
Modify the target CG and wing structure moment calculation in `mass_properties_engine.py` to account for the wing attachment offset `wing_attachment_x_m` (let's define it as `wing_x`):
```python
# In mass_properties_engine.py:
wing_x = getattr(f_geom, 'wing_attachment_x_m', 0.35 * f_geom.length_m)
w_x_pos = wing_x + wing_geom.quarter_chord_x_m

target_cg_x = wing_x + wing_geom.quarter_chord_x_m + (0.24 * wing_geom.mean_aerodynamic_chord_m)

non_batt_moment = (w_mass * (wing_x + wing_geom.quarter_chord_x_m + 0.04) +
                     t_mass * (f_geom.length_m - 0.12) +
                     f_mass * (f_geom.length_m * 0.46) +
                     p_mass * motor_x +
                     av_mass * av_x)
```

### Correction for BUG-03 (Stability Checker Limits)
Update `StabilityChecker` in `stability_checker.py` to treat static margins greater than 25% as compliance violations rather than passing silently:
```python
# In stability_checker.py:
elif mass_res.static_margin > 0.25:
    failures.append(
        f"Excessive static stability margin ({mass_res.static_margin*100:.1f}%). "
        "The aircraft is excessively nose-heavy, causing high trim drag and limited pitch elevator control authority."
    )
```

### Correction for BUG-04 (Battery Sizing Physics)
Modify `MassPropertiesEngine` to calculate battery mass based on actual mission energy required rather than a static MTOW fraction:
```python
# In mass_properties_engine.py:
# Sized battery / fuel mass based on flight time & power draw
p_av = requirements.avionics_result.power_analysis.continuous_power_w
p_pay = requirements.payload_result.payload_analysis.power_consumption_w
p_cruise = requirements.propulsion_result.power_analysis.required_cruise_power_w

required_energy_wh = (p_cruise + p_av + p_pay) * (m_profile.flight_time_min / 60.0)
# Apply 15% reserve margin (85% usable depth of discharge)
battery_energy_wh = required_energy_wh / 0.85

# specific energy of 200 Wh/kg
batt_mass = battery_energy_wh / 200.0
```

### Correction for BUG-05 & BUG-06 (Takeoff & Landing Roll equations)
Fix the dimensional errors in the flight roll equations in `flight_performance_engine.py`:
```python
# In flight_performance_engine.py:
# Takeoff roll (correct SI units including density rho):
takeoff_dist = (1.21 * wing_geom.wing_loading_kg_m2) / (rho * cl_takeoff * max(0.1, t_to_w))

# Landing roll (correct SI units with g canceling out):
landing_dist = (0.66 * wing_geom.wing_loading_kg_m2) / (rho * cl_max_landing * braking_coefficient)
```

---

## 19. Freeze Recommendation

### Safely Frozen? **NO**
Phase 2 **cannot safely be frozen** in its current state. While the individual software interfaces are well-orchestrated and tests pass, the pipeline has critical engineering defects that produce aerodynamically invalid aircraft designs (unstable/nose-heavy CG, oversized components, incorrect landing/takeoff performance metrics) and silently passes them as valid. 

**Recommendation**: Authorize the Phase 3 corrections outlined above to fix the pipeline defects and secure engineering correctness before freezing the orchestrator foundation.
