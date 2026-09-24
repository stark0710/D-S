# Multirotor Power Distribution & Electrical Integration Engine Validation Report

This report summarizes the electrical validation of the **Sprint 43 Power Distribution & Electrical Integration Engine** over **100 randomized multirotor missions**.

## Sizing Summary
- **Total Solved Cases**: 100/100 (100% Sizing Rate)
- **Mean Electrical Integration Efficiency**: 97.84%
- **Main Wiring Voltage Drop Compliance**: 100% (All main wires size and drop checks satisfy the 3.0% threshold limit)

## Detailed Electrical Sizing Ledger
| Case ID | Mission Type | Payload (kg) | Configuration | Power Distribution | Main Wire | ESC Wire | Battery Connector | Motor Connector | Efficiency (%) | Voltage Drop (V) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Videography | 0.81 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 98.35 | 0.082 |
| 2 | Security | 0.39 | Hexacopter X | Separate PDB | AWG 22 | AWG 8 | XT30 | MR30 | 97.28 | 0.087 |
| 3 | Search & Rescue | 1.62 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 98.12 | 0.108 |
| 4 | Cargo Delivery | 0.72 | Hexacopter X | Separate PDB | AWG 20 | AWG 8 | XT30 | MR30 | 97.89 | 0.092 |
| 5 | Videography | 1.31 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 98.06 | 0.085 |
| 6 | Heavy Lift | 3.45 | Hexacopter X | Separate PDB | AWG 14 | AWG 8 | XT60 | MR30 | 99.22 | 0.112 |
| 7 | Security | 0.46 | Hexacopter X | Separate PDB | AWG 20 | AWG 8 | XT30 | MR30 | 97.77 | 0.070 |
| 8 | Mapping | 1.87 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 97.13 | 0.125 |
| 9 | Agriculture | 2.15 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT30 | MR30 | 97.46 | 0.091 |
| 10 | Search & Rescue | 0.92 | Quadcopter X | 4-in-1 ESC bus | AWG 20 | AWG 8 | XT30 | MR30 | 97.59 | 0.086 |
| 11 | Photography | 0.38 | Hexacopter X | Separate PDB | AWG 22 | AWG 8 | XT30 | MR30 | 97.51 | 0.099 |
| 12 | Mapping | 2.72 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT30 | MR30 | 97.23 | 0.099 |
| 13 | Cargo Delivery | 3.00 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 99.10 | 0.132 |
| 14 | Search & Rescue | 2.74 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 98.27 | 0.121 |
| 15 | Mapping | 0.92 | Hexacopter X | Separate PDB | AWG 22 | AWG 8 | XT30 | MR30 | 95.42 | 0.106 |
| 16 | Survey | 3.06 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 97.29 | 0.127 |
| 17 | Cargo Delivery | 1.90 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT30 | MR30 | 98.42 | 0.096 |
| 18 | Search & Rescue | 3.25 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 98.13 | 0.122 |
| 19 | Survey | 3.19 | Hexacopter X | Separate PDB | AWG 14 | AWG 8 | XT60 | MR30 | 98.45 | 0.091 |
| 20 | Search & Rescue | 4.01 | Hexacopter X | Separate PDB | AWG 12 | AWG 8 | XT60 | MR30 | 99.28 | 0.080 |
| 21 | Agriculture | 2.39 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT30 | MR30 | 97.39 | 0.098 |
| 22 | Heavy Lift | 2.03 | Hexacopter X | Separate PDB | AWG 14 | AWG 22 | XT60 | MR30 | 96.98 | 0.102 |
| 23 | Photography | 1.70 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 97.81 | 0.111 |
| 24 | Search & Rescue | 0.80 | Quadcopter X | 4-in-1 ESC bus | AWG 20 | AWG 8 | XT30 | MR30 | 97.53 | 0.077 |
| 25 | Search & Rescue | 2.06 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 97.06 | 0.132 |
| 26 | Cargo Delivery | 3.22 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 99.07 | 0.130 |
| 27 | Mapping | 1.11 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 98.18 | 0.084 |
| 28 | Photography | 1.55 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 97.36 | 0.124 |
| 29 | Videography | 1.19 | Quadcopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 98.27 | 0.105 |
| 30 | Mapping | 3.47 | Hexacopter X | Separate PDB | AWG 14 | AWG 8 | XT60 | MR30 | 98.39 | 0.097 |
| 31 | Agriculture | 1.67 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 98.11 | 0.112 |
| 32 | Cargo Delivery | 3.33 | Hexacopter X | Separate PDB | AWG 14 | AWG 8 | XT60 | MR30 | 99.21 | 0.096 |
| 33 | Search & Rescue | 1.57 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 98.11 | 0.104 |
| 34 | Heavy Lift | 3.72 | Hexacopter X | Separate PDB | AWG 14 | AWG 8 | XT60 | MR30 | 99.17 | 0.098 |
| 35 | Mapping | 1.39 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 97.16 | 0.092 |
| 36 | Survey | 3.08 | Hexacopter X | Separate PDB | AWG 14 | AWG 8 | XT60 | MR30 | 98.48 | 0.094 |
| 37 | Cargo Delivery | 3.00 | Hexacopter X | Separate PDB | AWG 14 | AWG 8 | XT60 | MR30 | 99.24 | 0.093 |
| 38 | Mapping | 2.83 | Hexacopter X | Separate PDB | AWG 14 | AWG 8 | XT60 | MR30 | 97.82 | 0.094 |
| 39 | Photography | 1.23 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 98.30 | 0.107 |
| 40 | Search & Rescue | 0.67 | Quadcopter X | 4-in-1 ESC bus | AWG 18 | AWG 8 | XT30 | MR30 | 98.28 | 0.070 |
| 41 | Videography | 2.78 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT30 | MR30 | 97.20 | 0.099 |
| 42 | Cargo Delivery | 2.32 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 98.33 | 0.105 |
| 43 | Agriculture | 1.26 | Quadcopter X | Separate PDB | AWG 18 | AWG 22 | XT30 | MR30 | 95.28 | 0.123 |
| 44 | Agriculture | 4.34 | Hexacopter X | Separate PDB | AWG 14 | AWG 8 | XT60 | MR30 | 99.14 | 0.119 |
| 45 | Search & Rescue | 0.93 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 98.20 | 0.076 |
| 46 | Agriculture | 1.43 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 98.13 | 0.097 |
| 47 | Search & Rescue | 2.03 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 97.69 | 0.119 |
| 48 | Videography | 3.42 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 98.06 | 0.118 |
| 49 | Agriculture | 1.78 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT30 | MR30 | 97.65 | 0.089 |
| 50 | Photography | 1.16 | Quadcopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 98.28 | 0.102 |
| 51 | Survey | 1.22 | Hexacopter X | Separate PDB | AWG 20 | AWG 8 | XT30 | MR30 | 97.67 | 0.108 |
| 52 | Videography | 2.08 | Hexacopter X | Separate PDB | AWG 14 | AWG 8 | XT60 | MR30 | 98.07 | 0.093 |
| 53 | Security | 1.72 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT30 | MR30 | 97.67 | 0.089 |
| 54 | Agriculture | 0.89 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 98.18 | 0.073 |
| 55 | Mapping | 4.34 | Hexacopter X | Separate PDB | AWG 12 | AWG 8 | XT90 | MR30 | 99.26 | 0.086 |
| 56 | Survey | 1.56 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 97.95 | 0.088 |
| 57 | Survey | 0.72 | Hexacopter X | Separate PDB | AWG 22 | AWG 8 | XT30 | MR30 | 95.62 | 0.100 |
| 58 | Mapping | 2.14 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT30 | MR30 | 97.41 | 0.088 |
| 59 | Photography | 1.72 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 97.28 | 0.133 |
| 60 | Agriculture | 1.71 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 97.29 | 0.134 |
| 61 | Videography | 1.39 | Hexacopter X | Separate PDB | AWG 20 | AWG 8 | XT30 | MR30 | 97.52 | 0.106 |
| 62 | Videography | 1.48 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 97.33 | 0.116 |
| 63 | Cargo Delivery | 1.10 | Hexacopter X | Separate PDB | AWG 20 | AWG 8 | XT30 | MR30 | 97.48 | 0.088 |
| 64 | Search & Rescue | 2.61 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT30 | MR30 | 97.25 | 0.096 |
| 65 | Cargo Delivery | 1.62 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 98.58 | 0.133 |
| 66 | Inspection | 2.42 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 97.50 | 0.114 |
| 67 | Mapping | 3.06 | Hexacopter X | Separate PDB | AWG 14 | AWG 8 | XT60 | MR30 | 97.72 | 0.092 |
| 68 | Cargo Delivery | 0.30 | Quadcopter X | 4-in-1 ESC bus | AWG 22 | AWG 8 | XT30 | MR30 | 96.86 | 0.069 |
| 69 | Heavy Lift | 2.33 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 98.37 | 0.115 |
| 70 | Inspection | 2.31 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 97.53 | 0.111 |
| 71 | Mapping | 0.89 | Hexacopter X | Separate PDB | AWG 20 | AWG 8 | XT30 | MR30 | 97.52 | 0.080 |
| 72 | Heavy Lift | 2.13 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 98.43 | 0.117 |
| 73 | Cargo Delivery | 1.91 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 98.50 | 0.124 |
| 74 | Mapping | 2.48 | Hexacopter X | Separate PDB | AWG 14 | AWG 8 | XT60 | MR30 | 97.94 | 0.095 |
| 75 | Videography | 2.73 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 97.44 | 0.130 |
| 76 | Security | 3.86 | Hexacopter X | Separate PDB | AWG 14 | AWG 8 | XT60 | MR30 | 99.17 | 0.111 |
| 77 | Heavy Lift | 2.58 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 98.32 | 0.123 |
| 78 | Mapping | 0.50 | Quadcopter X | 4-in-1 ESC bus | AWG 20 | AWG 8 | XT30 | MR30 | 97.86 | 0.077 |
| 79 | Agriculture | 0.64 | Hexacopter X | Separate PDB | AWG 22 | AWG 8 | XT30 | MR30 | 97.27 | 0.105 |
| 80 | Mapping | 1.11 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 97.27 | 0.084 |
| 81 | Mapping | 1.88 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 97.14 | 0.127 |
| 82 | Heavy Lift | 0.94 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT30 | MR30 | 98.74 | 0.089 |
| 83 | Heavy Lift | 1.35 | Quadcopter X | Separate PDB | AWG 16 | AWG 22 | XT30 | MR30 | 96.76 | 0.097 |
| 84 | Survey | 4.05 | Hexacopter X | Separate PDB | AWG 14 | AWG 8 | XT60 | MR30 | 99.16 | 0.111 |
| 85 | Security | 0.39 | Quadcopter X | 4-in-1 ESC bus | AWG 22 | AWG 8 | XT30 | MR30 | 97.03 | 0.078 |
| 86 | Survey | 1.04 | Quadcopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 98.31 | 0.096 |
| 87 | Cargo Delivery | 2.73 | Hexacopter X | Separate PDB | AWG 14 | AWG 8 | XT60 | MR30 | 98.56 | 0.092 |
| 88 | Photography | 0.50 | Hexacopter X | Separate PDB | AWG 22 | AWG 8 | XT30 | MR30 | 97.39 | 0.101 |
| 89 | Photography | 3.95 | Hexacopter X | Separate PDB | AWG 14 | AWG 8 | XT60 | MR30 | 99.17 | 0.116 |
| 90 | Mapping | 1.73 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 97.27 | 0.129 |
| 91 | Inspection | 0.95 | Hexacopter X | Separate PDB | AWG 20 | AWG 8 | XT30 | MR30 | 97.58 | 0.087 |
| 92 | Inspection | 0.35 | Quadcopter X | 4-in-1 ESC bus | AWG 22 | AWG 8 | XT30 | MR30 | 95.74 | 0.080 |
| 93 | Mapping | 1.69 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 97.31 | 0.132 |
| 94 | Security | 3.45 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT60 | MR30 | 98.08 | 0.125 |
| 95 | Search & Rescue | 1.40 | Hexacopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 98.03 | 0.086 |
| 96 | Cargo Delivery | 0.72 | Hexacopter X | Separate PDB | AWG 20 | AWG 8 | XT30 | MR30 | 97.51 | 0.072 |
| 97 | Cargo Delivery | 1.49 | Quadcopter X | Separate PDB | AWG 16 | AWG 22 | XT60 | MR30 | 96.61 | 0.107 |
| 98 | Cargo Delivery | 2.68 | Hexacopter X | Separate PDB | AWG 16 | AWG 8 | XT30 | MR30 | 98.18 | 0.101 |
| 99 | Inspection | 1.32 | Quadcopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 98.07 | 0.090 |
| 100 | Photography | 1.31 | Quadcopter X | Separate PDB | AWG 18 | AWG 8 | XT30 | MR30 | 97.30 | 0.103 |
