"""
Fixed-Wing Propulsion Candidate Generator

Populates the Universal Component Repository with motors, propellers,
ESCs, and batteries, and generates compatible candidates.
"""

from typing import List
from backend.design.components.component_repository import ComponentRepository
from backend.design.components.component_category import ComponentCategory
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


def build_component_repository() -> ComponentRepository:
    """Populates and returns the shared component database repository."""
    repo = ComponentRepository()

    # 1. Motors (from MotorSelector catalog)
    motors = [
        {"name": "SunnySky X2216", "kv": 1100.0, "weight_g": 72.0, "max_power_w": 380.0, "nominal_voltage_v": 11.1, "max_current_a": 35.0, "cell_count_s": 3},
        {"name": "SunnySky X2820", "kv": 800.0, "weight_g": 140.0, "max_power_w": 600.0, "nominal_voltage_v": 14.8, "max_current_a": 45.0, "cell_count_s": 4},
        {"name": "T-Motor AT3520", "kv": 560.0, "weight_g": 210.0, "max_power_w": 950.0, "nominal_voltage_v": 22.2, "max_current_a": 50.0, "cell_count_s": 6},
        {"name": "T-Motor AT4120", "kv": 400.0, "weight_g": 310.0, "max_power_w": 1400.0, "nominal_voltage_v": 22.2, "max_current_a": 65.0, "cell_count_s": 6},
        {"name": "T-Motor MN5008", "kv": 340.0, "weight_g": 140.0, "max_power_w": 700.0, "nominal_voltage_v": 22.2, "max_current_a": 35.0, "cell_count_s": 6},
        {"name": "T-Motor U8 Lite", "kv": 190.0, "weight_g": 240.0, "max_power_w": 1000.0, "nominal_voltage_v": 44.4, "max_current_a": 25.0, "cell_count_s": 12},
        {"name": "KDE Direct 7215XF", "kv": 135.0, "weight_g": 620.0, "max_power_w": 3400.0, "nominal_voltage_v": 44.4, "max_current_a": 75.0, "cell_count_s": 12},
    ]
    for m in motors:
        repo.register_component(ComponentCategory.MOTOR, m)

    # 2. Propellers (from PropellerSelector catalog)
    props = [
        {"name": "9x6 APC", "diameter_in": 9.0, "pitch_in": 6.0, "diameter_m": 9.0 * 0.0254, "pitch_m": 6.0 * 0.0254},
        {"name": "10x7 APC", "diameter_in": 10.0, "pitch_in": 7.0, "diameter_m": 10.0 * 0.0254, "pitch_m": 7.0 * 0.0254},
        {"name": "11x7 APC", "diameter_in": 11.0, "pitch_in": 7.0, "diameter_m": 11.0 * 0.0254, "pitch_m": 7.0 * 0.0254},
        {"name": "12x6 APC", "diameter_in": 12.0, "pitch_in": 6.0, "diameter_m": 12.0 * 0.0254, "pitch_m": 6.0 * 0.0254},
        {"name": "12x8 APC", "diameter_in": 12.0, "pitch_in": 8.0, "diameter_m": 12.0 * 0.0254, "pitch_m": 8.0 * 0.0254},
        {"name": "13x8 APC", "diameter_in": 13.0, "pitch_in": 8.0, "diameter_m": 13.0 * 0.0254, "pitch_m": 8.0 * 0.0254},
        {"name": "14x10 APC", "diameter_in": 14.0, "pitch_in": 10.0, "diameter_m": 14.0 * 0.0254, "pitch_m": 10.0 * 0.0254},
        {"name": "15x10 APC", "diameter_in": 15.0, "pitch_in": 10.0, "diameter_m": 15.0 * 0.0254, "pitch_m": 10.0 * 0.0254},
        {"name": "16x8 APC", "diameter_in": 16.0, "pitch_in": 8.0, "diameter_m": 16.0 * 0.0254, "pitch_m": 8.0 * 0.0254},
        {"name": "18x10 APC", "diameter_in": 18.0, "pitch_in": 10.0, "diameter_m": 18.0 * 0.0254, "pitch_m": 10.0 * 0.0254},
        {"name": "20x10 APC", "diameter_in": 20.0, "pitch_in": 10.0, "diameter_m": 20.0 * 0.0254, "pitch_m": 10.0 * 0.0254},
        {"name": "22x12 APC", "diameter_in": 22.0, "pitch_in": 12.0, "diameter_m": 22.0 * 0.0254, "pitch_m": 12.0 * 0.0254},
    ]
    for p in props:
        repo.register_component(ComponentCategory.PROPELLER, p)

    # 3. ESCs
    escs = [
        {"name": "30A BLHeli_32", "continuous_current_a": 30.0, "max_supported_cells_s": 6, "weight_g": 14.0},
        {"name": "35A BLHeli_32", "continuous_current_a": 35.0, "max_supported_cells_s": 6, "weight_g": 18.0},
        {"name": "50A BLHeli_32", "continuous_current_a": 50.0, "max_supported_cells_s": 8, "weight_g": 28.0},
        {"name": "80A BLHeli_32", "continuous_current_a": 80.0, "max_supported_cells_s": 12, "weight_g": 45.0},
        {"name": "120A BLHeli_32", "continuous_current_a": 120.0, "max_supported_cells_s": 14, "weight_g": 65.0},
        {"name": "150A BLHeli_32", "continuous_current_a": 150.0, "max_supported_cells_s": 14, "weight_g": 85.0},
    ]
    for e in escs:
        repo.register_component(ComponentCategory.ESC, e)

    # 4. Batteries
    chemistries = [
        {"chemistry": "LiPo", "cell_nom": 3.7, "c_rate": 45.0, "wh_per_kg": 160.0},
        {"chemistry": "LiHV", "cell_nom": 3.8, "c_rate": 40.0, "wh_per_kg": 185.0},
        {"chemistry": "Li-Ion", "cell_nom": 3.6, "c_rate": 15.0, "wh_per_kg": 240.0},
    ]
    cell_counts = [3, 4, 6, 12]
    capacities = [2200.0, 3300.0, 5000.0, 8000.0, 10000.0, 16000.0]

    for chem in chemistries:
        for s in cell_counts:
            for cap in capacities:
                cell_nom = chem["cell_nom"]
                nominal_v = s * cell_nom
                wh = (cap / 1000.0) * nominal_v
                weight_g = round(wh / (chem["wh_per_kg"] / 1000.0), 1)
                name = f"{chem['chemistry']} {s}S {int(cap)}mAh {int(chem['c_rate'])}C Pack"
                b = {
                    "name": name,
                    "chemistry": chem["chemistry"],
                    "cell_count_s": s,
                    "nominal_voltage_v": round(nominal_v, 2),
                    "capacity_mah": cap,
                    "discharge_rating_c": chem["c_rate"],
                    "total_energy_wh": round(wh, 1),
                    "weight_g": weight_g,
                    "max_discharge_current_a": round((cap / 1000.0) * chem["c_rate"], 2),
                }
                repo.register_component(ComponentCategory.BATTERY, b)

    return repo


