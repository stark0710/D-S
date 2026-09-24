import math
from backend.design.multirotor.propeller.propeller_models import PropellerCandidate, PropellerContext

class PropellerPerformance:
    """
    Calculates operational aerodynamic metrics for multirotor propellers.
    """
    @staticmethod
    def calculate_performance(candidate: PropellerCandidate, context: PropellerContext) -> None:
        """
        Calculates hover RPMs, max RPM draws, tip speeds, and absorbed power values.
        """
        motor_spec = context.motor_spec
        frame_spec = context.frame_spec
        prop = candidate.propeller_record
        
        # 1. Load thrust requirements from motor optimization results
        hover_thrust = motor_spec.hover_thrust_n
        max_thrust = motor_spec.max_thrust_n
        candidate.hover_thrust_n = hover_thrust
        candidate.max_thrust_n = max_thrust

        # 2. Sized disc geometry
        d_p = prop.diameter_m
        pitch = prop.pitch_m
        a_disk = (math.pi / 4.0) * (d_p ** 2)
        candidate.disc_area_m2 = a_disk
        candidate.disc_loading_n_m2 = hover_thrust / a_disk

        # 3. Aerodynamic Coefficients
        # Standard propeller thrust coefficient model: C_T = 0.05 + 0.10 * (pitch / d_p)
        c_t = 0.05 + 0.10 * (pitch / d_p)
        if prop.blade_count == 3:
            c_t *= 1.30  # 3-blade thrust scaling factor
            
        rho = 1.225  # sea level air density

        # 4. RPM calculations: T = C_T * rho * n^2 * d_p^4
        # n = sqrt(T / (C_T * rho * d_p^4))
        # RPM = n * 60
        factor = c_t * rho * (d_p ** 4)
        if factor > 0.0:
            hover_n = math.sqrt(hover_thrust / factor)
            max_n = math.sqrt(max_thrust / factor)
            candidate.hover_rpm = hover_n * 60.0
            candidate.max_rpm = max_n * 60.0
        else:
            candidate.hover_rpm = 0.0
            candidate.max_rpm = 0.0

        # 5. Sized tip speed (at max RPM for safety constraint evaluation)
        candidate.tip_speed_m_s = (math.pi * candidate.max_rpm * d_p) / 60.0

        # 6. Sized Power absorbed: P = C_P * rho * n^3 * d_p^5
        # Standard power coefficient model: C_P = C_T * (pitch / d_p) * (1 / prop_eff)
        # Assuming prop efficiency of 75%
        c_p = c_t * (pitch / d_p) / 0.75
        
        hover_n_sec = candidate.hover_rpm / 60.0
        max_n_sec = candidate.max_rpm / 60.0
        
        candidate.hover_power_absorbed_w = c_p * rho * (hover_n_sec ** 3) * (d_p ** 5)
        candidate.max_power_absorbed_w = c_p * rho * (max_n_sec ** 3) * (d_p ** 5)

        # 7. Sized Hover efficiency (g/W)
        g_const = 9.80665
        if candidate.hover_power_absorbed_w > 0.0:
            eff_gw = (hover_thrust * 1000.0) / (candidate.hover_power_absorbed_w * g_const)
            candidate.hover_efficiency_g_w = round(eff_gw, 2)
        else:
            candidate.hover_efficiency_g_w = 0.0
