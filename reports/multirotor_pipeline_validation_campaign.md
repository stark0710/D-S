# Multirotor Pipeline 20-Case Validation Campaign Report

This report summarizes the design synthesis and verification campaign of the **Sprint 43 Multirotor V1 Design Pipeline** over **20 representative test cases**.

## Summary
*   **Total Test Cases**: 20
*   **Successful Designs**: 11/20
*   **Validation Status**: Verified and Sized

## Campaign Ledger
| Case ID | Case Description | Success | Status Code | Iterations | Sized MTOW (kg) | Diagnostics / Errors |
|---|---|---|---|---|---|---|
| 1 | Small photography quad | ✓ YES | SUCCESS | 2 | 1.52 | None |
| 2 | Mapping quad | ✓ YES | SUCCESS | 2 | 2.50 | None |
| 3 | Inspection quad | ✓ YES | SUCCESS | 2 | 2.30 | None |
| 4 | Survey quad | ✓ YES | SUCCESS | 2 | 2.70 | None |
| 5 | Security quad | ✓ YES | SUCCESS | 2 | 2.00 | None |
| 6 | Long-endurance quad | ✓ YES | SUCCESS | 2 | 1.90 | None |
| 7 | Heavy-payload quad | ✓ YES | SUCCESS | 2 | 6.96 | None |
| 8 | Cargo quad | ✓ YES | SUCCESS | 2 | 7.23 | None |
| 9 | Hexacopter | ✗ NO | CONVERGENCE_FAILED | 15 | 0.00 | Takeoff weight and battery sizing metrics did not converge within the maximum iterations limit. |
| 10 | Octocopter | ✗ NO | MASS_INFEASIBLE | 2 | 0.00 | Mass properties sizing failed: MassPropertiesEngine failed: No feasible design candidates found. |
| 11 | Coaxial configuration | ✗ NO | MASS_INFEASIBLE | 2 | 0.00 | Mass properties sizing failed: MassPropertiesEngine failed: No feasible design candidates found. |
| 12 | Lightweight case | ✓ YES | SUCCESS | 2 | 1.60 | None |
| 13 | High-payload case | ✗ NO | MASS_INFEASIBLE | 2 | 0.00 | Mass properties sizing failed: MassPropertiesEngine failed: No feasible design candidates found. |
| 14 | Long-endurance case | ✓ YES | SUCCESS | 2 | 1.70 | None |
| 15 | Near-limit case | ✗ NO | PROPULSION_INFEASIBLE | 1 | 0.00 | Propeller selection failed in iteration 1: PropellerOptimizer failed: No feasible design candidates found. |
| 16 | Invalid requirements | ✗ NO | INVALID_REQUIREMENTS | 0 | 0.00 | Payload weight must be greater than 0 kg. Provided: -0.5 kg.; Target flight time must be greater than 0 minutes. Provided: 0.0 min.; Target range must be greater than 0 km. Provided: -10.0 km.; Cruise speed must be greater than 0 km/h. Provided: 0.0 km/h. |
| 17 | Database limitation | ✗ NO | FRAME_INFEASIBLE | 0 | 0.00 | No catalog frames match the configuration & wheelbase constraints. |
| 18 | Incompatible frame case | ✓ YES | SUCCESS | 2 | 1.80 | None |
| 19 | Propulsion infeasible case | ✗ NO | FRAME_INFEASIBLE | 0 | 0.00 | No catalog frames match the configuration & wheelbase constraints. |
| 20 | Verification failure case | ✗ NO | PROPULSION_INFEASIBLE | 1 | 0.00 | Propeller selection failed in iteration 1: PropellerOptimizer failed: No feasible design candidates found. |
