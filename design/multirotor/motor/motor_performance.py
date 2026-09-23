import math
from backend.design.multirotor.motor.motor_models import MotorCandidate, MotorContext

class MotorPerformance:
    """
    Calculates operational and thermodynamic performance metrics for multirotor motors.
    """
    @staticmethod
    def calculate_performance(candidate: MotorCandidate, context: MotorContext) -> None:
        """
        Calculates hover currents, max current draws, electrical powers, and efficiencies.
        """
        req = context.requirements
        frame = context.frame_spec
        strategy = context.strategy_spec
        motor = candidate.motor_record
        
        # 1. Estimate All-Up Takeoff Weight (AUW)
        payload = context.requirements.payload_weight_kg
        frame_mass = frame.frame_mass_kg
        motor_count = frame.arm_count
        motor_mass = motor.empty_mass_kg
        
        # Sized battery mass: scales with payload and target flight time
        est_batt_mass = payload * 1.5 + (strategy.engineering_targets.target_hover_time_min / 30.0) * 0.4
        est_batt_mass = max(0.2, est_batt_mass)
        
        estimated_auw = payload + frame_mass + (motor_count * motor_mass) + est_batt_mass
        candidate.estimated_auw_kg = estimated_auw

        # 2. Hover and maximum thrust requirements
        g = 9.80665
        total_hover_thrust_n = estimated_auw * g
        hover_thrust_per_motor = total_hover_thrust_n / motor_count
        candidate.hover_thrust_n = hover_thrust_per_motor
        
        target_tw = strategy.engineering_targets.target_thrust_to_weight_ratio
        max_required_thrust = hover_thrust_per_motor * target_tw
        candidate.max_thrust_n = max_required_thrust

        # 3. Throttle Hover percentage
        # Throttle is proportional to square root of thrust fraction
        if motor.max_thrust_n > 0:
            pct = math.sqrt(hover_thrust_per_motor / motor.max_thrust_n) * 100.0
            candidate.throttle_hover_pct = min(100.0, max(0.0, pct))
        else:
            candidate.throttle_hover_pct = 100.0

        # 4. Sized Power and Current
        # Nominal battery voltage
        v_batt = 0.5 * (motor.min_voltage_v + motor.max_voltage_v)
        v_batt = max(3.7, v_batt)
        
        # Disk area calculation
        # Max propeller size is read from frame spec envelope or limits
        # standard propeller size is ~90% of max allowed propeller diameter
        max_prop_d = frame.envelope_dimensions_m[0] - frame.wheelbase_m
        max_prop_d = max(0.127, max_prop_d)  # default 5 inch min
        prop_d = 0.9 * max_prop_d
        
        a_disk = (math.pi / 4.0) * (prop_d ** 2)
        
        # Induced hover power using BEMT: P_ind = sqrt(T^3 / 2 rho A)
        rho = 1.225  # sea level air density
        p_induced = math.sqrt((hover_thrust_per_motor ** 3) / (2.0 * rho * a_disk))
        p_shaft = p_induced / 0.7  # 70% propeller efficiency
        
        # Motor Efficiency: scales down with higher KV (losses) and throttle
        base_efficiency = 0.86 - 0.05 * (motor.kv_rating / 2500.0)
        efficiency = max(0.60, base_efficiency - 0.05 * (candidate.throttle_hover_pct / 100.0))
        candidate.motor_efficiency = efficiency
        
        # Electrical hover power and current draw
        p_hover_elec = p_shaft / efficiency
        candidate.hover_power_w = p_hover_elec
        
        candidate.hover_current_a = p_hover_elec / v_batt
        
        # Climb / Max Current Draw
        candidate.max_current_a = candidate.hover_current_a * (target_tw ** 1.35)
