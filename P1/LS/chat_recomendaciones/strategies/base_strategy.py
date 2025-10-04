from abc import ABC, abstractmethod


class RecommendationStrategy(ABC):
    """Interfaz para las estrategias de recomendación."""

    @abstractmethod
    def generar(self, descripcion: str) -> str:
        pass
