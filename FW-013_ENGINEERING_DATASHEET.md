# ENGINEERING SPECIFICATION DATASHEET: FW-013
**Aircraft Design Synthesis Handoff Report**
Generated at: 2026-08-01 (Torq Wings Studio V3 Phase 5D)
Status: **SUCCESS**

---
## 1. Executive Summary Specification
| Parameter | Value |
| :--- | :--- |
| Case ID | FW-013 |
| Mission Category | SURVEY |
| Target MTOW (kg) | 5.720 kg |
| Wing Configuration | High Wing |
| Propulsion Configuration | Pusher |
| Wingspan | 2.101 m |
| Wing Area | 0.4205 m² |
| Aspect Ratio | 10.50 |
| Selected Root Airfoil | Clark Y |
| Selected Motor | T-Motor MN5008 |
| Selected Propeller | 22x12 APC |
| Battery Capacity (Wh) | 260.40 Wh |
| Static Stability Margin | 18.00% |
| Stall Speed | 46.70 km/h |
| Cruise Speed | 85.30 km/h |
| Range (Calculated) | 90.71 km |
| Endurance (Calculated) | 63.80 min |

## 2. Mission Requirements
N/A

## 3. Configuration Analysis
| Parameter | Value |
| :--- | :--- |
| wing_position | High Wing |
| propulsion_layout | Pusher |
| tail_configuration | Conventional |
| landing_gear_configuration | Belly Landing |
| engine_count | 1 |
| payload_arrangement | Under-Nose Camera Bay |
| architecture | High-Wing Rear-Pusher Survey Drone |

## 4. Wing Geometry & Sizing
| Parameter | Value |
| :--- | :--- |
| span_m | 2.1012 |
| area_m2 | 0.4205 |
| aspect_ratio | 10.5000 |
| wing_loading_kg_m2 | 13.4674 |
| root_chord_m | 0.2668 |
| tip_chord_m | 0.1334 |
| taper_ratio | 0.5000 |
| sweep_angle_deg | 0.0000 |
| dihedral_angle_deg | 3.0000 |
| wing_incidence_deg | 2.0000 |
| mean_aerodynamic_chord_m | 0.2075 |
| quarter_chord_x_m | 0.0519 |
| reference_area_m2 | 0.4205 |

### Wing Sizing Notes
- Wing sizing complete. Aspect Ratio: 10.50, Wing Area: 0.4205 m2.
- Estimated MTOW: 5.66 kg, Cruise Lift Coefficient: 0.390.
- Estimated Stall Speed: 46.7 km/h.
- Estimated Wing weight: 0.600 kg.

## 5. Airfoil Selection
| Parameter | Value |
| :--- | :--- |
| Selected Root Airfoil | Clark Y |
| Selected Tip Airfoil | NACA 0012 |
| Reynolds Number (Root) | N/A |
| Section drag coeff (Cd0) | N/A |
| Section max lift (Clmax) | 1.3130 |

## 6. Tail Geometry
### Horizontal Tail
| Parameter | Value |
| :--- | :--- |
| area_m2 | 0.0346 |
| span_m | 0.3950 |
| chord_root_m | 0.1030 |
| chord_tip_m | 0.0720 |
| aspect_ratio | 4.5000 |
| sweep_angle_deg | 0.0000 |
| taper_ratio | 0.7000 |
| incidence_angle_deg | 0.0000 |

### Vertical Tail
| Parameter | Value |
| :--- | :--- |
| area_m2 | 0.0280 |
| height_m | 0.2370 |
| chord_root_m | 0.1480 |
| chord_tip_m | 0.0890 |
| aspect_ratio | 2.0000 |
| sweep_angle_deg | 20.0000 |
| taper_ratio | 0.6000 |

### Volume Coefficients
| Parameter | Value |
| :--- | :--- |
| horizontal_V_h | 0.5000 |
| vertical_V_v | 0.0400 |

