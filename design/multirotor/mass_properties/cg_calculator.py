import math
from typing import Dict, Any

class CgCalculator:
    """
    Computes 3D Center of Gravity coordinates from component coordinates and masses.
    """
    @staticmethod
    def balance_battery(
        coords: Dict[str, tuple[float, float, float]],
        m_payload: float,
        m_battery: float,
        m_frame: float,
        m_motor: float,
        m_prop: float,
        m_esc: float,
        m_wire: float,
        m_pdb: float,
        arm_count: int,
        wheelbase_m: float,
        motor_coords: list[tuple[float, float, float]] = None
    ) -> Dict[str, tuple[float, float, float]]:
        """
        Balances the aircraft by shifting the battery and payload coordinates along X/Y axes.
        Returns a new coordinates dictionary.
        """
        coords = dict(coords)
        if m_battery <= 0.0 and m_payload <= 0.0:
            return coords
            
        sum_mx_other = 0.0
        sum_my_other = 0.0
        
        # 1. Layout components (excluding BatteryPack and PayloadBay)
        if "FlightController" in coords:
            x, y, _ = coords["FlightController"]
            sum_mx_other += 0.015 * x
            sum_my_other += 0.015 * y
        if "GPSReceiver" in coords:
            x, y, _ = coords["GPSReceiver"]
            sum_mx_other += 0.010 * x
            sum_my_other += 0.010 * y
        if "TelemetryModem" in coords:
            x, y, _ = coords["TelemetryModem"]
            sum_mx_other += 0.008 * x
            sum_my_other += 0.008 * y
        if "RcReceiver" in coords:
            x, y, _ = coords["RcReceiver"]
            sum_mx_other += 0.004 * x
            sum_my_other += 0.004 * y
        if "PowerDistributionBoard" in coords:
            x, y, _ = coords["PowerDistributionBoard"]
            sum_mx_other += (m_pdb + m_wire) * x
            sum_my_other += (m_pdb + m_wire) * y
            
        # 2. Frame core (centered at 0, 0)
        # 3. Radially symmetric arms, motors, props, ESCs
        m_single_arm = (m_frame * 0.60) / arm_count
        
        if motor_coords and len(motor_coords) > 0:
            for mx, my, _ in motor_coords:
                sum_mx_other += m_single_arm * (0.5 * mx)
                sum_my_other += m_single_arm * (0.5 * my)
                sum_mx_other += m_motor * mx
                sum_my_other += m_motor * my
                sum_mx_other += m_prop * mx
                sum_my_other += m_prop * my
                sum_mx_other += m_esc * (0.5 * mx)
                sum_my_other += m_esc * (0.5 * my)
        else:
            for k in range(arm_count):
                angle = (2.0 * math.pi * k) / arm_count
                x_arm_center = 0.25 * wheelbase_m * math.cos(angle)
                y_arm_center = 0.25 * wheelbase_m * math.sin(angle)
                x_tip = 0.5 * wheelbase_m * math.cos(angle)
                y_tip = 0.5 * wheelbase_m * math.sin(angle)
                
                sum_mx_other += m_single_arm * x_arm_center
                sum_my_other += m_single_arm * y_arm_center
                sum_mx_other += m_motor * x_tip
                sum_my_other += m_motor * y_tip
                sum_mx_other += m_prop * x_tip
                sum_my_other += m_prop * y_tip
                sum_mx_other += m_esc * (0.5 * x_tip)
                sum_my_other += m_esc * (0.5 * y_tip)
                
        max_r = 0.5 * wheelbase_m
        
        # Balance X-axis
        x_b_init = coords.get("BatteryPack", (0.0, 0.0, 0.0))[0]
        x_p_init = coords.get("PayloadBay", (0.0, 0.0, 0.0))[0]
        
        if "BatteryPack" in coords and m_battery > 0.0:
            if "PayloadBay" in coords and m_payload > 0.0:
                # Try to shift battery, keeping payload at its initial position
                x_b_ideal = -(sum_mx_other + m_payload * x_p_init) / m_battery
                if -max_r <= x_b_ideal <= max_r:
                    x_b = x_b_ideal
                    x_p = x_p_init
                else:
                    # Battery goes to limit
                    x_b = max_r if x_b_ideal > 0 else -max_r
                    # Shift payload to balance
                    x_p = -(sum_mx_other + m_battery * x_b) / m_payload
                    x_p = max(-max_r, min(max_r, x_p))
            else:
                x_b = -sum_mx_other / m_battery
                x_b = max(-max_r, min(max_r, x_b))
                x_p = x_p_init
        else:
            x_b = x_b_init
            if "PayloadBay" in coords and m_payload > 0.0:
                x_p = -sum_mx_other / m_payload
                x_p = max(-max_r, min(max_r, x_p))
            else:
                x_p = x_p_init

        # Balance Y-axis
        y_b_init = coords.get("BatteryPack", (0.0, 0.0, 0.0))[1]
        y_p_init = coords.get("PayloadBay", (0.0, 0.0, 0.0))[1]
        
        if "BatteryPack" in coords and m_battery > 0.0:
            if "PayloadBay" in coords and m_payload > 0.0:
                # Try to shift battery, keeping payload at its initial position
                y_b_ideal = -(sum_my_other + m_payload * y_p_init) / m_battery
                if -max_r <= y_b_ideal <= max_r:
                    y_b = y_b_ideal
                    y_p = y_p_init
                else:
                    # Battery goes to limit
                    y_b = max_r if y_b_ideal > 0 else -max_r
                    # Shift payload to balance
                    y_p = -(sum_my_other + m_battery * y_b) / m_payload
                    y_p = max(-max_r, min(max_r, y_p))
            else:
                y_b = -sum_my_other / m_battery
                y_b = max(-max_r, min(max_r, y_b))
                y_p = y_p_init
        else:
            y_b = y_b_init
            if "PayloadBay" in coords and m_payload > 0.0:
                y_p = -sum_my_other / m_payload
                y_p = max(-max_r, min(max_r, y_p))
            else:
                y_p = y_p_init

        if "BatteryPack" in coords:
            _, _, bz = coords["BatteryPack"]
            coords["BatteryPack"] = (x_b, y_b, bz)
        if "PayloadBay" in coords:
            _, _, pz = coords["PayloadBay"]
            coords["PayloadBay"] = (x_p, y_p, pz)
            
        return coords

    @staticmethod
    def calculate_cg(
        coords: Dict[str, tuple[float, float, float]],
        m_payload: float,
        m_battery: float,
        m_frame: float,
        m_motor: float,
        m_prop: float,
        m_esc: float,
        m_wire: float,
        m_pdb: float,
        arm_count: int,
        wheelbase_m: float,
        motor_coords: list[tuple[float, float, float]] = None
    ) -> tuple[float, float, float]:
        """
        Calculates center of gravity (X_cg, Y_cg, Z_cg) relative to geometric frame center.
        """
        components = []
        
        # 1. Layout components
        if "FlightController" in coords:
            components.append((0.015, coords["FlightController"]))
        if "GPSReceiver" in coords:
            components.append((0.010, coords["GPSReceiver"]))
        if "TelemetryModem" in coords:
            components.append((0.008, coords["TelemetryModem"]))
        if "RcReceiver" in coords:
            components.append((0.004, coords["RcReceiver"]))
        if "PowerDistributionBoard" in coords:
            components.append((m_pdb, coords["PowerDistributionBoard"]))
            components.append((m_wire, coords["PowerDistributionBoard"]))
            
        if "BatteryPack" in coords:
            components.append((m_battery, coords["BatteryPack"]))
        if "PayloadBay" in coords:
            components.append((m_payload, coords["PayloadBay"]))
            
        # 2. Frame central core
        components.append((m_frame * 0.40, (0.0, 0.0, 0.0)))
        
        # 3. Arms, motors, propellers, ESCs
        m_single_arm = (m_frame * 0.60) / arm_count
        
        if motor_coords and len(motor_coords) > 0:
            for mx, my, mz in motor_coords:
                components.append((m_single_arm, (0.5 * mx, 0.5 * my, 0.5 * mz)))
                components.append((m_motor, (mx, my, mz + 0.02)))
                components.append((m_prop, (mx, my, mz + 0.025)))
                components.append((m_esc, (0.5 * mx, 0.5 * my, mz - 0.01)))
        else:
            for k in range(arm_count):
                angle = (2.0 * math.pi * k) / arm_count
                x_arm_center = 0.25 * wheelbase_m * math.cos(angle)
                y_arm_center = 0.25 * wheelbase_m * math.sin(angle)
                x_tip = 0.5 * wheelbase_m * math.cos(angle)
                y_tip = 0.5 * wheelbase_m * math.sin(angle)
                
                components.append((m_single_arm, (x_arm_center, y_arm_center, 0.0)))
                components.append((m_motor, (x_tip, y_tip, 0.02)))
                components.append((m_prop, (x_tip, y_tip, 0.025)))
                components.append((m_esc, (0.5 * x_tip, 0.5 * y_tip, -0.01)))
                
        # 4. Run sum
        total_m = 0.0
        sum_mx = 0.0
        sum_my = 0.0
        sum_mz = 0.0
        
        for mass, (x, y, z) in components:
            total_m += mass
            sum_mx += mass * x
            sum_my += mass * y
            sum_mz += mass * z
            
        cg_x = sum_mx / total_m
        cg_y = sum_my / total_m
        cg_z = sum_mz / total_m
        
        return cg_x, cg_y, cg_z
