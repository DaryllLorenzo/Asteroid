import importlib
import pkgutil

from app.validation.rule import Rule


class Validator:
    """
    Validator.

    Methods:
        __init__: Initialize the instance.
        validate: Validate.
    """

    def __init__(self) -> None:
        """Initialize the instance."""
        self.active: bool = False
        self._rules: list[Rule] = []
        self._discover_rules()

    def _discover_rules(self) -> None:
        """Discover Rules."""
        import app.validation.rules as rules_pkg

        for _, module_name, _ in pkgutil.iter_modules(rules_pkg.__path__):
            module = importlib.import_module(f"app.validation.rules.{module_name}")
            if hasattr(module, "rule") and isinstance(module.rule, Rule):
                self._rules.append(module.rule)

    def validate(self, action_type: str, context: dict) -> list[str]:
        """
        Validate.

        Args:
            action_type (str): The action type.
            context (dict): The context.

        Returns:
            list[str]: Validate.
        """
        if not self.active:
            return []
        errors: list[str] = []
        for rule in self._rules:
            if rule.applies_to(action_type):
                error = rule.check(context)
                if error:
                    errors.append(error)
        return errors
