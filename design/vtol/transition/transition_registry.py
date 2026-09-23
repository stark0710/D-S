from typing import Dict, Type
from backend.design.vtol.mission.mission_requirements import VTOLType
from .transition_strategy import (
    TransitionStrategy, LiftCruiseTransitionStrategy, QuadPlaneTransitionStrategy,
    TiltRotorTransitionStrategy, TiltWingTransitionStrategy, TailSitterTransitionStrategy,
    VectoredThrustTransitionStrategy, BalancedTransitionStrategy
)

class TransitionRegistry:
    """
    Registry mapping aircraft configuration types to conversion strategies.
    """
    _registry: Dict[VTOLType, Type[TransitionStrategy]] = {
        VTOLType.LIFT_CRUISE: LiftCruiseTransitionStrategy,
        VTOLType.QUADPLANE: QuadPlaneTransitionStrategy,
        VTOLType.TILT_ROTOR: TiltRotorTransitionStrategy,
        VTOLType.TILT_WING: TiltWingTransitionStrategy,
        VTOLType.TAIL_SITTER: TailSitterTransitionStrategy,
        VTOLType.VECTORED_THRUST: VectoredThrustTransitionStrategy,
        VTOLType.HYBRID_VTOL: BalancedTransitionStrategy,
        VTOLType.TWIN_BOOM_VTOL: BalancedTransitionStrategy,
        VTOLType.BOX_WING_VTOL: BalancedTransitionStrategy,
        VTOLType.CUSTOM: BalancedTransitionStrategy
    }

    @classmethod
    def get_strategy(cls, vtol_type: VTOLType) -> TransitionStrategy:
        strategy_class = cls._registry.get(vtol_type, BalancedTransitionStrategy)
        return strategy_class()
