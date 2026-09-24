"""
Fixed-Wing CAD Part Generator Base Subsystem

Purpose:
    Defines the `PartGenerator` base class.

Role in Architecture:
    `PartGenerator` contains common parameters and builders to generate parts.
"""

from backend.design.fixed_wing.cad.geometry_builder import GeometryBuilder
from backend.design.fixed_wing.cad.feature_tree import FeatureTree


class PartGenerator:
    """
    Base class for individual subsystem CAD shape generators.
    """

    def __init__(self, builder: GeometryBuilder, feature_tree: FeatureTree) -> None:
        self.builder = builder
        self.tree = feature_tree
