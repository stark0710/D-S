from abc import ABC, abstractmethod
import math
from typing import List

from .manufacturing_requirements import ManufacturingRequirements
from .manufacturing_profile import ManufacturingProfile
from .bom_generator import BOMItem, BillOfMaterials
from .assembly_instruction_generator import AssemblyStep, AssemblyInstructions
from .process_plan_generator import ProcessOperation, ManufacturingProcessPlan
from .tooling_generator import ToolingItem, ToolingPlan
from .fixture_generator import FixtureItem, FixturePlan
from .quality_plan_generator import QualityCheckpoint, QualityPlan
from .inspection_plan_generator import InspectionItem, InspectionPlan
from .cost_estimation import ProductionCostEstimate
from .production_analysis import ManufacturabilityAssessment
from .manufacturing_result import ManufacturingResult

class ManufacturingStrategy(ABC):
    @abstractmethod
    def generate_package(self, reqs: ManufacturingRequirements, profile: ManufacturingProfile) -> ManufacturingResult:
        pass

    def _compile_bom(self) -> BillOfMaterials:
        items = [
            BOMItem("MAIN_SPAR_01", "Carbon fiber wing spar", 2, 450.0, "Carbon Fiber", "Structure"),
            BOMItem("ROTOR_BLADE_04", "Hover lift propeller", 4, 120.0, "Nylon Composite", "Propulsion"),
            BOMItem("LIPO_BATTERY_16S", "16S LiPo Battery pack", 1, 850.0, "Lithium Polymer", "Electrical"),
            BOMItem("BOLT_M4_16", "Socket head cap screw", 24, 0.45, "Stainless Steel 316", "Hardware")
        ]
        total_mat = sum(item.quantity * item.unit_cost_usd for item in items)
        return BillOfMaterials(items=items, total_parts_count=31, total_material_cost_usd=total_mat)

    def _compile_assembly_instructions(self) -> AssemblyInstructions:
        steps = [
            AssemblyStep(1, "Composite Layup", "Apply carbon fiber composite layers into wing molds.", 120.0, ["Wing Mold Jig", "Vacuum Bag"]),
            AssemblyStep(2, "Motor Positioning", "Align hover motors using fixture templates.", 45.0, ["Motor Alignment Cradle"]),
            AssemblyStep(3, "Wire Routing", "Pull electrical cabling loops through routing paths.", 60.0, ["Harness Guide Puller"])
        ]
        total_hours = sum(step.estimated_time_min for step in steps) / 60.0
        return AssemblyInstructions(steps=steps, estimated_assembly_time_hours=total_hours)

    def _compile_fixture_plan(self) -> FixturePlan:
        fixtures = [
            FixtureItem("FIX_WING_01", "Structural wing assembly frame", [100.0, 50.0, 0.0], 1200.0),
            FixtureItem("FIX_MOTOR_TILT", "Motor tilt alignment coordinate index", [0.0, 0.0, 0.0], 850.0)
        ]
        return FixturePlan(fixtures=fixtures, total_fixture_cost_usd=2050.0)

    def _compile_tooling_plan(self) -> ToolingPlan:
        tools = [
            ToolingItem("TOOL_WING_MOLD", "Carbon composite wing mold", 3500.0, 150)
        ]
        return ToolingPlan(tooling_list=tools, total_tooling_cost_usd=3500.0)

    def _compile_quality_plan(self) -> QualityPlan:
        checkpoints = [
            QualityCheckpoint("CHK_COMP_VOID", "Post-Cure Wing", "Ultrasonic Scan Check", "No voids > 1.5mm"),
            QualityCheckpoint("CHK_ROTOR_BAL", "Propeller Mount", "Static Rotor Balance Check", "< 0.1 g-mm")
        ]
        return QualityPlan(checkpoints=checkpoints, pass_criteria_description="AS9100 quality checks completed.")

    def _compile_inspection_plan(self) -> InspectionPlan:
        inspections = [
            InspectionItem("Wing Chord length", "350mm", "+/- 0.5mm", "Digital Caliper"),
            InspectionItem("Battery bay depth", "120mm", "+/- 0.2mm", "Depth Gauge")
        ]
        return InspectionPlan(inspections=inspections, inspector_level_required="Level II QA Inspector")

    def _compile_process_plan(self) -> ManufacturingProcessPlan:
        ops = [
            ProcessOperation("OP_10", "Composite layup floor", "Layup carbon composite main skins", 4.0),
            ProcessOperation("OP_20", "Autoclave area", "Bake and cure composite skins", 6.0),
            ProcessOperation("OP_30", "Assembly bench", "Install spars and landing gear", 3.5)
        ]
        return ManufacturingProcessPlan(operations=ops, total_lead_time_days=2.5)

    def _execute_production_sizing(
        self, reqs: ManufacturingRequirements, profile: ManufacturingProfile, is_mass_prod: bool = False
    ) -> ManufacturingResult:
        bom = self._compile_bom()
        instructions = self._compile_assembly_instructions()
        fixtures = self._compile_fixture_plan()
        tooling = self._compile_tooling_plan()
        quality = self._compile_quality_plan()
        inspection = self._compile_inspection_plan()
        process = self._compile_process_plan()
        
        # Sizing pricing
        mat_cost = bom.total_material_cost_usd
        labor_cost = instructions.estimated_assembly_time_hours * profile.labor_rate_usd_per_hour
        
        # Amortize setups over run units
        run_units = reqs.target_production_run_units
        tool_amort = tooling.total_tooling_cost_usd / run_units
        fix_amort = fixtures.total_fixture_cost_usd / run_units
        overhead = (mat_cost + labor_cost) * profile.overhead_markup_ratio
        
        total_cost = mat_cost + labor_cost + tool_amort + fix_amort + overhead
        
        cost_est = ProductionCostEstimate(
            bill_of_materials_cost_usd=mat_cost,
            labor_cost_usd=labor_cost,
            tooling_amortized_cost_usd=tool_amort,
            fixture_amortized_cost_usd=fix_amort,
            overhead_cost_usd=overhead,
            total_unit_cost_usd=total_cost
        )
        
        # Timeline scheduler
        timeline = {"Total Manufacturing Days": 4.5 if not is_mass_prod else 2.1}
        
        # Manufacturability index
        assessment = ManufacturabilityAssessment(
            manufacturability_score_pct=88.0 if not is_mass_prod else 92.0,
            material_utilization_pct=83.0,
            estimated_scrap_rate_pct=5.0,
            assembly_complexity_index=1.45,
            is_manufacturable=True
        )
        
        notes = ["Composite layup molds and jig schedules generated successfully.", "Assembly times verify budget thresholds."]
        recs = ["Purchase fasteners in wholesale batches to reduce unit materials costs."]
        
        return ManufacturingResult(
            bill_of_materials=bom, assembly_instructions=instructions,
            process_plan=process, tooling_plan=tooling, fixture_plan=fixtures,
            quality_plan=quality, inspection_plan=inspection,
            production_cost=cost_est, production_timeline=timeline,
            manufacturability_assessment=assessment, engineering_notes=notes,
            recommendations=recs, warnings=[]
        )

