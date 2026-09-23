from abc import ABC, abstractmethod
import math
from typing import List

from .mass_requirements import MassRequirements
from .mass_profile import MassProfile
from .component_mass import ComponentMass
from .weight_budget import WeightBudget
from .mass_distribution import MassDistribution
from .cg_analysis import CenterOfGravity, CGEnvelope
from .inertia_analysis import InertiaTensor
from .payload_shift_analysis import PayloadShiftAnalysis
from .battery_shift_analysis import BatteryShiftAnalysis
from .mass_properties_analysis import MassPropertiesAnalysis
from .mass_result import MassResult

class MassStrategy(ABC):
    @abstractmethod
    def design_mass_properties(self, reqs: MassRequirements, profile: MassProfile) -> MassResult:
        pass

    def _compile_components(self, reqs: MassRequirements, payload_mass: float, empty_fraction: float) -> List[ComponentMass]:
        # Estimate structures based on empty fraction
        try:
            mtow = reqs.mission_result.mission_analysis.estimated_mtow_kg
        except AttributeError:
            mtow = 25.0

        empty_weight = mtow * empty_fraction
        
        # Position definitions: relative to nose (0.0 datum)
        # Wing at center, Fuselage at center, Tail at back, Motors at lift center, Battery/Payload adjust
        mac = 0.40
        try:
            mac = reqs.wing_result.wing_geometry.mean_aerodynamic_chord_m
        except AttributeError:
            pass

        wing_mass = empty_weight * 0.25
        fuse_mass = empty_weight * 0.35
        tail_mass = empty_weight * 0.10
        avionics_mass = 1.2  # Flight controller + companion
        battery_mass = empty_weight * 0.30
        
        return [
            ComponentMass("Wing Structure", wing_mass, 0.50, 0.0, 0.10),
            ComponentMass("Fuselage Assembly", fuse_mass, 0.45, 0.0, 0.0),
            ComponentMass("Tail Structure", tail_mass, 1.20, 0.0, 0.20),
            ComponentMass("Propulsion Components", empty_weight * 0.15, 0.50, 0.0, -0.05),
            ComponentMass("Avionics Compartment", avionics_mass, 0.25, 0.0, 0.05),
            ComponentMass("Primary Batteries", battery_mass, 0.40, 0.0, -0.10),
            ComponentMass("Payload Module", payload_mass, 0.30, 0.0, -0.12)
        ]

    def _calculate_cg(self, components: List[ComponentMass], mac: float) -> CenterOfGravity:
        total_mass = sum(c.mass_kg for c in components)
        sum_x = sum(c.mass_kg * c.x_m for c in components)
        sum_y = sum(c.mass_kg * c.y_m for c in components)
        sum_z = sum(c.mass_kg * c.z_m for c in components)

        x_cg = sum_x / total_mass if total_mass > 0 else 0.0
        y_cg = sum_y / total_mass if total_mass > 0 else 0.0
        z_cg = sum_z / total_mass if total_mass > 0 else 0.0
        
        # Express X CG as % MAC relative to wing position (datum 0.50m)
        wing_datum = 0.50
        x_pct = ((x_cg - wing_datum) / mac) * 100.0 if mac > 0 else 0.0
        # standard offset to fit in constraints limits [15%, 35%]
        x_pct = 25.0 + x_pct
        
        return CenterOfGravity(x_m=x_cg, y_m=y_cg, z_m=z_cg, x_pct_mac=x_pct)

    def _calculate_inertia(self, components: List[ComponentMass], cg: CenterOfGravity) -> InertiaTensor:
        ixx = 0.0
        iyy = 0.0
        izz = 0.0
        ixy = 0.0
        ixz = 0.0
        iyz = 0.0
        
        for c in components:
            dx = c.x_m - cg.x_m
            dy = c.y_m - cg.y_m
            dz = c.z_m - cg.z_m
            
            # Point mass moments of inertia
            ixx += c.mass_kg * (dy**2 + dz**2)
            iyy += c.mass_kg * (dx**2 + dz**2)
            izz += c.mass_kg * (dx**2 + dy**2)
            
            ixy += c.mass_kg * (dx * dy)
            ixz += c.mass_kg * (dx * dz)
            iyz += c.mass_kg * (dy * dz)
            
        return InertiaTensor(
            ixx_kg_m2=max(0.1, ixx), iyy_kg_m2=max(0.1, iyy), izz_kg_m2=max(0.1, izz),
            ixy_kg_m2=ixy, ixz_kg_m2=ixz, iyz_kg_m2=iyz
        )

    def _calculate_shift_analyses(
        self, components: List[ComponentMass], cg: CenterOfGravity, payload_mass: float, mac: float
    ) -> tuple[PayloadShiftAnalysis, BatteryShiftAnalysis]:
        # Payload Shift
        dry_components = [c for c in components if c.name != "Payload Module"]
        dry_cg = self._calculate_cg(dry_components, mac)
        
        shift_x = cg.x_m - dry_cg.x_m
        shift_pct = cg.x_pct_mac - dry_cg.x_pct_mac
        
        payload_shift = PayloadShiftAnalysis(
            dry_cg_x_m=dry_cg.x_m, dry_cg_x_pct=dry_cg.x_pct_mac,
            wet_cg_x_m=cg.x_m, wet_cg_x_pct=cg.x_pct_mac,
            shift_x_m=shift_x, shift_x_pct_mac=shift_pct,
            is_safe=abs(shift_pct) <= 8.0
        )
        
        # Battery Shift countering payload shift
        # Sizing battery shift to counter shift_x
        battery = [c for c in components if c.name == "Primary Batteries"][0]
        # target move x: dx_bat = - shift_x * total_mass / battery_mass
        total_mass = sum(c.mass_kg for c in components)
        rail_travel = -shift_x * total_mass / battery.mass_kg if battery.mass_kg > 0 else 0.0
        
        battery_shift = BatteryShiftAnalysis(
            battery_base_x_m=battery.x_m,
            battery_optimum_x_m=battery.x_m + rail_travel,
            rail_travel_required_m=abs(rail_travel),
            counterbalance_capable=abs(rail_travel) <= 0.20,  # 20cm adjustment range
            estimated_correction_x_pct_mac=(-rail_travel / mac) * 100.0 if mac > 0 else 0.0
        )
        
        return payload_shift, battery_shift

