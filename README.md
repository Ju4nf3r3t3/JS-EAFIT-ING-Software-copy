# JS-EAFIT

This platform enables university entrepreneurs to showcase their businesses and products through personalized profiles. Buyers can explore ventures in a social media-style feed with interactive product cards. The platform features a basic chat system for direct communication between buyers and sellers, along with a star-based rating system to enhance trust and credibility.


# Taller 1 – Integración de IA, CRUD y Patrones de Diseño en Django

## Introducción

Este proyecto corresponde al Taller 1 de la asignatura de Ingeniería de Software. El objetivo fue **integrar una funcionalidad de recomendación con IA**, **implementar un CRUD para productos** y **aplicar el patrón de diseño Strategy** dentro de un proyecto Django ya existente.

Se documentan a continuación todos los pasos realizados.

---

## Actividad 3 – Integración de API Externa para Recomendaciones (chat_ia)

Para esta actividad se implementó un **endpoint** que recibe un mensaje de usuario, envía el texto a un modelo de IA (Mistral 7B) a través de la API de Hugging Face y devuelve una **recomendación de producto**. Además, si el modelo genera una recomendación válida, se solicita una imagen del producto a un modelo de **generación de imágenes** (SDXL).

### Cambios realizados

1. Se creó la carpeta `chat_recomendaciones` (ya existente en el proyecto) y se actualizó el archivo `views.py`.

2. Se agregó el endpoint en `urls.py`:

```python
path("recomendaciones/chat/", chat_ia, name="chat_ia")
```

3. Se creó la función `chat_ia` que:
   - Recibe el mensaje enviado por el usuario vía `POST`.
   - Llama a `generar_recomendacion(descripcion)`.
   - Si la recomendación es válida, llama a `generar_imagen(producto_nombre)`.
   - Devuelve la respuesta en formato JSON.

4. Se crearon las funciones auxiliares:
   - **`generar_recomendacion(descripcion)`**: Llama al modelo **Mistral-7B-Instruct** en Hugging Face para generar texto.
   - **`generar_imagen(producto_nombre)`**: Usa **Stable Diffusion XL** en Hugging Face para crear la imagen del producto.

---

## Actividad 4 – CRUD de Productos con Django ORM

Se creó una nueva app llamada **productos** para implementar un CRUD (Create, Read, Update, Delete) usando el **ORM de Django**.

### Pasos realizados

1. Crear la app:

```bash
python manage.py startapp productos
```

2. Agregar la app en `INSTALLED_APPS` de `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'productos',
]
```

3. Definir los modelos en `productos/models.py`:

```python
from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
```

4. Crear y aplicar las migraciones:

```bash
python manage.py makemigrations productos
python manage.py migrate
```

5. Registrar los modelos en `productos/admin.py` para poder gestionarlos desde el panel de administración:

```python
from django.contrib import admin
from .models import Categoria, Producto

admin.site.register(Categoria)
admin.site.register(Producto)
```

6. Iniciar el servidor y verificar el CRUD desde `/admin`.

### Resultado

Los administradores pueden **crear, listar, actualizar y eliminar** categorías y productos desde el panel admin de Django. Se cumplió el objetivo de implementar un CRUD completo usando el ORM de Django.

---

## Actividad 5 – Aplicación del Patrón de Diseño Strategy

Para mejorar la **escalabilidad y el mantenimiento del código**, se implementó el patrón de diseño **Strategy** en la funcionalidad de recomendaciones de la app `chat_recomendaciones`.

### Pasos realizados

1. Se creó el archivo `services/strategies.py`:

```python
from abc import ABC, abstractmethod
import requests
from django.conf import settings

class RecommendationStrategy(ABC):
    @abstractmethod
    def generar(self, descripcion):
        pass

class MistralRecommendation(RecommendationStrategy):
    def generar(self, descripcion):
        url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
        headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
        prompt = f"Eres un experto en recomendaciones para estudiantes.\nUsuario: {descripcion}\nAsistente:"

        response = requests.post(url, headers=headers, json={
            "inputs": prompt,
            "parameters": {"temperature": 0.7, "max_new_tokens": 50}
        })

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and data:
                texto = data[0].get("generated_text", "")
                return texto.strip()
        return "No encontré recomendaciones."

class DummyRecommendation(RecommendationStrategy):
    def generar(self, descripcion):
        return f"Recomendación simulada para: {descripcion}"
```

2. Se actualizó `views.py` para usar la estrategia:

```python
from .services.strategies import MistralRecommendation

def generar_recomendacion(descripcion):
    strategy = MistralRecommendation()
    return strategy.generar(descripcion)
```

3. De esta forma, el proyecto puede cambiar fácilmente entre diferentes estrategias (por ejemplo, un modelo de IA real, uno de prueba, etc.).

---

## Pruebas Realizadas

### 1. Servidor

```bash
python manage.py runserver
```

El servidor corrió sin errores. Se pudo acceder a la interfaz de administración.

### 2. CRUD de Productos

Se crearon categorías y productos desde `/admin`. Se verificó que las relaciones y las operaciones CRUD funcionen correctamente.

### 3. Endpoint de Recomendaciones

Se probó con `curl`:

```bash
curl -X POST -d "message=Recomiendame un cuaderno para la universidad" http://127.0.0.1:8000/recomendaciones/chat/
```

El endpoint devolvió una respuesta JSON (en pruebas locales puede fallar si no se tiene la clave de la API de Hugging Face configurada).

---




