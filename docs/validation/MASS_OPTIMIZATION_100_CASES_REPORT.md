# Sprint 28 Mass Properties Engine Validation Report
---
## 1. Validation Campaign Executive Summary
- **Missions Audited**: 100
- **Successful Mass/Weight Sizing**: 100
- **Failed Sizing**: 0
- **Average Candidates Evaluated**: 24.0
- **Average Feasible Candidates**: 24.0
- **Average Rejected Candidates**: 0.0
- **Total Campaign Time**: 0.84 s

## 2. Engineering Verification
- **100% Mass Conserved Designs**: Every optimized aircraft layout maintains 100% mass conservation, where the sum of all 22 breakdown elements exactly matches MTOW.
- **MTOW Consistency**: Sized MTOW remains below the target limit constraint across all configurations.
- **Subsystem Completeness**: The weight breakdown contains non-zero masses for structures, propulsion, avionics, wiring, paint, fasteners, and safety margin.
- **Realistic Weight Fractions**: Payload, battery, and structural fractions fall well within physical bounds across all MTOW regimes.
- **3D Moments of Inertia**: Consistent principal moments of inertia calculated relative to the sized center of gravity.

## 3. Representative Sizing Sample Cases (First 15)
| Case ID | Category | Status | Empty Weight (kg) | Operating Weight (kg) | Sized MTOW (kg) | Payload Frac | Battery Frac | Struct Frac | Conserved? | Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| FW-001 | Research | SUCCESS | 6.432 kg | 7.232 kg | 9.232 kg | 0.217 | 0.087 | 0.524 | YES | 0.6892 |
| FW-002 | Racing | SUCCESS | 5.102 kg | 5.902 kg | 7.902 kg | 0.253 | 0.101 | 0.462 | YES | 0.7005 |
| FW-003 | Custom | SUCCESS | 5.893 kg | 6.693 kg | 8.693 kg | 0.230 | 0.092 | 0.501 | YES | 0.6964 |
| FW-004 | Training | SUCCESS | 5.777 kg | 6.577 kg | 8.577 kg | 0.233 | 0.093 | 0.496 | YES | 0.6977 |
| FW-005 | Agriculture | SUCCESS | 7.564 kg | 9.064 kg | 11.064 kg | 0.181 | 0.136 | 0.529 | YES | 0.6774 |
| FW-006 | Custom | SUCCESS | 6.371 kg | 7.171 kg | 9.171 kg | 0.218 | 0.087 | 0.521 | YES | 0.6775 |
| FW-007 | Cargo | SUCCESS | 6.9 kg | 7.7 kg | 9.7 kg | 0.206 | 0.082 | 0.542 | YES | 0.6853 |
| FW-008 | Agriculture | SUCCESS | 7.169 kg | 7.969 kg | 9.969 kg | 0.201 | 0.080 | 0.551 | YES | 0.686 |
| FW-009 | Survey | SUCCESS | 5.155 kg | 5.955 kg | 7.955 kg | 0.251 | 0.101 | 0.464 | YES | 0.6996 |
| FW-010 | Cargo | SUCCESS | 7.528 kg | 9.028 kg | 11.028 kg | 0.181 | 0.136 | 0.527 | YES | 0.6728 |
| FW-011 | Cargo | SUCCESS | 8.032 kg | 9.532 kg | 11.532 kg | 0.173 | 0.130 | 0.543 | YES | 0.6751 |
| FW-012 | Cargo | SUCCESS | 6.141 kg | 7.641 kg | 9.641 kg | 0.207 | 0.156 | 0.476 | YES | 0.6981 |
| FW-013 | Racing | SUCCESS | 5.304 kg | 6.104 kg | 8.104 kg | 0.247 | 0.099 | 0.473 | YES | 0.6975 |
| FW-014 | Surveillance | SUCCESS | 5.275 kg | 6.075 kg | 8.075 kg | 0.248 | 0.099 | 0.471 | YES | 0.6934 |
| FW-015 | Cargo | SUCCESS | 4.793 kg | 5.243 kg | 7.243 kg | 0.276 | 0.062 | 0.466 | YES | 0.7173 |