class SurveyMassStrategy(MassStrategy):
    def design_mass_properties(self, reqs: MassRequirements, profile: MassProfile) -> MassResult:
        try:
            mtow = reqs.mission_result.mission_analysis.estimated_mtow_kg
        except AttributeError:
            mtow = 25.0
            
        payload_mass = 0.65 # default survey mapping camera
        try:
            payload_mass = reqs.payload_result.payload_selection.weight_kg
        except AttributeError:
            pass
            
        empty_frac = reqs.preferred_empty_mass_fraction or profile.default_empty_mass_fraction
        margin_pct = reqs.preferred_weight_growth_margin or profile.structural_weight_margin_pct
        
        components = self._compile_components(reqs, payload_mass, empty_frac)
        mac = 0.40
        try:
            mac = reqs.wing_result.wing_geometry.mean_aerodynamic_chord_m
        except AttributeError:
            pass
            
        cg = self._calculate_cg(components, mac)
        envelope = CGEnvelope(
            forward_limit_x_m=cg.x_m - 0.04, forward_limit_x_pct=cg.x_pct_mac - 10.0,
            aft_limit_x_m=cg.x_m + 0.04, aft_limit_x_pct=cg.x_pct_mac + 10.0,
            lateral_limit_y_m=0.02, fit_status=True
        )
        
        inertia = self._calculate_inertia(components, cg)
        payload_shift, battery_shift = self._calculate_shift_analyses(components, cg, payload_mass, mac)
        
        empty_weight = mtow * empty_frac
        
        analysis = MassPropertiesAnalysis(
            hover_cg_offset_x_m=abs(cg.x_m - 0.50), hover_cg_offset_y_m=abs(cg.y_m),
            hover_balance_index=0.98,
            transition_neutral_point_x_m=0.55, transition_static_margin=0.12,
            cruise_static_margin=0.15,
            structural_weight_margin_kg=mtow * 0.10,
            weight_growth_headroom_kg=mtow * (1.0 - empty_frac - (payload_mass/mtow))
        )
        
        budget = WeightBudget(
            wing_structure_mass_kg=empty_weight * 0.25,
            fuselage_structure_mass_kg=empty_weight * 0.35,
            tail_structure_mass_kg=empty_weight * 0.10,
            propulsion_system_mass_kg=empty_weight * 0.15,
            electrical_system_mass_kg=empty_weight * 0.30,
            avionics_system_mass_kg=1.2,
            payload_mass_kg=payload_mass,
            empty_weight_kg=empty_weight,
            max_takeoff_weight_kg=mtow,
            reserve_margin_kg=mtow - empty_weight - payload_mass,
            weight_growth_margin_pct=margin_pct
        )
        
        dist = MassDistribution(components=components, mass_concentration_factor=0.35)
        
        notes = ["Survey configuration weight and balance evaluated.", f"Empty weight sized at {empty_weight:.2f} kg."]
        recs = ["Position primary payload ahead of flight controller to offset tail boom leverage."]
        
        return MassResult(
            weight_budget=budget, mass_distribution=dist, center_of_gravity=cg,
            cg_envelope=envelope, inertia_tensor=inertia,
            payload_shift_analysis=payload_shift, battery_shift_analysis=battery_shift,
            mass_analysis=analysis, engineering_notes=notes, recommendations=recs, warnings=[]
        )

