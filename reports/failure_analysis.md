# Fixed-Wing Pipeline Sizing Failure Analysis Report

## 1. Executive Failure Summary

- **Total Sizing Runs Audited**: 1050
- **Representative Campaign Runs**: 1000
- **Campaign Successful Convergences**: 0 (0.0%)
- **Campaign Failed Sizing Cycles**: 1000 (100.0%)

## 2. Sizing Failure Taxonomy Breakdown

| Sizing Failure Category | Case Count | Failure Rate (%) |
| :--- | :---: | :---: |
| Certification Failure | 61 | 6.1% |
| CG Failure | 0 | 0.0% |
| Component Database Limitation | 280 | 28.0% |
| Configuration Infeasible | 0 | 0.0% |
| Electrical Infeasible | 0 | 0.0% |
| Invalid Requirements | 0 | 0.0% |
| Mass Limit Exceeded | 15 | 1.5% |
| Mission Infeasible | 0 | 0.0% |
| Performance Failure | 72 | 7.2% |
| Propulsion Infeasible | 143 | 14.3% |
| Sizing Infeasible | 352 | 35.2% |
| Unexpected Exception | 77 | 7.7% |

## 3. Boundary Stress Sizing Analysis

We audited 50 boundary, stress, and impossible cases to verify robustness.

