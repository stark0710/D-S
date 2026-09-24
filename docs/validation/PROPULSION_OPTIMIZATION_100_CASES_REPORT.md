# Sprint 26 Propulsion Optimization Engine Validation Report
---
## 1. Validation Campaign Executive Summary
- **Missions Audited**: 100
- **Successful Propulsion Designs**: 100
- **Failed Designs (no feasible candidate)**: 0
- **Average Candidates Generated per Mission**: 411.0
- **Average Feasible Candidates per Mission**: 200.3
- **Average Rejected Candidates per Mission**: 210.7
- **Total Campaign Time**: 70.93 s

## 2. Engineering Verification
- **100% Compatible Propulsion Systems**: Every successful aircraft has a fully compatible electrical configuration.
- **Power Margin**: Motor max power exceeds sized climb power.
- **Current Margin**: Climb current is below ESC and motor max current ratings.
- **Battery Margin**: Current draw never exceeds battery continuous C-rate discharge capability.
- **ESC Margin**: ESC ratings match or exceed motor full current draws.
- **Motor Margin**: All brushless motors operate safely within thermal current envelopes.
- **Static Thrust**: All takeoff thrust requirements are satisfied.
- **Estimated Endurance**: Flight time matches energy reserves (80% DOD LiPo/LiHV/Li-Ion limit).

## 3. Representative Optimization Sample Cases (First 15)
| Case ID | Status | Motor | Propeller | ESC | Battery | Voltage (V) | Static Thrust (N) | Endurance (min) | Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| FW-001 | SUCCESS | KDE Direct 7215XF | 18x10 APC | 80A BLHeli_32 | LiHV 12S 16000mAh 40C Pack | 45.6 | 115.26 | 163.9 | 0.7295 |
| FW-002 | SUCCESS | KDE Direct 7215XF | 18x10 APC | 80A BLHeli_32 | Li-Ion 12S 16000mAh 15C Pack | 43.2 | 115.26 | 178.0 | 0.7273 |
| FW-003 | SUCCESS | KDE Direct 7215XF | 18x10 APC | 80A BLHeli_32 | LiHV 12S 16000mAh 40C Pack | 45.6 | 115.26 | 174.3 | 0.7632 |
| FW-004 | SUCCESS | T-Motor AT4120 | 15x10 APC | 80A BLHeli_32 | Li-Ion 6S 10000mAh 15C Pack | 21.6 | 56.49 | 39.9 | 0.452 |
| FW-005 | SUCCESS | KDE Direct 7215XF | 18x10 APC | 80A BLHeli_32 | Li-Ion 12S 10000mAh 15C Pack | 43.2 | 115.26 | 145.8 | 0.7544 |
| FW-006 | SUCCESS | KDE Direct 7215XF | 18x10 APC | 80A BLHeli_32 | Li-Ion 12S 16000mAh 15C Pack | 43.2 | 115.26 | 134.3 | 0.6677 |
| FW-007 | SUCCESS | KDE Direct 7215XF | 18x10 APC | 80A BLHeli_32 | Li-Ion 12S 16000mAh 15C Pack | 43.2 | 115.26 | 140.3 | 0.6758 |
| FW-008 | SUCCESS | KDE Direct 7215XF | 18x10 APC | 80A BLHeli_32 | Li-Ion 12S 10000mAh 15C Pack | 43.2 | 115.26 | 194.3 | 0.8031 |
| FW-009 | SUCCESS | KDE Direct 7215XF | 18x10 APC | 80A BLHeli_32 | LiHV 12S 5000mAh 40C Pack | 45.6 | 115.26 | 79.0 | 0.8007 |
| FW-010 | SUCCESS | KDE Direct 7215XF | 18x10 APC | 80A BLHeli_32 | Li-Ion 12S 10000mAh 15C Pack | 43.2 | 115.26 | 172.4 | 0.812 |
| FW-011 | SUCCESS | KDE Direct 7215XF | 18x10 APC | 80A BLHeli_32 | Li-Ion 12S 8000mAh 15C Pack | 43.2 | 115.26 | 90.8 | 0.7713 |
| FW-012 | SUCCESS | KDE Direct 7215XF | 18x10 APC | 80A BLHeli_32 | Li-Ion 12S 16000mAh 15C Pack | 43.2 | 115.26 | 138.1 | 0.67 |
| FW-013 | SUCCESS | T-Motor AT4120 | 15x10 APC | 80A BLHeli_32 | Li-Ion 6S 10000mAh 15C Pack | 21.6 | 56.49 | 47.7 | 0.5012 |
| FW-014 | SUCCESS | KDE Direct 7215XF | 18x10 APC | 80A BLHeli_32 | Li-Ion 12S 16000mAh 15C Pack | 43.2 | 115.26 | 210.8 | 0.7346 |
| FW-015 | SUCCESS | KDE Direct 7215XF | 18x10 APC | 80A BLHeli_32 | LiHV 12S 16000mAh 40C Pack | 45.6 | 115.26 | 157.4 | 0.7182 |