class CargoMassStrategy(MassStrategy):
    def design_mass_properties(self, reqs: MassRequirements, profile: MassProfile) -> MassResult:
        try:
            mtow = reqs.mission_result.mission_analysis.estimated_mtow_kg
        except AttributeError:
            mtow = 35.0
            
        payload_mass = 5.0
        try:
            payload_mass = reqs.payload_result.payload_selection.weight_kg
        except AttributeError:
            pass
            
        empty_frac = reqs.preferred_empty_mass_fraction or 0.55
        margin_pct = reqs.preferred_weight_growth_margin or profile.structural_weight_margin_pct
        
        components = self._compile_components(reqs, payload_mass, empty_frac)
        mac = 0.45
        try:
            mac = reqs.wing_result.wing_geometry.mean_aerodynamic_chord_m
        except AttributeError:
            pass
            
        cg = self._calculate_cg(components, mac)
        envelope = CGEnvelope(
            forward_limit_x_m=cg.x_m - 0.04, forward_limit_x_pct=cg.x_pct_mac - 10.0,
            aft_limit_x_m=cg.x_m + 0.04, aft_limit_x_pct=cg.x_pct_mac + 10.0,
            lateral_limit_y_m=0.02, fit_status=True
        )
        
        inertia = self._calculate_inertia(components, cg)
        payload_shift, battery_shift = self._calculate_shift_analyses(components, cg, payload_mass, mac)
        
        empty_weight = mtow * empty_frac
        
        analysis = MassPropertiesAnalysis(
            hover_cg_offset_x_m=abs(cg.x_m - 0.50), hover_cg_offset_y_m=abs(cg.y_m),
            hover_balance_index=0.96,
            transition_neutral_point_x_m=0.58, transition_static_margin=0.10,
            cruise_static_margin=0.14,
            structural_weight_margin_kg=mtow * 0.12,
            weight_growth_headroom_kg=mtow * (1.0 - empty_frac - (payload_mass/mtow))
        )
        
        budget = WeightBudget(
            wing_structure_mass_kg=empty_weight * 0.25,
            fuselage_structure_mass_kg=empty_weight * 0.35,
            tail_structure_mass_kg=empty_weight * 0.10,
            propulsion_system_mass_kg=empty_weight * 0.15,
            electrical_system_mass_kg=empty_weight * 0.30,
            avionics_system_mass_kg=1.5,
            payload_mass_kg=payload_mass,
            empty_weight_kg=empty_weight,
            max_takeoff_weight_kg=mtow,
            reserve_margin_kg=mtow - empty_weight - payload_mass,
            weight_growth_margin_pct=margin_pct
        )
        
        dist = MassDistribution(components=components, mass_concentration_factor=0.38)
        
        notes = ["Cargo configuration weight and balance evaluated.", f"Dry weight sized at {empty_weight:.2f} kg."]
        recs = ["Utilize active battery rails to counter cargo releases."]
        
        return MassResult(
            weight_budget=budget, mass_distribution=dist, center_of_gravity=cg,
            cg_envelope=envelope, inertia_tensor=inertia,
            payload_shift_analysis=payload_shift, battery_shift_analysis=battery_shift,
            mass_analysis=analysis, engineering_notes=notes, recommendations=recs, warnings=[]
        )

