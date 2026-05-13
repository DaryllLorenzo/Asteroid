from app.validation.rule import Rule


class NoMeansEndBetweenEntities(Rule):
    def applies_to(self, action_type: str) -> bool:
        return action_type == "create_edge"

    def check(self, context: dict) -> str | None:
        if (
            context.get("arrow_type") == "means_end"
            and context.get("source_is_entity")
            and context.get("dest_is_entity")
        ):
            return (
                "No se puede crear un enlace Means-End entre "
                "Actores/Agentes. Los enlaces son para elementos Tropos "
                "dentro del subcanvas."
            )
        return None


rule = NoMeansEndBetweenEntities()