class GridSearchPropulsionCandidateGenerator:
    """Generates feasible and pre-filtered propulsion candidates."""

    def __init__(self, repository: ComponentRepository | None = None) -> None:
        self.repository = repository if repository else build_component_repository()

    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        """Generates all electrically and mechanically pre-filtered candidates."""
        motors = self.repository.get_components_by_category(ComponentCategory.MOTOR)
        props = self.repository.get_components_by_category(ComponentCategory.PROPELLER)
        escs = self.repository.get_components_by_category(ComponentCategory.ESC)
        batteries = self.repository.get_components_by_category(ComponentCategory.BATTERY)

        candidates = []
        for motor in motors:
            for propeller in props:
                # Prune propeller sizes to match motor torque capabilities
                m_name = motor["name"]
                dia_in = propeller["diameter_in"]
                if "X2216" in m_name and not (8.0 <= dia_in <= 11.0):
                    continue
                if "X2820" in m_name and not (10.0 <= dia_in <= 13.0):
                    continue
                if "AT3520" in m_name and not (11.0 <= dia_in <= 14.0):
                    continue
                if "AT4120" in m_name and not (12.0 <= dia_in <= 15.0):
                    continue
                if "MN5008" in m_name and not (14.0 <= dia_in <= 18.0):
                    continue
                if "U8 Lite" in m_name and not (16.0 <= dia_in <= 20.0):
                    continue
                if "7215XF" in m_name and not (18.0 <= dia_in <= 22.0):
                    continue

                for esc in escs:
                    # Filter ESC compatibility: rating >= motor max current
                    if esc["continuous_current_a"] < motor["max_current_a"]:
                        continue
                    # Prune over-rated ESCs to prevent excess weight
                    if esc["continuous_current_a"] > motor["max_current_a"] + 30.0:
                        continue
                    # Filter ESC cell count support
                    if esc["max_supported_cells_s"] < motor["cell_count_s"]:
                        continue

                    for battery in batteries:
                        # Voltage/Cell compatibility: cell count must match motor's designed count
                        if battery["cell_count_s"] != motor["cell_count_s"]:
                            continue

                        # Prune battery capacity based on motor/voltage scale
                        s_count = battery["cell_count_s"]
                        cap_mah = battery["capacity_mah"]
                        if s_count <= 4 and cap_mah > 6000.0:
                            continue
                        if s_count == 6 and not (3000.0 <= cap_mah <= 12000.0):
                            continue
                        if s_count == 12 and cap_mah < 5000.0:
                            continue

                        # Electrically compatible design candidate
                        design_variables = {
                            "motor": motor,
                            "motor_name": motor["name"],
                            "propeller": propeller,
                            "propeller_name": propeller["name"],
                            "esc": esc,
                            "esc_name": esc["name"],
                            "battery": battery,
                            "battery_name": battery["name"],
                            "cell_count_s": battery["cell_count_s"],
                            "nominal_voltage_v": battery["nominal_voltage_v"],
                            "battery_capacity_mah": battery["capacity_mah"],
                        }
                        candidates.append(OptimizationCandidate(design_variables=design_variables))

        return candidates
