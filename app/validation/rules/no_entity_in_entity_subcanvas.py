from app.validation.rule import Rule


class NoEntityInEntitySubcanvas(Rule):
    def applies_to(self, action_type: str) -> bool:
        return action_type == "subcanvas_add_node"

    def check(self, context: dict) -> str | None:
        if context.get("parent_is_entity") and context.get("child_type") in (
            "actor",
            "agent",
        ):
            return (
                "No se puede agregar un Actor/Agente dentro del subcanvas "
                "de otro Actor/Agente. Los subcanvases son para elementos "
                "Tropos (Metas, Recursos, Planes, Softgoals)."
            )
        return None


rule = NoEntityInEntitySubcanvas()
