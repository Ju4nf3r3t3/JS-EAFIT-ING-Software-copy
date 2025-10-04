class RecommendationService:
    """Contexto que usa la estrategia elegida."""

    def __init__(self, strategy):
        self.strategy = strategy

    def recomendar(self, descripcion: str) -> str:
        return self.strategy.generar(descripcion)