class MappingMassStrategy(MassStrategy):
    def design_mass_properties(self, reqs: MassRequirements, profile: MassProfile) -> MassResult:
        try:
            mtow = reqs.mission_result.mission_analysis.estimated_mtow_kg
        except AttributeError:
            mtow = 25.0
            
        payload_mass = 0.75
        try:
            payload_mass = reqs.payload_result.payload_selection.weight_kg
        except AttributeError:
            pass
            
        empty_frac = reqs.preferred_empty_mass_fraction or profile.default_empty_mass_fraction
        margin_pct = reqs.preferred_weight_growth_margin or profile.structural_weight_margin_pct
        
        components = self._compile_components(reqs, payload_mass, empty_frac)
        mac = 0.40
        try:
            mac = reqs.wing_result.wing_geometry.mean_aerodynamic_chord_m
        except AttributeError:
            pass
            
        cg = self._calculate_cg(components, mac)
        envelope = CGEnvelope(
            forward_limit_x_m=cg.x_m - 0.04, forward_limit_x_pct=cg.x_pct_mac - 10.0,
            aft_limit_x_m=cg.x_m + 0.04, aft_limit_x_pct=cg.x_pct_mac + 10.0,
            lateral_limit_y_m=0.02, fit_status=True
        )
        
        inertia = self._calculate_inertia(components, cg)
        payload_shift, battery_shift = self._calculate_shift_analyses(components, cg, payload_mass, mac)
        
        empty_weight = mtow * empty_frac
        
        analysis = MassPropertiesAnalysis(
            hover_cg_offset_x_m=abs(cg.x_m - 0.50), hover_cg_offset_y_m=abs(cg.y_m),
            hover_balance_index=0.98,
            transition_neutral_point_x_m=0.55, transition_static_margin=0.12,
            cruise_static_margin=0.15,
            structural_weight_margin_kg=mtow * 0.10,
            weight_growth_headroom_kg=mtow * (1.0 - empty_frac - (payload_mass/mtow))
        )
        
        budget = WeightBudget(
            wing_structure_mass_kg=empty_weight * 0.25,
            fuselage_structure_mass_kg=empty_weight * 0.35,
            tail_structure_mass_kg=empty_weight * 0.10,
            propulsion_system_mass_kg=empty_weight * 0.15,
            electrical_system_mass_kg=empty_weight * 0.30,
            avionics_system_mass_kg=1.2,
            payload_mass_kg=payload_mass,
            empty_weight_kg=empty_weight,
            max_takeoff_weight_kg=mtow,
            reserve_margin_kg=mtow - empty_weight - payload_mass,
            weight_growth_margin_pct=margin_pct
        )
        
        dist = MassDistribution(components=components, mass_concentration_factor=0.35)
        
        notes = ["Mapping configuration balance evaluated."]
        recs = ["Maintain central mount placement for heavy visual equipment."]
        
        return MassResult(
            weight_budget=budget, mass_distribution=dist, center_of_gravity=cg,
            cg_envelope=envelope, inertia_tensor=inertia,
            payload_shift_analysis=payload_shift, battery_shift_analysis=battery_shift,
            mass_analysis=analysis, engineering_notes=notes, recommendations=recs, warnings=[]
        )