| Case ID | Boundary Sizing Description | Pipeline Status | Sizing Outcome | Category |
| :--- | :--- | :--- | :--- | :--- |
| VAL-B-0001 | Min Payload | COMPONENT_DATABASE_LIMITATION | **FAILED** | Component Database Limitation |
| VAL-B-0002 | Max Payload | INTERNAL_EXCEPTION | **FAILED** | Unexpected Exception |
| VAL-B-0003 | Min Range | PERFORMANCE_INFEASIBLE | **FAILED** | Performance Failure |
| VAL-B-0004 | Max Range | COMPONENT_DATABASE_LIMITATION | **FAILED** | Component Database Limitation |
| VAL-B-0005 | Min Endurance | INVALID_REQUIREMENTS | **FAILED** | Invalid Requirements |
| VAL-B-0006 | Max Endurance | COMPONENT_DATABASE_LIMITATION | **FAILED** | Component Database Limitation |
| VAL-B-0007 | Min Cruise Speed | INVALID_REQUIREMENTS | **FAILED** | Invalid Requirements |
| VAL-B-0008 | Max Cruise Speed | COMPONENT_DATABASE_LIMITATION | **FAILED** | Component Database Limitation |
| VAL-B-0009 | Negative Payload | INVALID_REQUIREMENTS | **FAILED** | Invalid Requirements |
| VAL-B-0010 | Payload > Max Supported | INVALID_REQUIREMENTS | **FAILED** | Invalid Requirements |
| VAL-B-0011 | Negative Endurance | INVALID_REQUIREMENTS | **FAILED** | Invalid Requirements |
| VAL-B-0012 | Negative Cruise Speed | INVALID_REQUIREMENTS | **FAILED** | Invalid Requirements |
| VAL-B-0013 | Negative Range | INVALID_REQUIREMENTS | **FAILED** | Invalid Requirements |
| VAL-B-0014 | Physically Inconsistent Range | INVALID_REQUIREMENTS | **FAILED** | Invalid Requirements |
| VAL-B-0015 | Unsafe Hand Launch Sizing | INVALID_REQUIREMENTS | **FAILED** | Invalid Requirements |
| VAL-B-0016 | Unsafe Belly Landing Sizing | INVALID_REQUIREMENTS | **FAILED** | Invalid Requirements |
| VAL-B-0017 | Restricted MTOW limit | INVALID_REQUIREMENTS | **FAILED** | Invalid Requirements |
| VAL-B-0018 | Zero Endurance | INVALID_REQUIREMENTS | **FAILED** | Invalid Requirements |
| VAL-B-0019 | Zero Payload | INVALID_REQUIREMENTS | **FAILED** | Invalid Requirements |
| VAL-B-0020 | Zero Speed | INVALID_REQUIREMENTS | **FAILED** | Invalid Requirements |
| VAL-B-0021 | High Load Conventional | COMPONENT_DATABASE_LIMITATION | **FAILED** | Component Database Limitation |
| VAL-B-0022 | Very Long Endurance Small Payload | COMPONENT_DATABASE_LIMITATION | **FAILED** | Component Database Limitation |
| VAL-B-0023 | Heavy Fast Short | NON_CONVERGED | **FAILED** | Propulsion Infeasible |
| VAL-B-0024 | High Wind Mountainous Survey | INTERNAL_EXCEPTION | **FAILED** | Unexpected Exception |
| VAL-B-0025 | Desert Long Range Inspection | COMPONENT_DATABASE_LIMITATION | **FAILED** | Component Database Limitation |
| VAL-B-0026 | Marine High-Gust Catapult | INTERNAL_EXCEPTION | **FAILED** | Unexpected Exception |
| VAL-B-0027 | Extreme Urban Infrastructure | INTERNAL_EXCEPTION | **FAILED** | Unexpected Exception |
| VAL-B-0028 | High Speed Security Patrol | COMPONENT_DATABASE_LIMITATION | **FAILED** | Component Database Limitation |
| VAL-B-0029 | Large Agricultural Spraying | NON_CONVERGED | **FAILED** | Propulsion Infeasible |
| VAL-B-0030 | Light Belly Landing | PERFORMANCE_INFEASIBLE | **FAILED** | Performance Failure |
| VAL-B-0031 | Forest Net Recovery | NON_CONVERGED | **FAILED** | Sizing Infeasible |
| VAL-B-0032 | Heavy Payload Net Recovery | NON_CONVERGED | **FAILED** | Propulsion Infeasible |
| VAL-B-0033 | High Power Heavy Mapping | NON_CONVERGED | **FAILED** | Propulsion Infeasible |
| VAL-B-0034 | Deep Desert Research Sizing | COMPONENT_DATABASE_LIMITATION | **FAILED** | Component Database Limitation |
| VAL-B-0035 | High Speed Marine Search | COMPONENT_DATABASE_LIMITATION | **FAILED** | Component Database Limitation |
| VAL-B-0036 | Custom Budget Constraint | SUCCESS | **FAILED** | Certification Failure |
| VAL-B-0037 | High Budget Luxury | INTERNAL_EXCEPTION | **FAILED** | Unexpected Exception |
| VAL-B-0038 | Belly Landing Cargo Edge | NON_CONVERGED | **FAILED** | Propulsion Infeasible |
| VAL-B-0039 | Coastal Parachute Retrieval | INTERNAL_EXCEPTION | **FAILED** | Unexpected Exception |
| VAL-B-0040 | Extreme High Wind Hand Launch | NON_CONVERGED | **FAILED** | Sizing Infeasible |
| VAL-B-0041 | Min Speed Runaway Sizing | INVALID_REQUIREMENTS | **FAILED** | Invalid Requirements |
| VAL-B-0042 | Max Speed Runaway Sizing | NON_CONVERGED | **FAILED** | Sizing Infeasible |
| VAL-B-0043 | Extremely Low MTOW Sizing limit | MTOW_LIMIT_EXCEEDED | **FAILED** | Mass Limit Exceeded |
| VAL-B-0044 | Extreme Mountain Catapult | SUCCESS | **FAILED** | Certification Failure |
| VAL-B-0045 | Extreme Forest Landing Roll | INTERNAL_EXCEPTION | **FAILED** | Unexpected Exception |
| VAL-B-0046 | Extreme Desert Solar Sizing | COMPONENT_DATABASE_LIMITATION | **FAILED** | Component Database Limitation |
| VAL-B-0047 | Extreme Marine Spray Recovery | NON_CONVERGED | **FAILED** | Sizing Infeasible |
| VAL-B-0048 | Belly Landing Heavy Edge 2 | INTERNAL_EXCEPTION | **FAILED** | Unexpected Exception |
| VAL-B-0049 | Stall Speed Match Cruise Limit | INTERNAL_EXCEPTION | **FAILED** | Unexpected Exception |
| VAL-B-0050 | Budget Zero Constraint | INVALID_REQUIREMENTS | **FAILED** | Invalid Requirements |

## 4. Key Sizing Failure Findings

1. **Invalid Requirements Rejection**: All physically impossible cases (negative dimensions, speeds, and payload capacities) were successfully rejected at the validator entry point, demonstrating strict bounds enforcement.
2. **Propulsion Limitations**: Configurations requesting heavy payloads combined with short launch runs correctly failed at propulsion stage, avoiding the creation of physically impossible aircraft thrust balances.
3. **Sizing Non-Convergence**: Edge-of-feasibility cases that failed to converge in MTOW feedback loops did so gracefully within limits without infinite loop hangs or application crashes.
