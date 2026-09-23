import sys
import os
sys.path.insert(0, os.getcwd())
import inspect
import importlib

optimizers = [
    ("WingPlanformOptimizer", "backend.design.fixed_wing.wing.optimization.wing_planform_optimizer", "WingPlanformOptimizer"),
    ("FuselageOptimizer", "backend.design.fixed_wing.fuselage.optimization.fuselage_optimizer", "FuselageOptimizer"),
    ("PayloadPackagingOptimizer", "backend.design.fixed_wing.payload.optimization.payload_optimizer", "PayloadPackagingOptimizer"),
    ("TailOptimizer", "backend.design.fixed_wing.tail.optimization.tail_optimizer", "TailOptimizer"),
    ("PropulsionOptimizer", "backend.design.fixed_wing.propulsion.optimization.propulsion_optimizer", "PropulsionOptimizer"),
    ("ElectricalOptimizer", "backend.design.fixed_wing.electrical.electrical_optimizer", "ElectricalOptimizer"),
    ("MassPropertiesOptimizer", "backend.design.fixed_wing.mass_properties.optimization.mass_optimizer", "MassPropertiesOptimizer"),
    ("CGOptimizer", "backend.design.fixed_wing.cg.optimization.cg_optimizer", "CGOptimizer"),
    ("FlightPerformanceOptimizer", "backend.design.fixed_wing.performance.optimization.performance_engine", "FlightPerformanceOptimizer"),
]

for name, mod_path, cls_name in optimizers:
    print(f"\n======================================================================")
    print(f"OPTIMIZER: {name} ({mod_path})")
    print(f"======================================================================")
    try:
        mod = importlib.import_module(mod_path)
        cls = getattr(mod, cls_name)
        inst = cls()
        print(f"  Base class: {[b.__name__ for b in cls.__mro__]}")
        print(f"  Constraint manager: {inst.constraints.__class__.__name__ if hasattr(inst, 'constraints') else 'None'}")
        if hasattr(inst, 'constraints') and hasattr(inst.constraints, '_constraints'):
            print(f"    Constraints count: {len(inst.constraints._constraints)}")
            for c in inst.constraints._constraints:
                fn_name = c.check_fn.__name__ if hasattr(c.check_fn, '__name__') else str(c.check_fn)
                print(f"      - {c.name}: {fn_name}")
        
        print(f"  Objective function: {inst.objective.__class__.__name__ if hasattr(inst, 'objective') else 'None'}")
        if hasattr(inst, 'objective') and hasattr(inst.objective, '_terms'):
            print(f"    Objective terms count: {len(inst.objective._terms)}")
            for term in inst.objective._terms:
                fn_name = term.score_fn.__name__ if hasattr(term.score_fn, '__name__') else str(term.score_fn)
                print(f"      - {term.name}: weight={term.weight}, minimize={term.minimize}, func={fn_name}")
    except Exception as e:
        print(f"  ERROR inspecting {name}: {e}")
