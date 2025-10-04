import requests
from django.conf import settings

from .base_strategy import RecommendationStrategy


class HuggingFaceStrategy(RecommendationStrategy):
    def generar(self, descripcion: str) -> str:
        url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
        headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}

        prompt = f"""Eres un experto en recomendaciones de productos para estudiantes universitarios.
Responde ÚNICAMENTE con el formato: "Nombre del producto: breve descripción (máximo 8 palabras)"

Ejemplo: "Cuaderno profesional: 200 hojas con espiral metálico"

Usuario: {descripcion}
Asistente:"""

        data = {
            "inputs": prompt,
            "parameters": {
                "temperature": 0.7,
                "max_new_tokens": 50,
                "do_sample": True
            }
        }

        try:
            response = requests.post(
                url, headers=headers, json=data, timeout=25)
            if response.status_code == 200:
                resultado = response.json()
                if isinstance(resultado, list) and resultado:
                    texto = resultado[0].get('generated_text', '')
                    if "Asistente:" in texto:
                        return texto.split("Asistente:")[1].strip().strip('"')
                    return texto.strip().strip('"')
            return "No encontré productos. Por favor describe mejor lo que necesitas."
        except Exception as e:
            print(f"Error en HuggingFaceStrategy: {str(e)}")
            return "El servicio de recomendaciones no está disponible temporalmente."