## 7. Fuselage Sizing & Component Layout
| Parameter | Value |
| :--- | :--- |
| length_m | 1.5760 |
| width_m | 0.2360 |
| height_m | 0.2890 |
| nose_length_m | 0.2840 |
| tail_cone_length_m | 0.6300 |
| cross_section_type | Rectangular |
| wing_attachment_x_m | 0.5040 |
| tail_attachment_x_m | 1.4970 |
| payload_bay_length_m | 0.3470 |
| payload_bay_width_m | 0.2260 |
| payload_bay_height_m | 0.2170 |
| payload_bay_volume_m3 | 0.0170 |
| battery_bay_length_m | 0.2520 |
| battery_bay_width_m | 0.2260 |
| battery_bay_height_m | 0.1590 |
| battery_bay_volume_m3 | 0.0091 |
| avionics_bay_length_m | 0.2210 |
| avionics_bay_width_m | 0.2260 |
| avionics_bay_height_m | 0.1010 |
| total_volume_m3 | 0.0764 |

### Component Placement Locations (m from nose)
| Parameter | Value |
| :--- | :--- |
| calculated_cg_x_m | 0.5560 |
| target_cg_x_m | 0.5560 |
| static_margin_pct | 0.0000 |
| component_locations | **Motor**: 1.4970<br>**Payload**: 0.5560<br>**Battery**: 0.0500<br>**FlightController**: 0.5560<br>**GPS**: 0.6560<br>**Receiver**: 0.7060<br>**Telemetry**: 0.4060<br>**ESC**: 1.5770 |
| component_masses | **FuselageStructure**: 1.5000<br>**Motor**: 0.4000<br>**Payload**: 0.6100<br>**Battery**: 1.2000 |

## 8. Propulsion System Specification
| Parameter | Value |
| :--- | :--- |
| Selected Motor | T-Motor MN5008 |
| Selected Propeller | 22x12 APC |
| Propulsion Layout | Single Pusher |
| Propulsion Weight (kg) | 0.2050 |

### Cruise Propulsion Analysis
| Parameter | Value |
| :--- | :--- |
| cruise_speed_kmh | 85.3000 |
| required_cruise_thrust_n | 4.0400 |
| prop_rpm_cruise | 4664.0000 |
| throttle_setting_pct | 25.7000 |
| metadata |  |

### Thrust & Climb Limits
| Parameter | Value |
| :--- | :--- |
| required_cruise_thrust_n | 4.0400 |
| required_takeoff_thrust_n | 27.7700 |
| estimated_static_thrust_n | 46.0400 |
| thrust_to_weight_ratio | 0.8300 |
| power_loading_w_kg | 123.6100 |
| metadata |  |

### System Electrical Power Analysis
| Parameter | Value |
| :--- | :--- |
| required_cruise_power_w | 179.8000 |
| required_climb_power_w | 492.7000 |
| maximum_power_w | 700 |
| current_draw_cruise_a | 8.1000 |
| metadata | **voltage_v**: 22.2000<br>**motor_weight_g**: 140 |

### Propulsive Efficiency
| Parameter | Value |
| :--- | :--- |
| motor_efficiency | 0.8200 |
| propeller_efficiency | 0.6500 |
| total_system_efficiency | 0.5330 |
| energy_consumption_per_km_wh | 2.1100 |
| metadata |  |

## 9. Electronics & Avionics
| Parameter | Value |
| :--- | :--- |
| Flight Controller | Holybro Pixhawk 6C |
| GPS Navigation System | RTK GNSS |
| Telemetry Module | Microhard PMDDL2450 |
| Companion Computer | Raspberry Pi 4 Model B |
| Receiver | ExpressLRS 915M RX |
| Sensors | Holybro Digital Airspeed Sensor<br>Matek CAN Compass<br>Benewake TFmini Plus Lidar |

## 10. Battery System Sizing
| Parameter | Value |
| :--- | :--- |
| Battery Weight (kg) | 1.3020 |
| Battery Mass Fraction (%) | 22.80% |
| Battery Energy (Wh) | 260.4000 |
| Battery Specific Energy (Wh/kg) | 200.0000 |

## 11. Payload Configuration
| Parameter | Value |
| :--- | :--- |
| Installed Payload Mass (kg) | 0.5100 |
| Requested Payload Mass (kg) | 0.6100 |
| Design Margin (kg) | 0.0000 |
| Selected Sensors / Cargo | Sony RX1R II (RGB) |