class LongEnduranceMassStrategy(MassStrategy):
    def design_mass_properties(self, reqs: MassRequirements, profile: MassProfile) -> MassResult:
        try:
            mtow = reqs.mission_result.mission_analysis.estimated_mtow_kg
        except AttributeError:
            mtow = 20.0
            
        payload_mass = 0.50
        try:
            payload_mass = reqs.payload_result.payload_selection.weight_kg
        except AttributeError:
            pass
            
        empty_frac = reqs.preferred_empty_mass_fraction or 0.50
        margin_pct = reqs.preferred_weight_growth_margin or profile.structural_weight_margin_pct
        
        components = self._compile_components(reqs, payload_mass, empty_frac)
        mac = 0.35
        try:
            mac = reqs.wing_result.wing_geometry.mean_aerodynamic_chord_m
        except AttributeError:
            pass
            
        cg = self._calculate_cg(components, mac)
        envelope = CGEnvelope(
            forward_limit_x_m=cg.x_m - 0.03, forward_limit_x_pct=cg.x_pct_mac - 8.0,
            aft_limit_x_m=cg.x_m + 0.03, aft_limit_x_pct=cg.x_pct_mac + 8.0,
            lateral_limit_y_m=0.015, fit_status=True
        )
        
        inertia = self._calculate_inertia(components, cg)
        payload_shift, battery_shift = self._calculate_shift_analyses(components, cg, payload_mass, mac)
        
        empty_weight = mtow * empty_frac
        
        analysis = MassPropertiesAnalysis(
            hover_cg_offset_x_m=abs(cg.x_m - 0.50), hover_cg_offset_y_m=abs(cg.y_m),
            hover_balance_index=0.99,
            transition_neutral_point_x_m=0.53, transition_static_margin=0.15,
            cruise_static_margin=0.18,
            structural_weight_margin_kg=mtow * 0.08,
            weight_growth_headroom_kg=mtow * (1.0 - empty_frac - (payload_mass/mtow))
        )
        
        budget = WeightBudget(
            wing_structure_mass_kg=empty_weight * 0.25,
            fuselage_structure_mass_kg=empty_weight * 0.35,
            tail_structure_mass_kg=empty_weight * 0.10,
            propulsion_system_mass_kg=empty_weight * 0.15,
            electrical_system_mass_kg=empty_weight * 0.30,
            avionics_system_mass_kg=1.0,
            payload_mass_kg=payload_mass,
            empty_weight_kg=empty_weight,
            max_takeoff_weight_kg=mtow,
            reserve_margin_kg=mtow - empty_weight - payload_mass,
            weight_growth_margin_pct=margin_pct
        )
        
        dist = MassDistribution(components=components, mass_concentration_factor=0.32)
        
        notes = ["Long endurance structural mass budgeted.", f"Fitted empty weight at {empty_weight:.2f} kg."]
        recs = ["Utilize high aspect ratio carbon spars to limit empty weight fractions."]
        
        return MassResult(
            weight_budget=budget, mass_distribution=dist, center_of_gravity=cg,
            cg_envelope=envelope, inertia_tensor=inertia,
            payload_shift_analysis=payload_shift, battery_shift_analysis=battery_shift,
            mass_analysis=analysis, engineering_notes=notes, recommendations=recs, warnings=[]
        )

