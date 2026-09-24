from backend.design.multirotor.esc.esc_models import EscCandidate, EscContext

class EscPerformance:
    """
    Calculates operational, electrical, and thermal metrics for multirotor ESCs.
    """
    @staticmethod
    def calculate_performance(candidate: EscCandidate, context: EscContext) -> None:
        """
        Calculates power losses, current margins, efficiencies, and thermal margins.
        """
        motor_spec = context.motor_spec
        esc = candidate.esc_record
        
        # 1. Load current draws from motor sizing outputs
        candidate.hover_current_a = motor_spec.hover_current_a
        candidate.max_current_a = motor_spec.max_current_a

        # 2. Sized internal resistance power losses: P = I^2 * R
        # Typical modern MOS-FET internal resistance is around 1.5 milliohms
        r_internal = 0.0015  # ohms
        candidate.hover_power_loss_w = (candidate.hover_current_a ** 2) * r_internal
        candidate.max_power_loss_w = (candidate.max_current_a ** 2) * r_internal

        # 3. Sized ESC Efficiency
        # Efficiency is extremely high (~98%) but scales down with load
        load_fraction = candidate.hover_current_a / esc.continuous_current_a
        candidate.esc_efficiency = 0.985 - 0.015 * load_fraction

        # 4. Sized Current Margin (continuous safety buffer)
        candidate.current_margin_a = esc.continuous_current_a - candidate.hover_current_a

        # 5. Sized Thermal margin (transient safety headroom)
        max_load = candidate.max_current_a / esc.continuous_current_a
        candidate.thermal_margin_pct = max(0.0, (1.0 - max_load) * 100.0)
