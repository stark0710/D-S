import os
import importlib
import inspect
from typing import List
from backend.design.common.verification.models import VerificationRule
from backend.design.common.verification.rule_registry import global_registry

class RuleLoader:
    @staticmethod
    def load_rules_from_directory(directory_path: str = None, package_name: str = None) -> List[VerificationRule]:
        """Dynamically imports python modules in the rules directory and registers rules."""
        if not directory_path:
            # Default to the rules directory next to this file
            directory_path = os.path.join(os.path.dirname(__file__), "rules")
        if not package_name:
            package_name = "backend.design.common.verification.rules"

        if not os.path.exists(directory_path):
            return []

        loaded_rules = []
        for filename in os.listdir(directory_path):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                full_module_name = f"{package_name}.{module_name}"
                try:
                    module = importlib.import_module(full_module_name)
                    # Reload to ensure freshness
                    importlib.reload(module)
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, VerificationRule) and 
                            obj is not VerificationRule):
                            # Instantiate the rule
                            rule_instance = obj()
                            # Check config layout classification
                            config_type = getattr(rule_instance, "config_type", "Generic")
                            global_registry.register_rule(config_type, rule_instance)
                            loaded_rules.append(rule_instance)
                except Exception as e:
                    print(f"Failed to load module {full_module_name}: {e}")
        return loaded_rules
