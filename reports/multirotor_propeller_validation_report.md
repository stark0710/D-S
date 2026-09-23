# Multirotor Propeller Optimization Engine Validation Report

This report summarizes the aerodynamic validation of the **Sprint 40 Propeller Optimization Engine** over **100 randomized multirotor missions**.

## Sizing Summary
- **Total Solved Cases**: 100/100 (100% Sizing Rate)
- **Mean Propeller Diameter**: 12.9 inches
- **Mean Hover Efficiency**: 6.38 g/W
- **Aerodynamic Tip Speed Compliance**: 100% (All tip speed calculations sit safely below shockwave limits of 220 m/s)

## Detailed Propeller Sizing Ledger
| Case ID | Mission Type | Payload (kg) | Configuration | Selected Motor | Sized Propeller | Diameter (in) | Pitch (in) | Hover Eff (g/W) |
|---|---|---|---|---|---|---|---|---|
| 1 | Videography | 0.81 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 6.6 |
| 2 | Security | 0.39 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 8.4 |
| 3 | Search & Rescue | 1.62 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 4.9 |
| 4 | Cargo Delivery | 0.72 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 6.9 |
| 5 | Videography | 1.31 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 5.4 |
| 6 | Heavy Lift | 3.45 | Hexacopter X | T-Motor U8 II-190 | T-Motor 22x7.2 Carbon | 22.0 | 7.2 | 9.7 |
| 7 | Security | 0.46 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 7.8 |
| 8 | Mapping | 1.87 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 6.1 |
| 9 | Agriculture | 2.15 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.8 |
| 10 | Search & Rescue | 0.92 | Quadcopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 5.1 |
| 11 | Photography | 0.38 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 8.4 |
| 12 | Mapping | 2.72 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.3 |
| 13 | Cargo Delivery | 3.00 | Hexacopter X | T-Motor U8 II-190 | T-Motor 22x7.2 Carbon | 22.0 | 7.2 | 10.3 |
| 14 | Search & Rescue | 2.74 | Hexacopter X | T-Motor MN5008-400 | Tarot 15x5.5 Carbon | 15.0 | 5.5 | 6.8 |
| 15 | Mapping | 0.92 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 6.2 |
| 16 | Survey | 3.06 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.1 |
| 17 | Cargo Delivery | 1.90 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 6.1 |
| 18 | Search & Rescue | 3.25 | Hexacopter X | T-Motor MN5008-400 | Tarot 15x5.5 Carbon | 15.0 | 5.5 | 6.3 |
| 19 | Survey | 3.19 | Hexacopter X | T-Motor MN5008-400 | Tarot 15x5.5 Carbon | 15.0 | 5.5 | 6.5 |
| 20 | Search & Rescue | 4.01 | Hexacopter X | T-Motor U8 II-190 | T-Motor 18x6.1 Carbon | 18.0 | 6.1 | 7.2 |
| 21 | Agriculture | 2.39 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.5 |
| 22 | Heavy Lift | 2.03 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.9 |
| 23 | Photography | 1.70 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 6.4 |
| 24 | Search & Rescue | 0.80 | Quadcopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 5.3 |
| 25 | Search & Rescue | 2.06 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.8 |
| 26 | Cargo Delivery | 3.22 | Hexacopter X | T-Motor U8 II-190 | T-Motor 22x7.2 Carbon | 22.0 | 7.2 | 10.0 |
| 27 | Mapping | 1.11 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 5.9 |
| 28 | Photography | 1.55 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 5.0 |
| 29 | Videography | 1.19 | Quadcopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 6.1 |
| 30 | Mapping | 3.47 | Hexacopter X | T-Motor MN5008-400 | Tarot 15x5.5 Carbon | 15.0 | 5.5 | 6.2 |
| 31 | Agriculture | 1.67 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 6.3 |
| 32 | Cargo Delivery | 3.33 | Hexacopter X | T-Motor U8 II-190 | T-Motor 22x7.2 Carbon | 22.0 | 7.2 | 9.9 |
| 33 | Search & Rescue | 1.57 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 4.9 |
| 34 | Heavy Lift | 3.72 | Hexacopter X | T-Motor U8 II-190 | T-Motor 22x7.2 Carbon | 22.0 | 7.2 | 9.4 |
| 35 | Mapping | 1.39 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 5.4 |
| 36 | Survey | 3.08 | Hexacopter X | T-Motor U8 II-190 | T-Motor 18x6.1 Carbon | 18.0 | 6.1 | 8.2 |
| 37 | Cargo Delivery | 3.00 | Hexacopter X | T-Motor U8 II-190 | T-Motor 22x7.2 Carbon | 22.0 | 7.2 | 10.3 |
| 38 | Mapping | 2.83 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.3 |
| 39 | Photography | 1.23 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 5.5 |
| 40 | Search & Rescue | 0.67 | Quadcopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 5.8 |
| 41 | Videography | 2.78 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.2 |
| 42 | Cargo Delivery | 2.32 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.7 |
| 43 | Agriculture | 1.26 | Quadcopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 6.0 |
| 44 | Agriculture | 4.34 | Hexacopter X | T-Motor U8 II-190 | T-Motor 18x6.1 Carbon | 18.0 | 6.1 | 7.0 |
| 45 | Search & Rescue | 0.93 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 6.0 |
| 46 | Agriculture | 1.43 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 5.2 |
| 47 | Search & Rescue | 2.03 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.8 |
| 48 | Videography | 3.42 | Hexacopter X | T-Motor MN5008-400 | Tarot 15x5.5 Carbon | 15.0 | 5.5 | 6.2 |
| 49 | Agriculture | 1.78 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 6.3 |
| 50 | Photography | 1.16 | Quadcopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 6.3 |
| 51 | Survey | 1.22 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 5.6 |
| 52 | Videography | 2.08 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.8 |
| 53 | Security | 1.72 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 6.3 |
| 54 | Agriculture | 0.89 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 6.3 |
| 55 | Mapping | 4.34 | Hexacopter X | T-Motor U8 II-190 | T-Motor 18x6.1 Carbon | 18.0 | 6.1 | 7.0 |
| 56 | Survey | 1.56 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 5.0 |
| 57 | Survey | 0.72 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 6.7 |
| 58 | Mapping | 2.14 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.8 |
| 59 | Photography | 1.72 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 6.2 |
| 60 | Agriculture | 1.71 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 6.2 |
| 61 | Videography | 1.39 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 5.1 |
| 62 | Videography | 1.48 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 6.6 |
| 63 | Cargo Delivery | 1.10 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 5.8 |
| 64 | Search & Rescue | 2.61 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.3 |
| 65 | Cargo Delivery | 1.62 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 6.6 |
| 66 | Inspection | 2.42 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.5 |
| 67 | Mapping | 3.06 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.1 |
| 68 | Cargo Delivery | 0.30 | Quadcopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 8.1 |
| 69 | Heavy Lift | 2.33 | Hexacopter X | T-Motor MN5008-400 | Tarot 15x5.5 Carbon | 15.0 | 5.5 | 7.3 |
| 70 | Inspection | 2.31 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.6 |
| 71 | Mapping | 0.89 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 6.3 |
| 72 | Heavy Lift | 2.13 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.8 |
| 73 | Cargo Delivery | 1.91 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 6.2 |
| 74 | Mapping | 2.48 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.6 |
| 75 | Videography | 2.73 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.2 |
| 76 | Security | 3.86 | Hexacopter X | T-Motor U8 II-190 | T-Motor 18x6.1 Carbon | 18.0 | 6.1 | 7.3 |
| 77 | Heavy Lift | 2.58 | Hexacopter X | T-Motor MN5008-400 | Tarot 15x5.5 Carbon | 15.0 | 5.5 | 6.9 |
| 78 | Mapping | 0.50 | Quadcopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 6.8 |
| 79 | Agriculture | 0.64 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 6.9 |
| 80 | Mapping | 1.11 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 6.0 |
| 81 | Mapping | 1.88 | Hexacopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 6.1 |
| 82 | Heavy Lift | 0.94 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 6.1 |
| 83 | Heavy Lift | 1.35 | Quadcopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 6.0 |
| 84 | Survey | 4.05 | Hexacopter X | T-Motor U8 II-190 | T-Motor 18x6.1 Carbon | 18.0 | 6.1 | 7.2 |
| 85 | Security | 0.39 | Quadcopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 6.8 |
| 86 | Survey | 1.04 | Quadcopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 5.1 |
| 87 | Cargo Delivery | 2.73 | Hexacopter X | T-Motor MN5008-400 | Tarot 15x5.5 Carbon | 15.0 | 5.5 | 6.9 |
| 88 | Photography | 0.50 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 7.0 |
| 89 | Photography | 3.95 | Hexacopter X | T-Motor U8 II-190 | T-Motor 18x6.1 Carbon | 18.0 | 6.1 | 7.3 |
| 90 | Mapping | 1.73 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 4.9 |
| 91 | Inspection | 0.95 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 5.9 |
| 92 | Inspection | 0.35 | Quadcopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 7.3 |
| 93 | Mapping | 1.69 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 4.9 |
| 94 | Security | 3.45 | Hexacopter X | T-Motor U8 II-190 | T-Motor 18x6.1 Carbon | 18.0 | 6.1 | 7.6 |
| 95 | Search & Rescue | 1.40 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 5.2 |
| 96 | Cargo Delivery | 0.72 | Hexacopter X | T-Motor F40 PRO IV-1950 | APC 10x4.7 MR | 10.0 | 4.7 | 6.7 |
| 97 | Cargo Delivery | 1.49 | Quadcopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.8 |
| 98 | Cargo Delivery | 2.68 | Hexacopter X | T-Motor MN5008-400 | Tarot 15x5.5 Carbon | 15.0 | 5.5 | 6.9 |
| 99 | Inspection | 1.32 | Quadcopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.9 |
| 100 | Photography | 1.31 | Quadcopter X | T-Motor MN4014-370 | Tarot 13x5.5 Carbon | 13.0 | 5.5 | 5.9 |
