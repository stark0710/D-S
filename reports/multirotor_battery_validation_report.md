# Multirotor Battery Optimization Engine Validation Report

This report summarizes the electrical and flight endurance validation of the **Sprint 42 Battery Optimization Engine** over **100 randomized multirotor missions**.

## Sizing Summary
- **Total Solved Cases**: 100/100 (100% Sizing Rate)
- **Mean Battery Flight Time**: 13.2 minutes
- **Mean Sized Takeoff Weight (AUW)**: 5.24 kg
- **Mean Hover Throttle Percentage**: 28.3% (Sit safely within the optimal control window)
- **Propulsion Assembly Completeness**: 100% (All selected components generate a valid, compiled PropulsionAssembly)

## Detailed Battery Sizing Ledger
| Case ID | Mission Type | Payload (kg) | Configuration | Selected Motor | Selected ESC | Selected Battery | Nominal Voltage (V) | Flight Time (min) | AUW (kg) | Hover Throttle (%) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Videography | 0.81 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 13.8 | 2.34 | 21.7 |
| 2 | Security | 0.39 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 32.9 | 1.86 | 17.3 |
| 3 | Search & Rescue | 1.62 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 10.5 | 3.45 | 32.0 |
| 4 | Cargo Delivery | 0.72 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 19.4 | 2.33 | 21.6 |
| 5 | Videography | 1.31 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 13.3 | 2.98 | 27.6 |
| 6 | Heavy Lift | 3.45 | Hexacopter X | T-Motor U8 II-190 | T-Motor Flame 80A Heavy | T-Motor 22000mAh 12S LiPo | 44.4 | 20.9 | 11.45 | 26.1 |
| 7 | Security | 0.46 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 25.7 | 1.90 | 17.6 |
| 8 | Mapping | 1.87 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 2.8 | 5.65 | 29.4 |
| 9 | Agriculture | 2.15 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 80A Heavy | T-Line 1300mAh 4S LiPo | 14.8 | 2.4 | 4.68 | 24.4 |
| 10 | Search & Rescue | 0.92 | Quadcopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Samsung 5000mAh 6S Li-Ion | 22.2 | 24.9 | 2.28 | 31.7 |
| 11 | Photography | 0.38 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 29.0 | 1.82 | 16.9 |
| 12 | Mapping | 2.72 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 2.2 | 6.58 | 34.3 |
| 13 | Cargo Delivery | 3.00 | Hexacopter X | T-Motor U8 II-190 | T-Motor Flame 80A Heavy | T-Motor 22000mAh 12S LiPo | 44.4 | 28.3 | 11.10 | 25.3 |
| 14 | Search & Rescue | 2.74 | Hexacopter X | T-Motor MN5008-400 | T-Motor Flame 60A Pro | GensAce 10000mAh 6S LiPo | 22.2 | 14.0 | 6.42 | 29.7 |
| 15 | Mapping | 0.92 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | T-Line 1300mAh 4S LiPo | 14.8 | 8.3 | 2.44 | 22.6 |
| 16 | Survey | 3.06 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 1.7 | 6.84 | 35.6 |
| 17 | Cargo Delivery | 1.90 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 80A Heavy | GensAce 10000mAh 6S LiPo | 22.2 | 17.7 | 5.77 | 30.1 |
| 18 | Search & Rescue | 3.25 | Hexacopter X | T-Motor MN5008-400 | T-Motor Flame 60A Pro | GensAce 10000mAh 6S LiPo | 22.2 | 13.9 | 7.05 | 32.6 |
| 19 | Survey | 3.19 | Hexacopter X | T-Motor MN5008-400 | T-Motor Flame 60A Pro | GensAce 10000mAh 6S LiPo | 22.2 | 11.7 | 6.87 | 31.8 |
| 20 | Search & Rescue | 4.01 | Hexacopter X | T-Motor U8 II-190 | T-Motor Flame 180A Extreme | T-Motor 22000mAh 12S LiPo | 44.4 | 18.4 | 12.98 | 29.6 |
| 21 | Agriculture | 2.39 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 2.3 | 6.17 | 32.1 |
| 22 | Heavy Lift | 2.03 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 80A Heavy | GensAce 10000mAh 6S LiPo | 22.2 | 10.5 | 5.69 | 29.6 |
| 23 | Photography | 1.70 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 2.0 | 5.23 | 27.2 |
| 24 | Search & Rescue | 0.80 | Quadcopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 23.3 | 2.15 | 29.9 |
| 25 | Search & Rescue | 2.06 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 2.7 | 5.86 | 30.5 |
| 26 | Cargo Delivery | 3.22 | Hexacopter X | T-Motor U8 II-190 | T-Motor Flame 80A Heavy | T-Motor 22000mAh 12S LiPo | 44.4 | 28.8 | 11.38 | 26.0 |
| 27 | Mapping | 1.11 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 13.5 | 2.72 | 25.2 |
| 28 | Photography | 1.55 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | T-Line 1300mAh 4S LiPo | 14.8 | 2.8 | 2.96 | 27.4 |
| 29 | Videography | 1.19 | Quadcopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | Molicel 4200mAh 6S Li-Ion | 22.2 | 10.8 | 3.88 | 30.3 |
| 30 | Mapping | 3.47 | Hexacopter X | T-Motor MN5008-400 | T-Motor Flame 180A Extreme | GensAce 10000mAh 6S LiPo | 22.2 | 11.0 | 8.57 | 39.7 |
| 31 | Agriculture | 1.67 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 10.2 | 3.51 | 32.5 |
| 32 | Cargo Delivery | 3.33 | Hexacopter X | T-Motor U8 II-190 | T-Motor Flame 80A Heavy | T-Motor 22000mAh 12S LiPo | 44.4 | 24.4 | 11.39 | 26.0 |
| 33 | Search & Rescue | 1.57 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 10.9 | 3.41 | 31.6 |
| 34 | Heavy Lift | 3.72 | Hexacopter X | T-Motor U8 II-190 | T-Motor Flame 80A Heavy | T-Motor 22000mAh 12S LiPo | 44.4 | 23.9 | 11.85 | 27.0 |
| 35 | Mapping | 1.39 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | T-Line 1300mAh 4S LiPo | 14.8 | 3.8 | 2.73 | 25.2 |
| 36 | Survey | 3.08 | Hexacopter X | T-Motor MN5008-400 | T-Motor Flame 60A Pro | GensAce 10000mAh 6S LiPo | 22.2 | 11.4 | 6.72 | 31.1 |
| 37 | Cargo Delivery | 3.00 | Hexacopter X | T-Motor U8 II-190 | T-Motor Flame 80A Heavy | T-Motor 22000mAh 12S LiPo | 44.4 | 25.3 | 11.03 | 25.2 |
| 38 | Mapping | 2.83 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 1.5 | 6.47 | 33.7 |
| 39 | Photography | 1.23 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 10.6 | 2.80 | 26.0 |
| 40 | Search & Rescue | 0.67 | Quadcopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 16.2 | 1.89 | 26.2 |
| 41 | Videography | 2.78 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 2.2 | 6.66 | 34.7 |
| 42 | Cargo Delivery | 2.32 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 80A Heavy | GensAce 10000mAh 6S LiPo | 22.2 | 16.1 | 6.25 | 32.5 |
| 43 | Agriculture | 1.26 | Quadcopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 2.9 | 3.63 | 28.3 |
| 44 | Agriculture | 4.34 | Hexacopter X | T-Motor U8 II-190 | T-Motor Flame 80A Heavy | T-Motor 22000mAh 12S LiPo | 44.4 | 19.8 | 12.27 | 28.0 |
| 45 | Search & Rescue | 0.93 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 14.9 | 2.52 | 23.3 |
| 46 | Agriculture | 1.43 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 11.6 | 3.08 | 28.5 |
| 47 | Search & Rescue | 2.03 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 1.9 | 5.60 | 29.2 |
| 48 | Videography | 3.42 | Hexacopter X | T-Motor MN5008-400 | T-Motor Flame 60A Pro | GensAce 10000mAh 6S LiPo | 22.2 | 14.3 | 7.28 | 33.7 |
| 49 | Agriculture | 1.78 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 80A Heavy | T-Line 1300mAh 4S LiPo | 14.8 | 2.5 | 4.22 | 22.0 |
| 50 | Photography | 1.16 | Quadcopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 11.1 | 2.42 | 33.6 |
| 51 | Survey | 1.22 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 16.6 | 2.95 | 27.3 |
| 52 | Videography | 2.08 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 1.5 | 5.57 | 29.0 |
| 53 | Security | 1.72 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 2.5 | 5.37 | 27.9 |
| 54 | Agriculture | 0.89 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 15.5 | 2.48 | 22.9 |
| 55 | Mapping | 4.34 | Hexacopter X | T-Motor U8 II-190 | T-Motor Flame 180A Extreme | T-Motor 22000mAh 12S LiPo | 44.4 | 17.2 | 13.32 | 30.4 |
| 56 | Survey | 1.56 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 12.9 | 3.51 | 32.5 |
| 57 | Survey | 0.72 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | T-Line 1300mAh 4S LiPo | 14.8 | 8.9 | 2.17 | 20.1 |
| 58 | Mapping | 2.14 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 2.5 | 5.92 | 30.8 |
| 59 | Photography | 1.72 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 2.6 | 5.40 | 28.1 |
| 60 | Agriculture | 1.71 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 2.6 | 5.39 | 28.1 |
| 61 | Videography | 1.39 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 16.9 | 3.20 | 29.6 |
| 62 | Videography | 1.48 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 3.0 | 4.97 | 25.9 |
| 63 | Cargo Delivery | 1.10 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 20.3 | 2.89 | 26.8 |
| 64 | Search & Rescue | 2.61 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 2.3 | 6.47 | 33.7 |
| 65 | Cargo Delivery | 1.62 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 80A Heavy | GensAce 10000mAh 6S LiPo | 22.2 | 12.7 | 5.27 | 27.4 |
| 66 | Inspection | 2.42 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 1.9 | 6.11 | 31.8 |
| 67 | Mapping | 3.06 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 1.5 | 6.76 | 35.2 |
| 68 | Cargo Delivery | 0.30 | Quadcopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Samsung 5000mAh 6S Li-Ion | 22.2 | 49.3 | 1.48 | 20.6 |
| 69 | Heavy Lift | 2.33 | Hexacopter X | T-Motor MN5008-400 | T-Motor Flame 60A Pro | GensAce 10000mAh 6S LiPo | 22.2 | 14.7 | 5.94 | 27.5 |
| 70 | Inspection | 2.31 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 2.0 | 5.99 | 31.2 |
| 71 | Mapping | 0.89 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 22.4 | 2.64 | 24.5 |
| 72 | Heavy Lift | 2.13 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 80A Heavy | GensAce 10000mAh 6S LiPo | 22.2 | 14.5 | 5.95 | 31.0 |
| 73 | Cargo Delivery | 1.91 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 80A Heavy | GensAce 10000mAh 6S LiPo | 22.2 | 13.7 | 5.65 | 29.4 |
| 74 | Mapping | 2.48 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 1.5 | 6.04 | 31.5 |
| 75 | Videography | 2.73 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 1.7 | 6.42 | 33.4 |
| 76 | Security | 3.86 | Hexacopter X | T-Motor U8 II-190 | T-Motor Flame 180A Extreme | T-Motor 22000mAh 12S LiPo | 44.4 | 21.2 | 12.89 | 29.4 |
| 77 | Heavy Lift | 2.58 | Hexacopter X | T-Motor MN5008-400 | T-Motor Flame 60A Pro | GensAce 10000mAh 6S LiPo | 22.2 | 13.8 | 6.21 | 28.8 |
| 78 | Mapping | 0.50 | Quadcopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 23.2 | 1.74 | 24.2 |
| 79 | Agriculture | 0.64 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 27.3 | 2.39 | 22.1 |
| 80 | Mapping | 1.11 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | T-Line 1300mAh 4S LiPo | 14.8 | 4.2 | 2.40 | 22.2 |
| 81 | Mapping | 1.88 | Hexacopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 2.8 | 5.64 | 29.4 |
| 82 | Heavy Lift | 0.94 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | GensAce 10000mAh 6S LiPo | 22.2 | 19.1 | 3.47 | 32.1 |
| 83 | Heavy Lift | 1.35 | Quadcopter X | T-Motor MN4014-370 | T-Motor Flame 80A Heavy | GensAce 10000mAh 6S LiPo | 22.2 | 17.6 | 4.28 | 33.4 |
| 84 | Survey | 4.05 | Hexacopter X | T-Motor U8 II-190 | T-Motor Flame 180A Extreme | T-Motor 22000mAh 12S LiPo | 44.4 | 21.1 | 13.11 | 29.9 |
| 85 | Security | 0.39 | Quadcopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 36.9 | 1.58 | 21.9 |
| 86 | Survey | 1.04 | Quadcopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 11.8 | 2.28 | 31.7 |
| 87 | Cargo Delivery | 2.73 | Hexacopter X | T-Motor MN5008-400 | T-Motor Flame 60A Pro | GensAce 10000mAh 6S LiPo | 22.2 | 11.5 | 6.31 | 29.2 |
| 88 | Photography | 0.50 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 28.2 | 2.20 | 20.4 |
| 89 | Photography | 3.95 | Hexacopter X | T-Motor U8 II-190 | T-Motor Flame 180A Extreme | T-Motor 22000mAh 12S LiPo | 44.4 | 20.3 | 12.97 | 29.6 |
| 90 | Mapping | 1.73 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | T-Line 1300mAh 4S LiPo | 14.8 | 2.7 | 3.18 | 29.4 |
| 91 | Inspection | 0.95 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 20.8 | 2.69 | 24.9 |
| 92 | Inspection | 0.35 | Quadcopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | T-Line 1300mAh 4S LiPo | 14.8 | 11.1 | 1.20 | 16.7 |
| 93 | Mapping | 1.69 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | T-Line 1300mAh 4S LiPo | 14.8 | 2.7 | 3.12 | 28.9 |
| 94 | Security | 3.45 | Hexacopter X | T-Motor MN5008-400 | T-Motor Flame 60A Pro | GensAce 10000mAh 6S LiPo | 22.2 | 13.6 | 7.28 | 33.7 |
| 95 | Search & Rescue | 1.40 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Molicel 4200mAh 6S Li-Ion | 22.2 | 13.1 | 3.09 | 28.6 |
| 96 | Cargo Delivery | 0.72 | Hexacopter X | T-Motor F40 PRO IV-1950 | T-Motor Flame 60A Pro | Samsung 5000mAh 6S Li-Ion | 22.2 | 29.9 | 2.46 | 22.8 |
| 97 | Cargo Delivery | 1.49 | Quadcopter X | T-Motor MN4014-370 | T-Motor Flame 80A Heavy | GensAce 10000mAh 6S LiPo | 22.2 | 15.9 | 4.42 | 34.5 |
| 98 | Cargo Delivery | 2.68 | Hexacopter X | T-Motor MN5008-400 | T-Motor Flame 60A Pro | GensAce 10000mAh 6S LiPo | 22.2 | 16.8 | 6.46 | 29.9 |
| 99 | Inspection | 1.32 | Quadcopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | Molicel 4200mAh 6S Li-Ion | 22.2 | 12.7 | 4.09 | 31.9 |
| 100 | Photography | 1.31 | Quadcopter X | T-Motor MN4014-370 | T-Motor Flame 180A Extreme | T-Line 1300mAh 4S LiPo | 14.8 | 3.4 | 3.73 | 29.1 |
