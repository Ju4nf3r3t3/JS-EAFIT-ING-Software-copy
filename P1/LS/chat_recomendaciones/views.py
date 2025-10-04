from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import base64
import requests
import json

# Importamos el servicio y la estrategia
from .recommendation_service import RecommendationService
from .strategies.huggingface_strategy import HuggingFaceStrategy


@csrf_exempt
@require_POST
def chat_ia(request):
    """
    Endpoint que recibe una descripción y devuelve una recomendación de producto e imagen
    usando el patrón Strategy para la recomendación.
    """
    try:
        # Obtenemos el mensaje del usuario
        descripcion = request.POST.get("message")

        # --- 1. Usamos el Strategy para generar la recomendación ---
        service = RecommendationService(HuggingFaceStrategy())
        recomendacion = service.recomendar(descripcion)

        # --- 2. Si hay recomendación válida, generamos la imagen ---
        imagen_b64 = None
        if recomendacion and "No encontré" not in recomendacion:
            producto_nombre = recomendacion.split(":")[0].strip()
            imagen_b64 = generar_imagen(producto_nombre)

        # --- 3. Respuesta JSON ---
        return JsonResponse({
            "producto": recomendacion,
            "imagen": imagen_b64,
            "status": "success"
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido", "status": "error"}, status=400)
    except Exception as e:
        print(f"Error en endpoint: {str(e)}")
        return JsonResponse({
            "error": "Error interno del servidor",
            "status": "error"
        }, status=500)


def generar_imagen(producto_nombre):
    """
    Genera imágenes usando SDXL con manejo de errores
    """
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}

    prompt = f"Fotografía profesional de {producto_nombre}, fondo blanco, estilo e-commerce, alta calidad, 4k"

    try:
        response = requests.post(
            url,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "width": 512,
                    "height": 512,
                    "num_inference_steps": 20
                }
            },
            timeout=30
        )

        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')

        print(f"Error en imagen: {response.status_code} - {response.text}")
        return None

    except Exception as e:
        print(f"Error en generación de imagen: {str(e)}")
        return None
