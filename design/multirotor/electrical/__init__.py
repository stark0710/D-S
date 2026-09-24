"""
Multirotor Power Distribution and Electrical Integration Package.
"""

from backend.design.multirotor.electrical.electrical_models import ElectricalContext, ElectricalCandidate
from backend.design.multirotor.electrical.connector_selector import ConnectorSelector, CatalogConnectorRecord
from backend.design.multirotor.electrical.wiring_optimizer import WiringOptimizer, CatalogWireRecord
from backend.design.multirotor.electrical.power_distribution import PowerDistributionSizer
from backend.design.multirotor.electrical.electrical_constraints import ElectricalConstraintsEvaluator
from backend.design.multirotor.electrical.electrical_validator import ElectricalValidator
from backend.design.multirotor.electrical.electrical_result import ElectricalSpecification
from backend.design.multirotor.electrical.electrical_engine import ElectricalEngine

__all__ = [
    "ElectricalContext",
    "ElectricalCandidate",
    "ConnectorSelector",
    "CatalogConnectorRecord",
    "WiringOptimizer",
    "CatalogWireRecord",
    "PowerDistributionSizer",
    "ElectricalConstraintsEvaluator",
    "ElectricalValidator",
    "ElectricalSpecification",
    "ElectricalEngine",
]
