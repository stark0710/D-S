"""
FamilyEligibilityAnalyzer Subsystem

Purpose:
    Defines the `FamilyEligibilityAnalyzer` class responsible for checking mandatory constraint eligibility
    for each of the 3 aircraft families (MULTIROTOR, FIXED_WING, VTOL) prior to scoring.
"""

from typing import Dict, List, Tuple
from backend.design.common.mission.mission_profile import MissionProfile
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.advisor.recommendation.vehicle_family import VehicleFamily


class FamilyEligibilityAnalyzer:
    """
    Analyzer evaluating hard mandatory constraint eligibility for aircraft families.
    """

    def analyze_eligibility(
        self, profile: MissionProfile, hover_required: bool = False
    ) -> Tuple[List[VehicleFamily], Dict[VehicleFamily, str]]:
        """
        Determines eligible and eliminated families based on mandatory constraints.

        Args:
            profile (MissionProfile): Target engineering mission profile.
            hover_required (bool): Flag indicating mandatory sustained hover requirement.

        Returns:
            Tuple[List[VehicleFamily], Dict[VehicleFamily, str]]: Eligible family list and eliminated family map.
        """
        eligible: list[VehicleFamily] = []
        eliminated: dict[VehicleFamily, str] = {}

        to_type = profile.takeoff_requirement
        ld_type = profile.landing_requirement
        env = profile.environment

        # 1. FIXED_WING Eligibility
        fixed_wing_eliminated = False
        if env == OperatingEnvironment.INDOOR:
            eliminated[VehicleFamily.FIXED_WING] = (
                "Indoor operating environment prohibits wing-borne forward cruise flight."
            )
            fixed_wing_eliminated = True
        elif to_type == TakeoffType.VERTICAL or ld_type == LandingType.VERTICAL or hover_required:
            eliminated[VehicleFamily.FIXED_WING] = (
                "Conventional fixed-wing aircraft cannot perform vertical takeoff, vertical landing, or sustained hover."
            )
            fixed_wing_eliminated = True
        elif to_type == TakeoffType.RUNWAY and env == OperatingEnvironment.URBAN:
            eliminated[VehicleFamily.FIXED_WING] = (
                "Runway-dependent fixed-wing launch is prohibited in confined urban operating environment."
            )
            fixed_wing_eliminated = True

        if not fixed_wing_eliminated:
            eligible.append(VehicleFamily.FIXED_WING)

        # 2. MULTIROTOR Eligibility
        multirotor_eliminated = False
        if to_type not in (TakeoffType.VERTICAL,) and not hover_required and profile.range_requirement > 100.0 and env != OperatingEnvironment.INDOOR:
            eliminated[VehicleFamily.MULTIROTOR] = (
                "Multirotor aerodynamic drag severely limits operational range beyond 100 km."
            )
            multirotor_eliminated = True

        if not multirotor_eliminated:
            eligible.append(VehicleFamily.MULTIROTOR)

        # 3. VTOL Eligibility
        vtol_eliminated = False
        if env == OperatingEnvironment.INDOOR:
            eliminated[VehicleFamily.VTOL] = (
                "Indoor operating environment prohibits wing-borne forward cruise flight."
            )
            vtol_eliminated = True
        elif to_type not in (TakeoffType.VERTICAL,) and profile.range_requirement < 10.0:
            eliminated[VehicleFamily.VTOL] = (
                "Hybrid VTOL hardware complexity is unnecessary for non-vertical short-range missions."
            )
            vtol_eliminated = True

        if not vtol_eliminated:
            eligible.append(VehicleFamily.VTOL)

        return eligible, eliminated