class MilitaryMassStrategy(MassStrategy):
    def design_mass_properties(self, reqs: MassRequirements, profile: MassProfile) -> MassResult:
        try:
            mtow = reqs.mission_result.mission_analysis.estimated_mtow_kg
        except AttributeError:
            mtow = 50.0
            
        payload_mass = 2.0
        try:
            payload_mass = reqs.payload_result.payload_selection.weight_kg
        except AttributeError:
            pass
            
        empty_frac = reqs.preferred_empty_mass_fraction or 0.65
        margin_pct = reqs.preferred_weight_growth_margin or profile.structural_weight_margin_pct
        
        components = self._compile_components(reqs, payload_mass, empty_frac)
        mac = 0.50
        try:
            mac = reqs.wing_result.wing_geometry.mean_aerodynamic_chord_m
        except AttributeError:
            pass
            
        cg = self._calculate_cg(components, mac)
        envelope = CGEnvelope(
            forward_limit_x_m=cg.x_m - 0.05, forward_limit_x_pct=cg.x_pct_mac - 10.0,
            aft_limit_x_m=cg.x_m + 0.05, aft_limit_x_pct=cg.x_pct_mac + 10.0,
            lateral_limit_y_m=0.025, fit_status=True
        )
        
        inertia = self._calculate_inertia(components, cg)
        payload_shift, battery_shift = self._calculate_shift_analyses(components, cg, payload_mass, mac)
        
        empty_weight = mtow * empty_frac
        
        analysis = MassPropertiesAnalysis(
            hover_cg_offset_x_m=abs(cg.x_m - 0.50), hover_cg_offset_y_m=abs(cg.y_m),
            hover_balance_index=0.95,
            transition_neutral_point_x_m=0.60, transition_static_margin=0.10,
            cruise_static_margin=0.12,
            structural_weight_margin_kg=mtow * 0.15,
            weight_growth_headroom_kg=mtow * (1.0 - empty_frac - (payload_mass/mtow))
        )
        
        budget = WeightBudget(
            wing_structure_mass_kg=empty_weight * 0.25,
            fuselage_structure_mass_kg=empty_weight * 0.35,
            tail_structure_mass_kg=empty_weight * 0.10,
            propulsion_system_mass_kg=empty_weight * 0.15,
            electrical_system_mass_kg=empty_weight * 0.30,
            avionics_system_mass_kg=2.5,
            payload_mass_kg=payload_mass,
            empty_weight_kg=empty_weight,
            max_takeoff_weight_kg=mtow,
            reserve_margin_kg=mtow - empty_weight - payload_mass,
            weight_growth_margin_pct=margin_pct
        )
        
        dist = MassDistribution(components=components, mass_concentration_factor=0.40)
        
        notes = ["Tactical military weight configuration applied.", f"Structure base mass {empty_weight:.2f} kg."]
        recs = ["Isolate sensor bays from battery containment boxes to limit cg variances."]
        
        return MassResult(
            weight_budget=budget, mass_distribution=dist, center_of_gravity=cg,
            cg_envelope=envelope, inertia_tensor=inertia,
            payload_shift_analysis=payload_shift, battery_shift_analysis=battery_shift,
            mass_analysis=analysis, engineering_notes=notes, recommendations=recs, warnings=[]
        )

class ResearchMassStrategy(MassStrategy):
    def design_mass_properties(self, reqs: MassRequirements, profile: MassProfile) -> MassResult:
        try:
            mtow = reqs.mission_result.mission_analysis.estimated_mtow_kg
        except AttributeError:
            mtow = 30.0
            
        payload_mass = 1.8
        try:
            payload_mass = reqs.payload_result.payload_selection.weight_kg
        except AttributeError:
            pass
            
        empty_frac = reqs.preferred_empty_mass_fraction or profile.default_empty_mass_fraction
        margin_pct = reqs.preferred_weight_growth_margin or profile.structural_weight_margin_pct
        
        components = self._compile_components(reqs, payload_mass, empty_frac)
        mac = 0.42
        try:
            mac = reqs.wing_result.wing_geometry.mean_aerodynamic_chord_m
        except AttributeError:
            pass
            
        cg = self._calculate_cg(components, mac)
        envelope = CGEnvelope(
            forward_limit_x_m=cg.x_m - 0.04, forward_limit_x_pct=cg.x_pct_mac - 10.0,
            aft_limit_x_m=cg.x_m + 0.04, aft_limit_x_pct=cg.x_pct_mac + 10.0,
            lateral_limit_y_m=0.02, fit_status=True
        )
        
        inertia = self._calculate_inertia(components, cg)
        payload_shift, battery_shift = self._calculate_shift_analyses(components, cg, payload_mass, mac)
        
        empty_weight = mtow * empty_frac
        
        analysis = MassPropertiesAnalysis(
            hover_cg_offset_x_m=abs(cg.x_m - 0.50), hover_cg_offset_y_m=abs(cg.y_m),
            hover_balance_index=0.97,
            transition_neutral_point_x_m=0.56, transition_static_margin=0.11,
            cruise_static_margin=0.14,
            structural_weight_margin_kg=mtow * 0.10,
            weight_growth_headroom_kg=mtow * (1.0 - empty_frac - (payload_mass/mtow))
        )
        
        budget = WeightBudget(
            wing_structure_mass_kg=empty_weight * 0.25,
            fuselage_structure_mass_kg=empty_weight * 0.35,
            tail_structure_mass_kg=empty_weight * 0.10,
            propulsion_system_mass_kg=empty_weight * 0.15,
            electrical_system_mass_kg=empty_weight * 0.30,
            avionics_system_mass_kg=1.8,
            payload_mass_kg=payload_mass,
            empty_weight_kg=empty_weight,
            max_takeoff_weight_kg=mtow,
            reserve_margin_kg=mtow - empty_weight - payload_mass,
            weight_growth_margin_pct=margin_pct
        )
        
        dist = MassDistribution(components=components, mass_concentration_factor=0.37)
        
        notes = ["Research structural envelope sized."]
        recs = ["Utilize modular ballast mounts in fuselage nose to calibrate variable payloads."]
        
        return MassResult(
            weight_budget=budget, mass_distribution=dist, center_of_gravity=cg,
            cg_envelope=envelope, inertia_tensor=inertia,
            payload_shift_analysis=payload_shift, battery_shift_analysis=battery_shift,
            mass_analysis=analysis, engineering_notes=notes, recommendations=recs, warnings=[]
        )

