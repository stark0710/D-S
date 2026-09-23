# Multirotor Motor Optimization Engine Validation Report

This report summarizes the propulsion validation of the **Sprint 39 Motor Optimization Engine** over **100 randomized multirotor missions**.

## Sizing Summary
- **Total Solved Cases**: 100/100 (100% Sizing Rate)
- **Mean Hover Current Draw**: 5.14 A
- **Mean Hover Throttle**: 58.8 %
- **Thermal Margin Compliance**: 100% (All continuous hover current draws are within thermal margins)

## Detailed Propulsion Sizing Ledger
| Case ID | Mission Type | Payload (kg) | Configuration | Selected Motor | KV Rating | Hover Current (A) | Hover Throttle (%) | Efficiency (%) |
|---|---|---|---|---|---|---|---|---|
| 1 | Videography | 0.81 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 2.76 | 51.7 | 79.5 |
| 2 | Security | 0.39 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 0.79 | 40.5 | 80.1 |
| 3 | Search & Rescue | 1.62 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 4.79 | 69.6 | 78.6 |
| 4 | Cargo Delivery | 0.72 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 1.73 | 49.5 | 79.6 |
| 5 | Videography | 1.31 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 3.52 | 63.1 | 78.9 |
| 6 | Heavy Lift | 3.45 | Hexacopter X | T-Motor U8 II-190 | 190 | 7.30 | 50.7 | 83.1 |
| 7 | Security | 0.46 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 1.22 | 43.7 | 79.9 |
| 8 | Mapping | 1.87 | Hexacopter X | T-Motor MN4014-370 | 370 | 3.93 | 58.5 | 82.3 |
| 9 | Agriculture | 2.15 | Hexacopter X | T-Motor MN4014-370 | 370 | 6.82 | 62.1 | 82.2 |
| 10 | Search & Rescue | 0.92 | Quadcopter X | T-Motor F40 PRO IV-1950 | 1950 | 3.18 | 66.8 | 78.8 |
| 11 | Photography | 0.38 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 0.91 | 40.3 | 80.1 |
| 12 | Mapping | 2.72 | Hexacopter X | T-Motor MN4014-370 | 370 | 5.96 | 67.8 | 81.9 |
| 13 | Cargo Delivery | 3.00 | Hexacopter X | T-Motor U8 II-190 | 190 | 4.79 | 47.8 | 83.2 |
| 14 | Search & Rescue | 2.74 | Hexacopter X | T-Motor MN5008-400 | 400 | 7.62 | 63.9 | 82.0 |
| 15 | Mapping | 0.92 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 1.52 | 55.2 | 79.3 |
| 16 | Survey | 3.06 | Hexacopter X | T-Motor MN4014-370 | 370 | 8.13 | 70.5 | 81.7 |
| 17 | Cargo Delivery | 1.90 | Hexacopter X | T-Motor MN4014-370 | 370 | 4.64 | 58.3 | 82.3 |
| 18 | Search & Rescue | 3.25 | Hexacopter X | T-Motor MN5008-400 | 400 | 8.19 | 68.7 | 81.8 |
| 19 | Survey | 3.19 | Hexacopter X | T-Motor MN5008-400 | 400 | 9.56 | 67.3 | 81.8 |
| 20 | Search & Rescue | 4.01 | Hexacopter X | T-Motor U8 II-190 | 190 | 8.24 | 53.9 | 82.9 |
| 21 | Agriculture | 2.39 | Hexacopter X | T-Motor MN4014-370 | 370 | 5.86 | 65.4 | 82.0 |
| 22 | Heavy Lift | 2.03 | Hexacopter X | T-Motor MN4014-370 | 370 | 8.92 | 60.5 | 82.2 |
| 23 | Photography | 1.70 | Hexacopter X | T-Motor MN4014-370 | 370 | 5.50 | 55.9 | 82.5 |
| 24 | Search & Rescue | 0.80 | Quadcopter X | T-Motor F40 PRO IV-1950 | 1950 | 2.72 | 63.8 | 78.9 |
| 25 | Search & Rescue | 2.06 | Hexacopter X | T-Motor MN4014-370 | 370 | 4.49 | 61.3 | 82.2 |
| 26 | Cargo Delivery | 3.22 | Hexacopter X | T-Motor U8 II-190 | 190 | 4.94 | 49.3 | 83.2 |
| 27 | Mapping | 1.11 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 3.06 | 57.5 | 79.2 |
| 28 | Photography | 1.55 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 6.15 | 67.3 | 78.7 |
| 29 | Videography | 1.19 | Quadcopter X | T-Motor MN4014-370 | 370 | 4.73 | 58.4 | 82.3 |
| 30 | Mapping | 3.47 | Hexacopter X | T-Motor MN5008-400 | 400 | 8.44 | 69.9 | 81.7 |
| 31 | Agriculture | 1.67 | Hexacopter X | T-Motor MN4014-370 | 370 | 4.93 | 56.9 | 82.4 |
| 32 | Cargo Delivery | 3.33 | Hexacopter X | T-Motor U8 II-190 | 190 | 5.93 | 49.6 | 83.1 |
| 33 | Search & Rescue | 1.57 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 4.54 | 68.8 | 78.7 |
| 34 | Heavy Lift | 3.72 | Hexacopter X | T-Motor U8 II-190 | 190 | 6.61 | 52.3 | 83.0 |
| 35 | Mapping | 1.39 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 4.20 | 62.6 | 79.0 |
| 36 | Survey | 3.08 | Hexacopter X | T-Motor U8 II-190 | 190 | 6.94 | 47.9 | 83.2 |
| 37 | Cargo Delivery | 3.00 | Hexacopter X | T-Motor U8 II-190 | 190 | 5.41 | 47.8 | 83.2 |
| 38 | Mapping | 2.83 | Hexacopter X | T-Motor MN4014-370 | 370 | 9.40 | 67.9 | 81.9 |
| 39 | Photography | 1.23 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 4.69 | 62.3 | 79.0 |
| 40 | Search & Rescue | 0.67 | Quadcopter X | T-Motor F40 PRO IV-1950 | 1950 | 3.88 | 59.1 | 79.1 |
| 41 | Videography | 2.78 | Hexacopter X | T-Motor MN4014-370 | 370 | 6.26 | 69.3 | 81.8 |
| 42 | Cargo Delivery | 2.32 | Hexacopter X | T-Motor MN4014-370 | 370 | 5.66 | 63.1 | 82.1 |
| 43 | Agriculture | 1.26 | Quadcopter X | T-Motor MN4014-370 | 370 | 6.44 | 59.7 | 82.3 |
| 44 | Agriculture | 4.34 | Hexacopter X | T-Motor U8 II-190 | 190 | 8.89 | 55.5 | 82.8 |
| 45 | Search & Rescue | 0.93 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 2.96 | 56.7 | 79.3 |
| 46 | Agriculture | 1.43 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 4.29 | 65.7 | 78.8 |
| 47 | Search & Rescue | 2.03 | Hexacopter X | T-Motor MN4014-370 | 370 | 6.80 | 61.0 | 82.2 |
| 48 | Videography | 3.42 | Hexacopter X | T-Motor MN5008-400 | 400 | 8.02 | 70.2 | 81.7 |
| 49 | Agriculture | 1.78 | Hexacopter X | T-Motor MN4014-370 | 370 | 6.13 | 57.1 | 82.4 |
| 50 | Photography | 1.16 | Quadcopter X | T-Motor MN4014-370 | 370 | 6.50 | 56.9 | 82.4 |
| 51 | Survey | 1.22 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 2.56 | 60.8 | 79.1 |
| 52 | Videography | 2.08 | Hexacopter X | T-Motor MN4014-370 | 370 | 8.63 | 61.2 | 82.2 |
| 53 | Security | 1.72 | Hexacopter X | T-Motor MN4014-370 | 370 | 4.39 | 56.7 | 82.4 |
| 54 | Agriculture | 0.89 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 2.50 | 53.6 | 79.4 |
| 55 | Mapping | 4.34 | Hexacopter X | T-Motor U8 II-190 | 190 | 9.17 | 55.4 | 82.9 |
| 56 | Survey | 1.56 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 3.64 | 68.6 | 78.7 |
| 57 | Survey | 0.72 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 1.32 | 50.5 | 79.6 |
| 58 | Mapping | 2.14 | Hexacopter X | T-Motor MN4014-370 | 370 | 4.70 | 61.4 | 82.2 |
| 59 | Photography | 1.72 | Hexacopter X | T-Motor MN4014-370 | 370 | 4.20 | 57.2 | 82.4 |
| 60 | Agriculture | 1.71 | Hexacopter X | T-Motor MN4014-370 | 370 | 4.44 | 58.1 | 82.4 |
| 61 | Videography | 1.39 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 2.83 | 66.1 | 78.8 |
| 62 | Videography | 1.48 | Hexacopter X | T-Motor MN4014-370 | 370 | 3.54 | 54.3 | 82.5 |
| 63 | Cargo Delivery | 1.10 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 1.90 | 58.3 | 79.2 |
| 64 | Search & Rescue | 2.61 | Hexacopter X | T-Motor MN4014-370 | 370 | 5.93 | 67.8 | 81.9 |
| 65 | Cargo Delivery | 1.62 | Hexacopter X | T-Motor MN4014-370 | 370 | 6.01 | 54.1 | 82.6 |
| 66 | Inspection | 2.42 | Hexacopter X | T-Motor MN4014-370 | 370 | 6.80 | 64.7 | 82.0 |
| 67 | Mapping | 3.06 | Hexacopter X | T-Motor MN4014-370 | 370 | 9.43 | 70.4 | 81.7 |
| 68 | Cargo Delivery | 0.30 | Quadcopter X | T-Motor F40 PRO IV-1950 | 1950 | 0.78 | 41.8 | 80.0 |
| 69 | Heavy Lift | 2.33 | Hexacopter X | T-Motor MN5008-400 | 400 | 6.78 | 59.9 | 82.2 |
| 70 | Inspection | 2.31 | Hexacopter X | T-Motor MN4014-370 | 370 | 6.44 | 63.6 | 82.1 |
| 71 | Mapping | 0.89 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 1.55 | 53.6 | 79.4 |
| 72 | Heavy Lift | 2.13 | Hexacopter X | T-Motor MN4014-370 | 370 | 6.25 | 61.3 | 82.2 |
| 73 | Cargo Delivery | 1.91 | Hexacopter X | T-Motor MN4014-370 | 370 | 6.04 | 57.7 | 82.4 |
| 74 | Mapping | 2.48 | Hexacopter X | T-Motor MN4014-370 | 370 | 8.92 | 64.1 | 82.1 |
| 75 | Videography | 2.73 | Hexacopter X | T-Motor MN4014-370 | 370 | 8.33 | 68.2 | 81.8 |
| 76 | Security | 3.86 | Hexacopter X | T-Motor U8 II-190 | 190 | 7.00 | 53.3 | 83.0 |
| 77 | Heavy Lift | 2.58 | Hexacopter X | T-Motor MN5008-400 | 400 | 7.73 | 62.8 | 82.1 |
| 78 | Mapping | 0.50 | Quadcopter X | T-Motor F40 PRO IV-1950 | 1950 | 1.93 | 50.3 | 79.6 |
| 79 | Agriculture | 0.64 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 1.17 | 49.6 | 79.6 |
| 80 | Mapping | 1.11 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 3.56 | 57.2 | 79.2 |
| 81 | Mapping | 1.88 | Hexacopter X | T-Motor MN4014-370 | 370 | 4.06 | 58.8 | 82.3 |
| 82 | Heavy Lift | 0.94 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 3.57 | 56.0 | 79.3 |
| 83 | Heavy Lift | 1.35 | Quadcopter X | T-Motor MN4014-370 | 370 | 6.56 | 59.8 | 82.3 |
| 84 | Survey | 4.05 | Hexacopter X | T-Motor U8 II-190 | 190 | 7.15 | 54.1 | 82.9 |
| 85 | Security | 0.39 | Quadcopter X | T-Motor F40 PRO IV-1950 | 1950 | 1.32 | 50.0 | 79.6 |
| 86 | Survey | 1.04 | Quadcopter X | T-Motor F40 PRO IV-1950 | 1950 | 5.66 | 66.3 | 78.8 |
| 87 | Cargo Delivery | 2.73 | Hexacopter X | T-Motor MN5008-400 | 400 | 8.98 | 62.7 | 82.1 |
| 88 | Photography | 0.50 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 1.18 | 48.2 | 79.7 |
| 89 | Photography | 3.95 | Hexacopter X | T-Motor U8 II-190 | 190 | 7.38 | 53.6 | 82.9 |
| 90 | Mapping | 1.73 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 6.41 | 69.7 | 78.6 |
| 91 | Inspection | 0.95 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 1.98 | 57.5 | 79.2 |
| 92 | Inspection | 0.35 | Quadcopter X | T-Motor F40 PRO IV-1950 | 1950 | 1.58 | 46.2 | 79.8 |
| 93 | Mapping | 1.69 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 6.52 | 68.9 | 78.7 |
| 94 | Security | 3.45 | Hexacopter X | T-Motor U8 II-190 | 190 | 6.19 | 51.1 | 83.1 |
| 95 | Search & Rescue | 1.40 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 3.72 | 65.3 | 78.8 |
| 96 | Cargo Delivery | 0.72 | Hexacopter X | T-Motor F40 PRO IV-1950 | 1950 | 1.30 | 50.7 | 79.6 |
| 97 | Cargo Delivery | 1.49 | Quadcopter X | T-Motor MN4014-370 | 370 | 7.53 | 61.7 | 82.2 |
| 98 | Cargo Delivery | 2.68 | Hexacopter X | T-Motor MN5008-400 | 400 | 6.00 | 62.9 | 82.1 |
| 99 | Inspection | 1.32 | Quadcopter X | T-Motor MN4014-370 | 370 | 4.20 | 61.0 | 82.2 |
| 100 | Photography | 1.31 | Quadcopter X | T-Motor MN4014-370 | 370 | 5.34 | 60.4 | 82.2 |