## 12. Mass & Weight Breakdown
| Parameter | Value |
| :--- | :--- |
| structural_weight_kg | 3.4430 |
| propulsion_weight_kg | 0.2050 |
| avionics_weight_kg | 0.2600 |
| payload_weight_kg | 0.5100 |
| battery_fuel_weight_kg | 1.3020 |
| useful_load_kg | 1.8120 |
| payload_fraction | 0.0890 |
| battery_fraction | 0.2280 |

## 13. Center of Gravity (CG) & Stability
| Parameter | Value |
| :--- | :--- |
| CG Location X (m from nose) | 0.6060 |
| CG Location Y (m) | 0.0000 |
| CG Location Z (m) | -0.0190 |
| Neutral Point (m from nose) | 0.6430 |
| Static Margin (%) | 18.00% |

## 14. Aerodynamics & Flight Performance
### Cruising Performance
| Parameter | Value |
| :--- | :--- |
| maximum_speed_kmh | 153.8000 |
| cruise_speed_kmh | 85.3000 |
| minimum_controllable_speed_kmh | 53.7000 |
| best_glide_ratio | 17.1500 |
| max_rate_of_climb_m_s | 5.5600 |
| metadata |  |

### Stall Speed Analysis
| Parameter | Value |
| :--- | :--- |
| stall_speed_clean_kmh | 46.7000 |
| stall_speed_landing_kmh | 41.5000 |
| stall_angle_of_attack_deg | 13.7000 |
| stall_characteristics_warning | docile nose drop |
| metadata |  |

### Range Sizing
| Parameter | Value |
| :--- | :--- |
| maximum_range_km | 106.7100 |
| cruise_range_km | 90.7100 |
| energy_consumption_rate_wh_km | 2.4400 |
| metadata |  |

### Endurance Sizing
| Parameter | Value |
| :--- | :--- |
| maximum_endurance_min | 75.0600 |
| cruise_endurance_min | 63.8000 |
| average_power_draw_w | 208.2000 |
| metadata |  |

### Takeoff Performance
| Parameter | Value |
| :--- | :--- |
| takeoff_distance_m | 25.5900 |
| rotation_speed_m_s | 16.2200 |
| ground_acceleration_m_s2 | 7.7500 |
| takeoff_duration_s | 2.0900 |
| metadata |  |

### Landing Performance
| Parameter | Value |
| :--- | :--- |
| landing_distance_m | 8.0500 |
| approach_speed_m_s | 14.9800 |
| braking_deceleration_m_s2 | 4.5000 |
| landing_duration_s | 3.3300 |
| metadata |  |

### Aerodynamic Coefficients
| Parameter | Value |
| :--- | :--- |
| cruise_lift_coefficient | 0.3940 |
| cruise_drag_coefficient | 0.0287 |
| lift_to_drag_ratio | 13.7000 |
| zero_lift_drag_coefficient | 0.0230 |
| induced_drag_factor | 0.0370 |
| metadata |  |

## 15. Compliance Verification & Risk Assessment
| Parameter | Value |
| :--- | :--- |
| Verification Status | VERIFIED |
| Mission Readiness | Ready |
| Violations Count | 0 |
| Warnings Count | 1 |

### Warnings
- **WARNING**: DIAGNOSTICS_AR_ATTEMPTED: [10.5]

### Verification Risk Assessment
| Parameter | Value |
| :--- | :--- |
| overall_risk_score | 0.0000 |
| risk_level | Low |
| identified_risks |  |
| mitigation_actions | Adjust battery/payload longitudinal placements inside the fuselage to correct CG offsets.<br>Verify all autopilot parameters meet redundancy profiles.<br>Improve camera mounting vibration isolations to ensure clean camera stabilization. |

