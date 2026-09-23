"""
CADEngine Subsystem

Purpose:
    Defines the `CADEngine` class, which serves as the public entry point for multirotor CAD generation engineering.

Role in Architecture:
    `CADEngine` receives engineered subsystem outputs (`FrameResult`, `PropulsionResult`, `ElectricalResult`, `AvionicsResult`, `PayloadResult`),
    resolves strategy from `CADRegistry`, executes 3D CAD model generation via `CADStrategy`, validates outputs via `CADValidator`,
    and returns a `CADResult`.
"""

from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.avionics.avionics_result import AvionicsResult
from backend.design.drone.payload.payload_result import PayloadResult
from backend.design.drone.cad.cad_constraints import CADConstraints
from backend.design.drone.cad.cad_result import CADResult
from backend.design.drone.cad.cad_validator import CADValidator
from backend.design.drone.cad.cad_registry import CADRegistry
from backend.design.drone.cad.cad_strategy import (
    NeutralCADStrategy,
    FreeCADStrategy,
)


class CADEngine:
    """
    Public entry point service for multirotor CAD generation engineering.

    Design Principles:
        - Single Responsibility Principle: Multirotor 3D CAD geometry generation and export representation only.
        - Dependency Injection: Injects `CADRegistry` and `CADValidator` collaborators.
        - Non-Optimization: Converts engineering data into geometric representations without modifying engineering parameters.
    """

    def __init__(
        self,
        registry: CADRegistry | None = None,
        validator: CADValidator | None = None
    ) -> None:
        """Initializes the CADEngine."""
        if registry is None:
            registry = CADRegistry()
            registry.register_strategy(NeutralCADStrategy())
            registry.register_strategy(FreeCADStrategy())

        self._registry: CADRegistry = registry
        self._validator: CADValidator = validator if validator else CADValidator()

    def generate_cad(
        self,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult,
        payload_result: PayloadResult,
        strategy_name: str = "NeutralCADStrategy",
        export_format: str = "JSON_PARAMETRIC",
        constraints: CADConstraints | None = None
    ) -> CADResult:
        """
        Converts an approved multirotor design into a parametric digital aircraft CAD model.

        Args:
            structure_result (FrameResult): Frame result.
            propulsion_result (PropulsionResult): Propulsion result.
            electrical_result (ElectricalResult): Electrical result.
            avionics_result (AvionicsResult): Avionics result.
            payload_result (PayloadResult): Payload result.
            strategy_name (str): Identifier name of the strategy to execute.
            export_format (str): Desired CAD export format ('STEP', 'IGES', 'STL', 'OBJ', 'JSON_PARAMETRIC').
            constraints (CADConstraints | None): CAD constraints.

        Returns:
            CADResult: Completed CAD generation engineering output summary.
        """
        const = constraints if constraints else CADConstraints()
        strategy = self._registry.get_strategy(strategy_name)

        cad_res = strategy.generate_cad(
            structure_result=structure_result,
            propulsion_result=propulsion_result,
            electrical_result=electrical_result,
            avionics_result=avionics_result,
            payload_result=payload_result,
            export_format=export_format
        )

        warns = self._validator.validate_cad(cad_res, const)
        if warns:
            cad_res.warnings.extend(warns)

        return cad_res
