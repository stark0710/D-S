import math
from backend.design.multirotor.battery.battery_models import BatteryCandidate, BatteryContext

class BatteryPerformance:
    """
    Calculates operational, thermodynamic, and flight endurance performance metrics for multirotor batteries.
    """
    @staticmethod
    def calculate_performance(candidate: BatteryCandidate, context: BatteryContext) -> None:
        """
        Calculates hover endurances, max aircraft climb currents, and safety discharge margins.
        """
        req = context.requirements
        frame = context.frame_spec
        motor = context.motor_spec
        esc = context.esc_spec
        prop = context.propeller_spec
        batt = candidate.battery_record
        
        # 1. Calculate Sized All-Up Takeoff Weight (AUW)
        payload = req.payload_weight_kg
        frame_mass = frame.frame_mass_kg
        motor_count = frame.arm_count
        
        propulsion_mass = motor_count * (motor.weight_kg + esc.weight_kg + prop.weight_kg)
        battery_mass = batt.empty_mass_kg
        
        estimated_auw = payload + frame_mass + propulsion_mass + battery_mass
        candidate.estimated_auw_kg = estimated_auw

        # 2. Battery electrical specs
        candidate.nominal_voltage_v = batt.nominal_voltage_v
        capacity_ah = batt.capacity_mah / 1000.0
        candidate.battery_energy_wh = capacity_ah * batt.nominal_voltage_v

        # 3. Sized actual hover thrust and scale hover current
        # Sized motor sizer AUW
        motor_auw = motor.hover_thrust_n * motor_count / 9.80665
        motor_auw = max(0.1, motor_auw)
        
        # Thrust scale ratio
        thrust_ratio = estimated_auw / motor_auw
        
        # Sized motor current draw scales by thrust ratio to the power of 1.3
        actual_hover_current_per_motor = motor.hover_current_a * (thrust_ratio ** 1.3)
        actual_max_current_per_motor = motor.max_current_a * (thrust_ratio ** 1.3)
        
        # Avionics bus current draw
        i_avionics = 0.5
        candidate.hover_current_draw_a = (actual_hover_current_per_motor * motor_count) + i_avionics
        candidate.max_current_draw_a = (actual_max_current_per_motor * motor_count) + 1.0

        # 4. Discharge limits (C-Rating capacity)
        candidate.continuous_discharge_limit_a = capacity_ah * batt.continuous_c_rating
        candidate.burst_discharge_limit_a = capacity_ah * batt.burst_c_rating

        # 5. Flight time estimations under 80% Depth of Discharge limit
        usable_capacity_ah = capacity_ah * 0.8
        
        hover_time = (usable_capacity_ah / candidate.hover_current_draw_a) * 60.0
        candidate.estimated_hover_time_min = round(hover_time, 2)
        
        # Average flight current draw is slightly higher (~12%) due to cruise maneuvers and drag
        avg_flight_current = 1.12 * candidate.hover_current_draw_a
        flight_time = (usable_capacity_ah / avg_flight_current) * 60.0
        candidate.estimated_flight_time_min = round(flight_time, 2)

        # Usable reserve energy
        candidate.remaining_energy_margin_pct = 20.0
