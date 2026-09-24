"""
Fixed-Wing CAD Propulsion Generator Subsystem

Purpose:
    Defines the `PropulsionGenerator` class.

Role in Architecture:
    `PropulsionGenerator` generates motor brackets, mount firewalls, and propellers blocks.
"""

from backend.design.fixed_wing.cad.part_generator import PartGenerator


class PropulsionGenerator(PartGenerator):
    """
    Parametric motor mount and propeller generator.
    """

    def generate_propulsion(
        self,
        prop_diameter_in: float,
        is_pusher: bool,
    ) -> str:
        """
        Generates propulsion brackets.

        Returns:
            str: Solid representation string.
        """
        motor_bracket = self.builder.create_cylinder("MotorBracket", 0.02, 0.04)
        prop_block = self.builder.create_cylinder("PropellerDisc", prop_diameter_in * 0.0254 / 2.0, 0.005)
        
        prop_solid = f"Propulsion(bracket={motor_bracket}, prop={prop_block}, pusher={is_pusher})"
        self.tree.add_feature("AssemblyMerge", "propulsion", {"diameter": prop_diameter_in, "is_pusher": is_pusher})
        return prop_solid