class PrototypeManufacturingStrategy(ManufacturingStrategy):
    def generate_package(self, reqs: ManufacturingRequirements, profile: ManufacturingProfile) -> ManufacturingResult:
        result = self._execute_production_sizing(reqs, profile, is_mass_prod=False)
        result.engineering_notes = ["Prototype individual composite build instructions generated."]
        result.recommendations = ["Build wing layup mockups to check resin absorption rates before final curing."]
        return result

class LowVolumeManufacturingStrategy(ManufacturingStrategy):
    def generate_package(self, reqs: ManufacturingRequirements, profile: ManufacturingProfile) -> ManufacturingResult:
        result = self._execute_production_sizing(reqs, profile, is_mass_prod=False)
        result.engineering_notes = ["Low volume composite layup schedule generated."]
        result.recommendations = ["Review vacuum bag seal integrity parameters on first three production iterations."]
        return result

class ProductionManufacturingStrategy(ManufacturingStrategy):
    def generate_package(self, reqs: ManufacturingRequirements, profile: ManufacturingProfile) -> ManufacturingResult:
        result = self._execute_production_sizing(reqs, profile, is_mass_prod=True)
        result.engineering_notes = ["High volume automated tooling files generated."]
        result.recommendations = ["Deploy CNC jigs to index spar joints automatically."]
        return result

class CompositeManufacturingStrategy(ManufacturingStrategy):
    def generate_package(self, reqs: ManufacturingRequirements, profile: ManufacturingProfile) -> ManufacturingResult:
        result = self._execute_production_sizing(reqs, profile, is_mass_prod=False)
        result.engineering_notes = ["Reinforced carbon composite layup schedules generated."]
        result.recommendations = ["Enforce fiber weave angle tolerances during mold wrapping."]
        return result

class ResearchManufacturingStrategy(ManufacturingStrategy):
    def generate_package(self, reqs: ManufacturingRequirements, profile: ManufacturingProfile) -> ManufacturingResult:
        result = self._execute_production_sizing(reqs, profile, is_mass_prod=False)
        result.engineering_notes = ["Research configurable layout manufacturing documents generated."]
        result.recommendations = ["Ensure sensor mounts allow modular access without structural rework."]
        return result

class BalancedManufacturingStrategy(ManufacturingStrategy):
    def generate_package(self, reqs: ManufacturingRequirements, profile: ManufacturingProfile) -> ManufacturingResult:
        result = self._execute_production_sizing(reqs, profile, is_mass_prod=False)
        result.engineering_notes = ["Balanced industrial/commercial manufacturing package generated."]
        result.recommendations = ["Verify standard fasteners availability before finalizing local build releases."]
        return result
