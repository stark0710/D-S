"""
Unit Tests for Construction Configuration Selection Engine (C1 through C6).
"""
import pytest
from unittest.mock import MagicMock
from backend.design.fixed_wing.construction.construction_types import (
    ConstructionConfigurationId,
    ConstructionCatalog,
    StiffnessLevel,
    ManufacturingComplexity,
)
from backend.design.fixed_wing.construction.construction_engine import (
    ConstructionConfigurationSelectionEngine,
    ConstructionSelectionResult,
)


class TestConstructionSelection:
    @pytest.fixture
    def engine(self):
        return ConstructionConfigurationSelectionEngine()

    def test_catalog_all_six_configurations_exist(self):
        """Verify C1 to C6 configurations exist with valid specifications in catalog."""
        cfgs = ConstructionCatalog.get_all()
        assert len(cfgs) == 6
        expected_ids = {
            ConstructionConfigurationId.C1_FOAM_CORE_COMPOSITE,
            ConstructionConfigurationId.C2_BALSA_SKELETON_COMPOSITE,
            ConstructionConfigurationId.C3_BALSA_CARBON_SKELETON_FILM,
            ConstructionConfigurationId.C4_FOAM_DEPRON_FILM,
            ConstructionConfigurationId.C5_FOLDED_FOAM_MONOCOQUE,
            ConstructionConfigurationId.C6_WOOD_SKELETON_FILM,
        }
        actual_ids = {c.configuration_id for c in cfgs}
        assert actual_ids == expected_ids

    def test_advisor_selects_c1_for_demanding_survey_uav(self, engine):
        """Engineering Advisor should select C1 (FOAM_CORE_COMPOSITE) for professional survey UAV."""
        reqs = MagicMock()
        reqs.payload_weight_kg = 2.0
        reqs.target_range_km = 60.0
        reqs.target_flight_time_min = 60.0
        reqs.cruise_speed_kmh = 85.0
        reqs.mission_type = "SURVEY"

        wing_geom = MagicMock()
        wing_geom.span_m = 2.5

        res = engine.select_configuration(reqs, wing_geometry=wing_geom)
        assert isinstance(res, ConstructionSelectionResult)
        assert res.selected_configuration.configuration_id in (
            ConstructionConfigurationId.C1_FOAM_CORE_COMPOSITE,
            ConstructionConfigurationId.C2_BALSA_SKELETON_COMPOSITE,
        )
        assert res.selected_configuration.configuration_id == ConstructionConfigurationId.C1_FOAM_CORE_COMPOSITE
        assert res.mode == "ENGINEERING_ADVISOR"
        assert len(res.ranked_configurations) + len(res.rejected_configurations) == 6

    def test_advisor_selects_c4_or_c5_for_educational_low_payload(self, engine):
        """Engineering Advisor should select C4 or C5 for educational / hobby low-cost missions."""
        reqs = MagicMock()
        reqs.payload_weight_kg = 0.15
        reqs.target_range_km = 5.0
        reqs.target_flight_time_min = 15.0
        reqs.cruise_speed_kmh = 45.0
        reqs.mission_type = "EDUCATIONAL"

        wing_geom = MagicMock()
        wing_geom.span_m = 1.0

        res = engine.select_configuration(reqs, wing_geometry=wing_geom)
        assert res.selected_configuration.configuration_id in (
            ConstructionConfigurationId.C4_FOAM_DEPRON_FILM,
            ConstructionConfigurationId.C5_FOLDED_FOAM_MONOCOQUE,
            ConstructionConfigurationId.C3_BALSA_CARBON_SKELETON_FILM,
        )

    def test_advisor_selects_c3_for_lightweight_short_range(self, engine):
        """Engineering Advisor should favor C3 for ultra-lightweight surveillance."""
        reqs = MagicMock()
        reqs.payload_weight_kg = 0.20
        reqs.target_range_km = 8.0
        reqs.target_flight_time_min = 20.0
        reqs.cruise_speed_kmh = 50.0
        reqs.mission_type = "SURVEILLANCE"

        wing_geom = MagicMock()
        wing_geom.span_m = 1.2

        res = engine.select_configuration(reqs, wing_geometry=wing_geom)
        assert res.selected_configuration.configuration_id in (
            ConstructionConfigurationId.C3_BALSA_CARBON_SKELETON_FILM,
            ConstructionConfigurationId.C4_FOAM_DEPRON_FILM,
        )

    def test_manual_mode_override(self, engine):
        """Manual mode must unconditionally honor user selection without silent replacement."""
        reqs = MagicMock()
        reqs.payload_weight_kg = 1.5
        reqs.cruise_speed_kmh = 75.0

        # User explicitly chooses C6_WOOD_SKELETON_FILM
        res = engine.select_configuration(
            mission_requirements=reqs,
            manual_config_id=ConstructionConfigurationId.C6_WOOD_SKELETON_FILM,
        )
        assert res.selected_configuration.configuration_id == ConstructionConfigurationId.C6_WOOD_SKELETON_FILM
        assert res.mode == "MANUAL"

        # User explicitly chooses C5_FOLDED_FOAM_MONOCOQUE
        res_c5 = engine.select_configuration(
            mission_requirements=reqs,
            manual_config_id="FOLDED_FOAM_MONOCOQUE",
        )
        assert res_c5.selected_configuration.configuration_id == ConstructionConfigurationId.C5_FOLDED_FOAM_MONOCOQUE
        assert res_c5.mode == "MANUAL"