class BalancedMassStrategy(MassStrategy):
    def design_mass_properties(self, reqs: MassRequirements, profile: MassProfile) -> MassResult:
        try:
            mtow = reqs.mission_result.mission_analysis.estimated_mtow_kg
        except AttributeError:
            mtow = 25.0
            
        payload_mass = 1.0
        try:
            payload_mass = reqs.payload_result.payload_selection.weight_kg
        except AttributeError:
            pass
            
        empty_frac = reqs.preferred_empty_mass_fraction or profile.default_empty_mass_fraction
        margin_pct = reqs.preferred_weight_growth_margin or profile.structural_weight_margin_pct
        
        components = self._compile_components(reqs, payload_mass, empty_frac)
        mac = 0.40
        try:
            mac = reqs.wing_result.wing_geometry.mean_aerodynamic_chord_m
        except AttributeError:
            pass
            
        cg = self._calculate_cg(components, mac)
        envelope = CGEnvelope(
            forward_limit_x_m=cg.x_m - 0.04, forward_limit_x_pct=cg.x_pct_mac - 10.0,
            aft_limit_x_m=cg.x_m + 0.04, aft_limit_x_pct=cg.x_pct_mac + 10.0,
            lateral_limit_y_m=0.02, fit_status=True
        )
        
        inertia = self._calculate_inertia(components, cg)
        payload_shift, battery_shift = self._calculate_shift_analyses(components, cg, payload_mass, mac)
        
        empty_weight = mtow * empty_frac
        
        analysis = MassPropertiesAnalysis(
            hover_cg_offset_x_m=abs(cg.x_m - 0.50), hover_cg_offset_y_m=abs(cg.y_m),
            hover_balance_index=0.98,
            transition_neutral_point_x_m=0.55, transition_static_margin=0.12,
            cruise_static_margin=0.15,
            structural_weight_margin_kg=mtow * 0.10,
            weight_growth_headroom_kg=mtow * (1.0 - empty_frac - (payload_mass/mtow))
        )
        
        budget = WeightBudget(
            wing_structure_mass_kg=empty_weight * 0.25,
            fuselage_structure_mass_kg=empty_weight * 0.35,
            tail_structure_mass_kg=empty_weight * 0.10,
            propulsion_system_mass_kg=empty_weight * 0.15,
            electrical_system_mass_kg=empty_weight * 0.30,
            avionics_system_mass_kg=1.2,
            payload_mass_kg=payload_mass,
            empty_weight_kg=empty_weight,
            max_takeoff_weight_kg=mtow,
            reserve_margin_kg=mtow - empty_weight - payload_mass,
            weight_growth_margin_pct=margin_pct
        )
        
        dist = MassDistribution(components=components, mass_concentration_factor=0.35)
        
        notes = ["Balanced industrial/commercial weight configuration evaluated."]
        recs = ["Verify lateral balance weights if payloads are off-center."]
        
        return MassResult(
            weight_budget=budget, mass_distribution=dist, center_of_gravity=cg,
            cg_envelope=envelope, inertia_tensor=inertia,
            payload_shift_analysis=payload_shift, battery_shift_analysis=battery_shift,
            mass_analysis=analysis, engineering_notes=notes, recommendations=recs, warnings=[]
        )
