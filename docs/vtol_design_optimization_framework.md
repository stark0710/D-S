# VTOL Design Optimization Framework

## VTOL Optimization Philosophy
Automated design optimization resolves conflicting parameters across multiple engineering disciplines (aerodynamics, structures, propulsion, electrical). For example, increasing battery capacity improves range but increases aircraft weight, which in turn demands higher hover thrust and increases structural wing loading. The optimization philosophy centers on:
1. **Multi-Objective Tradeoffs**: Avoiding sub-optimal single-objective results by searching for a set of designs (Pareto Front) that balance range, endurance, weight, and reliability.
2. **Strict Constraint Handling**: Prioritizing engineering feasibility (e.g. static margins, thermal limits, structural margins) through active penalty scoring before evaluating objectives.
3. **Simultaneous Verification integration**: Pulling metrics directly from hover, transition, and cruise flight profiles to evaluate overall flight worthiness.

---

## Objective Functions
Supported optimization objectives evaluate design dimensions:
- **Maximum range**: Maximizing forward cruise range ($km$) under constraint boundaries.
- **Maximum endurance**: Maximizing continuous flight duration ($min$).
- **Minimum empty weight**: Minimizing empty structure weight ($kg$) to increase cargo payloads.
- **Maximum hover efficiency**: Minimizing hover power required through rotor disk area sizing.
- **Maximum reliability**: Minimizing component failure rates to maximize MTBF.

---

## Constraint Management
Constraints are managed via penalty functions to reject unfeasible candidates:
- **Structural limits**: g-load limit margin checks.
- **Power & Current limits**: Continuous current must not exceed ESC/wire limits.
- **CG boundaries**: Composite takeoff CG must remain between 15% and 35% MAC.
- **Flight feasibility**: Minimum thrust margin must exceed 1.30 to hover safely.

---

## Pareto Optimization
Multi-objective optimization uses NSGA-II to find non-dominated design candidate sets. Each candidate on the Pareto Front represents an optimal tradeoff, where no single objective can be improved without degrading another. Crowding distance calculations ensure candidates are spread evenly across the frontier.

---

## Sensitivity Analysis & Trade-off Analysis
- **Sensitivity Analysis**: Computes the gradient of objectives with respect to design variables (e.g. change in cruise power per unit change in wing aspect ratio):
  $$\frac{\partial P_{required}}{\partial AR} \approx \frac{P(AR + \Delta) - P(AR)}{\Delta}$$
  This isolates the variables that have the highest leverage over design improvements.
- **Trade-off Analysis**: Slices the Pareto front to compute compromising slopes (e.g., how much range is sacrificed to increase payload capability by 1.0 kg).

---

## Validation Assumptions
The validator enforces:
- **Convergence limits**: Confirms that optimizer loops converged within profile iteration limits.
- **Feasibility checks**: Rejects designs that exhibit constraint violations or penalties.
- **improvement validations**: Ensures the optimized design has improved fitness scores compared to base baselines.

---

## Extension Mechanism
To extend the framework:
1. **Integrate new optimizers**: Implement the `OptimizationStrategy` interface in `optimization_strategy.py` and register it in `optimization_registry.py`.
2. **Add variables/objectives**: Update variable dimensions in `design_variables.py` or customize fitness scoring algorithms in `objective_functions.py`.
