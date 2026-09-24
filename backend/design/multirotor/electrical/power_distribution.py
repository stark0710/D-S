from dataclasses import dataclass
from typing import Dict, Any

@dataclass(slots=True)
class PowerDistributionBudget:
    """
    Compilation of power, voltage, and current budgets for the aircraft electrical system.
    """
    pdb_type: str  # "Integrated PDB", "Separate PDB", "4-in-1 ESC bus"
    has_discrete_bec: bool
    bec_capacity_5v_a: float
    bec_capacity_12v_a: float
    avionics_power_w: float
    payload_power_w: float
    total_auxiliary_power_w: float
    bec_margin_5v_pct: float
    bec_margin_12v_pct: float


class PowerDistributionSizer:
    """
    Budgets and sizes Power Distribution Boards (PDBs) and BEC regulators.
    """
    @staticmethod
    def size_power_distribution(payload_weight_kg: float, arm_count: int, esc_has_bec: bool) -> PowerDistributionBudget:
        """
        Sizes regulators, BECs, and budgets power based on payload and motor count.
        """
        # 1. Avionics consumption budgets
        # FC: 5V/2.0A (10W), GPS: 5V/0.5A (2.5W), Telemetry: 5V/1.0A (5W)
        i_fc_5v = 2.0
        i_gps_5v = 0.5
        i_telemetry_5v = 1.0
        total_5v_current_required = i_fc_5v + i_gps_5v + i_telemetry_5v  # 3.5 A
        
        # 2. Sized payload consumption
        # Payload power scales with weight (nominal 15W per kg at 12V)
        payload_power = max(5.0, 15.0 * payload_weight_kg)
        total_12v_current_required = payload_power / 12.0

        # 3. Select PDB type and BEC capacities
        # If using 4-in-1 ESC (common on small quads <= 4 arms)
        if arm_count <= 4 and payload_weight_kg <= 1.0:
            pdb_type = "4-in-1 ESC bus"
            has_discrete_bec = not esc_has_bec
            bec_5v = 5.0 if has_discrete_bec else 3.0
            bec_12v = 0.0
        else:
            # Sized multirotors use separate PDB or heavy power distribution modules
            pdb_type = "Separate PDB"
            has_discrete_bec = True
            bec_5v = 5.0  # Dual BEC capability
            bec_12v = max(2.0, math_ceil(total_12v_current_required + 1.0))

        # 4. Calculate safety margins
        margin_5v = ((bec_5v - total_5v_current_required) / bec_5v) * 100.0
        margin_12v = ((bec_12v - total_12v_current_required) / bec_12v) * 100.0 if bec_12v > 0 else 0.0
        
        total_aux = (total_5v_current_required * 5.0) + payload_power

        return PowerDistributionBudget(
            pdb_type=pdb_type,
            has_discrete_bec=has_discrete_bec,
            bec_capacity_5v_a=bec_5v,
            bec_capacity_12v_a=bec_12v,
            avionics_power_w=total_5v_current_required * 5.0,
            payload_power_w=payload_power,
            total_auxiliary_power_w=total_aux,
            bec_margin_5v_pct=max(0.0, margin_5v),
            bec_margin_12v_pct=max(0.0, margin_12v)
        )

def math_ceil(x: float) -> float:
    """Helper integer ceiling."""
    return float(int(x) + (1 if x > int(x) else 0))
