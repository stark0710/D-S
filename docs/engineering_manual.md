# Engineering Manual — Torq Wings Design Studio V3
## Production Release Sizing Principles & Equations

This document details the analytical sizing principles, physical equations, databases, and constraints frozen for the Fixed-Wing Design Studio V3.

---

## 1. MTOW Convergence Sizing Loop

The aircraft sizing is converged iteratively by updating the Maximum Takeoff Weight (MTOW) based on computed component weights. The loop terminates when the relative change in MTOW falls below the tolerance threshold ($1\%$):

$$\Delta_{\text{relative}} = \frac{|MTOW_{\text{new}} - MTOW_{\text{old}}|}{MTOW_{\text{old}}} \le 0.01$$

The weight breakdown is formulated as:

$$MTOW = W_{\text{structural}} + W_{\text{propulsion}} + W_{\text{avionics}} + W_{\text{battery}} + W_{\text{payload}}$$

---

## 2. Wing Sizing & Geometry Sizing

- **Aspect Ratio ($AR$)**: Relation of wingspan ($b$) to reference wing area ($S$):
  
  $$AR = \frac{b^2}{S}$$

- **Mean Aerodynamic Chord ($c_{\text{mac}}$)**:
  
  $$c_{\text{mac}} = \frac{2}{3} c_{\text{root}} \frac{1 + \lambda + \lambda^2}{1 + \lambda}$$
  
  where $\lambda = \frac{c_{\text{tip}}}{c_{\text{root}}}$ is the taper ratio.

- **Wing Loading ($\frac{W}{S}$)**: Sizing parameter dictating stall speed and lift capability:
  
  $$V_{\text{stall}} = \sqrt{\frac{2 g (MTOW / S)}{\rho C_{L,\text{max}}}}$$

---

## 3. Tail Volume Sizing Coefficients

The tail sizing uses volume coefficients to guarantee aerodynamic control authority:

- **Horizontal Tail Volume Coefficient ($V_h$)**:
  
  $$V_h = \frac{S_t l_t}{S c_{\text{mac}}}$$

- **Vertical Tail Volume Coefficient ($V_v$)**:
  
  $$V_v = \frac{S_v l_t}{S b}$$
  
  where $S_t$ is horizontal tail area, $S_v$ is vertical tail area, and $l_t$ is the tail moment arm (tail arm).

---

## 4. Propulsion & Sizing Balance

- **Required Cruise Thrust ($T_{\text{cruise}}$)**: Equals total cruise aerodynamic drag:
  
  $$T_{\text{cruise}} = D_{\text{cruise}} = \frac{MTOW \cdot g}{L/D}$$

- **Required Cruise Power ($P_{\text{cruise}}$)**:
  
  $$P_{\text{cruise}} = \frac{T_{\text{cruise}} V_{\text{cruise}}}{\eta_{\text{sys}}}$$
  
  where $\eta_{\text{sys}} = \eta_{\text{motor}} \cdot \eta_{\text{propeller}}$ is total propulsive system efficiency.

---

## 5. CG Balance & Longitudinal Stability

- **Center of Gravity Location ($x_{\text{CG}}$)**:
  
  $$x_{\text{CG}} = \frac{\sum m_i x_i}{\sum m_i}$$

- **Static Margin ($SM$)**: Measures pitch stability; must lie between $5\%$ and $25\%$ for certified designs:
  
  $$SM = \frac{x_{\text{NP}} - x_{\text{CG}}}{c_{\text{mac}}}$$
  
  where $x_{\text{NP}}$ is the aircraft Neutral Point.