---
## 16. Final Aircraft Design Configuration File Specification
```json
{
    "success": true,
    "status": {},
    "iterations": 13,
    "converged": true,
    "convergence_history": [
        {
            "iteration": 1,
            "mtow_old": 1.525,
            "mtow_new": 2.5308,
            "absolute_delta_kg": 1.0058,
            "relative_delta": 0.659541,
            "converged": false
        },
        {
            "iteration": 2,
            "mtow_old": 2.5308,
            "mtow_new": 3.2569,
            "absolute_delta_kg": 0.7261,
            "relative_delta": 0.286905,
            "converged": false
        },
        {
            "iteration": 3,
            "mtow_old": 3.2569,
            "mtow_new": 3.821,
            "absolute_delta_kg": 0.5641,
            "relative_delta": 0.173202,
            "converged": false
        },
        {
            "iteration": 4,
            "mtow_old": 3.821,
            "mtow_new": 4.2575,
            "absolute_delta_kg": 0.4365,
            "relative_delta": 0.114237,
            "converged": false
        },
        {
            "iteration": 5,
            "mtow_old": 4.2575,
            "mtow_new": 4.5931,
            "absolute_delta_kg": 0.3356,
            "relative_delta": 0.078826,
            "converged": false
        },
        {
            "iteration": 6,
            "mtow_old": 4.5931,
            "mtow_new": 4.9005,
            "absolute_delta_kg": 0.3074,
            "relative_delta": 0.066926,
            "converged": false
        },
        {
            "iteration": 7,
            "mtow_old": 4.9005,
            "mtow_new": 5.1274,
            "absolute_delta_kg": 0.2269,
            "relative_delta": 0.046301,
            "converged": false
        },
        {
            "iteration": 8,
            "mtow_old": 5.1274,
            "mtow_new": 5.3011,
            "absolute_delta_kg": 0.1737,
            "relative_delta": 0.033877,
            "converged": false
        },
        {
            "iteration": 9,
            "mtow_old": 5.3011,
            "mtow_new": 5.4323,
            "absolute_delta_kg": 0.1312,
            "relative_delta": 0.02475,
            "converged": false
        },
        {
            "iteration": 10,
            "mtow_old": 5.4323,
            "mtow_new": 5.5311,
            "absolute_delta_kg": 0.0988,
            "relative_delta": 0.018188,
            "converged": false
        },
        {
            "iteration": 11,
            "mtow_old": 5.5311,
            "mtow_new": 5.606,
            "absolute_delta_kg": 0.0749,
            "relative_delta": 0.013542,
            "converged": false
        },
        {
            "iteration": 12,
            "mtow_old": 5.606,
            "mtow_new": 5.663,
            "absolute_delta_kg": 0.057,
            "relative_delta": 0.010168,
            "converged": false
        },
        {
            "iteration": 13,
            "mtow_old": 5.663,
            "mtow_new": 5.7058,
            "absolute_delta_kg": 0.0428,
            "relative_delta": 0.007558,
            "converged": true
        }
    ],
    "mission_result": {
        "mission_profile": {
            "mission_category": {},
            "payload_kg": 0.61,
            "flight_time_min": 63.8,
            "cruise_speed_kmh": 85.3,
            "stall_speed_target_kmh": 45.0,
            "maximum_takeoff_weight_limit_kg": 5.663,
            "operational_altitude_m": 150.0,
            "mission_range_km": 14.3,
            "launch_method": {},
            "landing_method": {},
            "budget": 15000.0,
            "environment": {},
            "autonomy_level": {},
            "air_density_kg_m3": 1.2075,
            "energy_demand_kwh": 0.0821,
            "cruise_emphasis": 0.7,
            "payload_emphasis": 0.3,
            "launch_recovery_complexity": 0.5,
            "environmental_complexity": 0.2,
            "operational_risk_score": 0.2,
            "mission_summary": "Fixed-Wing Survey Mission Profile. Payload: 0.61 kg, Endurance: 63.8 min, Speed: 85.3 km/h, Altitude: 150.0 m. Est. Energy: 0.08 kWh. Complexity: Low.",
            "metadata": {
                "complexity_score": 14.71,
                "complexity_category": "Low"
            }
        },
        "mission_category": {},
        "mission_score": 92.64,
        "complexity": "Low",
        "engineering_requirements": {
            "payload_mass_kg": 0.61,
            "flight_time_sec": 3828.0,
            "cruise_speed_m_s": 23.694444444444443,
            "stall_speed_target_m_s": 12.5,
            "mission_range_m": 14300.0,
            "operating_altitude_m": 150.0,
            "environment": "Rural",
            "launch_method": "Hand Launch",
            "landing_method": "Parachute",
            "autonomy_level": "Fully Autonomous"
        },
        "constraints": {
            "minimum_payload_kg": 0.61,
            "minimum_range_km": 14.3,
            "minimum_endurance_min": 63.8,
            "target_cruise_speed_kmh": 85.3,
            "maximum_stall_speed_kmh": 45.0,
            "maximum_takeoff_weight_kg": 25.0,
            "budget_limit": 15000.0,
            "required_launch_method": {},
            "required_landing_method": {},
            "operating_environment": {},
            "required_autonomy_level": {}
        },
        "recommendations": [
            "Use a high-resolution downward-facing RGB/Multispectral camera payload.",
            "Optimize wing design for steady roll/pitch holding to ensure clear mapping images.",
            "Design for an autopilot system capable of grid-based waypoint flight patterns."
        ],
        "warnings": [],
        "metadata": {
            "engine_version": "1.0.0",
            "timestamp": "2026-08-01T09:47:53.769343",
            "feasibility_score": 100.0,
            "complexity_score": 14.71,
            "source_category": "Survey"
        }
    },
    "configuration_result": {
        "selected_configuration": {
            "wing_position": "High Wing",
            "propulsion_layout": "Pusher",
            "tail_configuration": "Conventional",
            "landing_gear_configuration": "Belly Landing",
            "engine_count": "1",
            "payload_arrangement": "Under-Nose Camera Bay",
            "architecture": "High-Wing Rear-Pusher Survey Drone"
        },
        "configuration_score": 94.2,
        "wing_configuration": "High Wing",
        "propulsion_configuration": "Pusher",
        "tail_configuration": "Conventional",
        "landing_gear_configuration": "Belly Landing",
        "engineering_rationale": "A High-Wing Pusher configuration provides a completely unobstructed view for downward-facing mapping sensors. The high wing offers excellent roll stability, which is vital for consistent photogrammetric overlaps. Belly Landing gear is selected to simplify field operations in semi-prepared rural sites.",
        "alternative_configurations": [
            {
                "layout": {
                    "wing_position": "High Wing",
                    "propulsion_layout": "Tractor",
                    "tail_configuration": "Conventional",
                    "landing_gear_configuration": "Tricycle",
                    "engine_count": "1",
                    "payload_arrangement": "CG Bay (Internal)",
                    "architecture": "Conventional High-Wing Tractor (Utility)"
                },
                "score": 89.0,
                "rationale": "Conventional High-Wing Tractor (Utility) offers simplicity=100.0 and aerodynamics=75.0.",
                "comparison": {
                    "config_a_name": "High-Wing Rear-Pusher Survey Drone",
                    "config_b_name": "Conventional High-Wing Tractor (Utility)",
                    "comparison_matrix": {
                        "aerodynamics_delta": 17.0,
                        "simplicity_delta": 0.0,
                        "cost_delta": 0.0,
                        "winner": "A"
                    },
                    "trade_offs": [
                        "Propulsion layout: Pusher affects camera visibility and thrust alignment differently than Tractor.",
                        "Landing gear: Belly Landing affects drag in flight and operational site flexibility relative to Tricycle."
                    ],
                    "rationales": {
                        "aerodynamics": "Config A is 17.0 points better aerodynamically.",
                        "structural_simplicity": "Config A is 0.0 points simpler.",
                        "cost_impact": "Config A is 0.0 points more cost-effective."
                    }
                }
            },
            {
                "layout": {
                    "wing_position": "Mid Wing",
                    "propulsion_layout": "Pusher",
                    "tail_configuration": "Tailless",
                    "landing_gear_configuration": "Belly Landing",
                    "engine_count": "1",
                    "payload_arrangement": "CG Bay (Internal)",
                    "architecture": "Tailless Flying Wing Pusher"
                },
                "score": 88.5,
                "rationale": "Tailless Flying Wing Pusher offers simplicity=95.0 and aerodynamics=100.0.",
                "comparison": {
                    "config_a_name": "High-Wing Rear-Pusher Survey Drone",
                    "config_b_name": "Tailless Flying Wing Pusher",
                    "comparison_matrix": {
                        "aerodynamics_delta": -8.0,
                        "simplicity_delta": 5.0,
                        "cost_delta": 0.0,
                        "winner": "A"
                    },
                    "trade_offs": [
                        "Wing position: High Wing offers different roll stability and ground clearance characteristics compared to Mid Wing.",
                        "Tail assembly: Conventional impacts stability derivatives and structural complexity compared to the Tailless layout."
                    ],
                    "rationales": {
                        "aerodynamics": "Config A is 8.0 points worse aerodynamically.",
                        "structural_simplicity": "Config A is 5.0 points simpler.",
                        "cost_impact": "Config A is 0.0 points more cost-effective."
                    }
                }
            },
            {
                "layout": {
                    "wing_position": "Low Wing",
                    "propulsion_layout": "Tractor",
                    "tail_configuration": "Conventional",
                    "landing_gear_configuration": "Taildragger",
                    "engine_count": "1",
                    "payload_arrangement": "CG Tank",
                    "architecture": "Low-Wing Tractor Sprayer"
                },
                "score": 85.2,
                "rationale": "Low-Wing Tractor Sprayer offers simplicity=100.0 and aerodynamics=72.0.",
                "comparison": {
                    "config_a_name": "High-Wing Rear-Pusher Survey Drone",
                    "config_b_name": "Low-Wing Tractor Sprayer",
                    "comparison_matrix": {
                        "aerodynamics_delta": 20.0,
                        "simplicity_delta": 0.0,
                        "cost_delta": 0.0,
                        "winner": "A"
                    },
                    "trade_offs": [
                        "Wing position: High Wing offers different roll stability and ground clearance characteristics compared to Low Wing.",
                        "Propulsion layout: Pusher affects camera visibility and thrust alignment differently than Tractor.",
                        "Landing gear: Belly Landing affects drag in flight and operational site flexibility relative to Taildragger."
                    ],
                    "rationales": {
                        "aerodynamics": "Config A is 20.0 points better aerodynamically.",
                        "structural_simplicity": "Config A is 0.0 points simpler.",
                        "cost_impact": "Config A is 0.0 points more cost-effective."
                    }
                }
            },
            {
                "layout": {
                    "wing_position": "High Wing",
                    "propulsion_layout": "Twin Boom Pusher",
                    "tail_configuration": "Twin Boom",
                    "landing_gear_configuration": "Skid",
                    "engine_count": "1",
                    "payload_arrangement": "CG Bay (Internal)",
                    "architecture": "Twin-Boom Pusher Monoplane"
                },
                "score": 83.0,
                "rationale": "Twin-Boom Pusher Monoplane offers simplicity=70.0 and aerodynamics=75.0.",
                "comparison": {
                    "config_a_name": "High-Wing Rear-Pusher Survey Drone",
                    "config_b_name": "Twin-Boom Pusher Monoplane",
                    "comparison_matrix": {
                        "aerodynamics_delta": 17.0,
                        "simplicity_delta": 30.0,
                        "cost_delta": 35.0,
                        "winner": "A"
                    },
                    "trade_offs": [
                        "Propulsion layout: Pusher affects camera visibility and thrust alignment differently than Twin Boom Pusher.",
                        "Tail assembly: Conventional impacts stability derivatives and structural complexity compared to the Twin Boom layout.",
                        "Landing gear: Belly Landing affects drag in flight and operational site flexibility relative to Skid."
                    ],
                    "rationales": {
                        "aerodynamics": "Config A is 17.0 points better aerodynamically.",
                        "structural_simplicity": "Config A is 30.0 points simpler.",
                        "cost_impact": "Config A is 35.0 points more cost-effective."
                    }
                }
            },
            {
                "layout": {
                    "wing_position": "High Wing",
                    "propulsion_layout": "Twin Tractor",
                    "tail_configuration": "Conventional",
                    "landing_gear_configuration": "Tricycle",
                    "engine_count": "2",
                    "payload_arrangement": "Fuselage Cargo Bay",
                    "architecture": "Twin-Engine High-Wing Cargo"
                },
                "score": 79.0,
                "rationale": "Twin-Engine High-Wing Cargo offers simplicity=75.0 and aerodynamics=75.0.",
                "comparison": {
                    "config_a_name": "High-Wing Rear-Pusher Survey Drone",
                    "config_b_name": "Twin-Engine High-Wing Cargo",
                    "comparison_matrix": {
                        "aerodynamics_delta": 17.0,
                        "simplicity_delta": 25.0,
                        "cost_delta": 30.0,
                        "winner": "A"
                    },
          
... [truncated specification payload] ...
```