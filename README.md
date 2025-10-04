# JS-EAFIT

This platform enables university entrepreneurs to showcase their businesses and products through personalized profiles. Buyers can explore ventures in a social media-style feed with interactive product cards. The platform features a basic chat system for direct communication between buyers and sellers, along with a star-based rating system to enhance trust and credibility.


# Taller 1 – Integración de IA, CRUD y Patrones de Diseño en Django

## Introducción

Este proyecto corresponde al Taller 1 de la asignatura de Ingeniería de Software. El objetivo fue **integrar una funcionalidad de recomendación con IA**, **implementar un CRUD para productos** y **aplicar el patrón de diseño Strategy** dentro de un proyecto Django ya existente.

Se documentan a continuación todos los pasos realizados.

---

## Actividad 2- Revisión 


1. Usabilidad
Aspectos cumplidos:

La interfaz emplea Bootstrap y tipografía clara, lo que facilita la navegación y la legibilidad.

La barra de búsqueda es intuitiva y cuenta con filtros por categoría y ubicación.

El módulo de recomendaciones mediante chat agrega valor al ofrecer sugerencias personalizadas.

Aspectos a mejorar:

Incorporar un sistema de autocompletado en la búsqueda para orientar al usuario.

Implementar retroalimentación visual más detallada en procesos como compra, inicio de sesión o uso del carrito.

Mejorar la accesibilidad mediante soporte para lectores de pantalla y etiquetas ARIA.

Inversión sugerida: pruebas de usabilidad con usuarios reales y adopción de librerías enfocadas en accesibilidad.

2. Compatibilidad
Aspectos cumplidos:

El uso de Bootstrap 5 garantiza compatibilidad en navegadores modernos.

El diseño es responsivo y se adapta a distintos tamaños de pantalla.

Aspectos a mejorar:

Verificar el correcto funcionamiento en navegadores antiguos.

Realizar pruebas en diferentes sistemas operativos y dispositivos móviles con distintos formatos de pantalla.

Inversión sugerida: herramientas de testing multiplataforma, como BrowserStack o SauceLabs.

3. Rendimiento
Aspectos cumplidos:

Las imágenes cuentan con tamaños definidos y se ajustan correctamente.

El uso de CDN para Bootstrap e iconos reduce los tiempos de carga.

Aspectos a mejorar:

Implementar carga diferida (lazy loading) de imágenes para mejorar tiempos de respuesta.

Incorporar mecanismos de caché en consultas frecuentes a la base de datos.

Garantizar que el sistema de recomendaciones no afecte el rendimiento bajo alta concurrencia.

Inversión sugerida: contratación de servicios de hosting con CDN integrado y uso de tecnologías de caché como Redis o Memcached.

4. Seguridad

Aspectos cumplidos:

El sistema emplea token CSRF para prevenir ataques de falsificación de peticiones.

Existe una base para la autenticación de usuarios mediante el módulo de inicio de sesión.

Aspectos a mejorar:

Asegurar el cifrado de contraseñas mediante algoritmos robustos como bcrypt o argon2.

Incluir validaciones adicionales en formularios para prevenir inyección de código.

Configurar el uso obligatorio de HTTPS en el servidor.

Inversión sugerida: adquisición de certificados SSL, implementación de un firewall de aplicaciones web (WAF) y realización de auditorías de seguridad externas.
## Actividad 3 – Integración de API Externa para Recomendaciones (chat_ia)

Para esta actividad se implementó un **endpoint** que recibe un mensaje de usuario, envía el texto a un modelo de IA (Mistral 7B) a través de la API de Hugging Face y devuelve una **recomendación de producto**. Además, si el modelo genera una recomendación válida, se solicita una imagen del producto a un modelo de **generación de imágenes** (SDXL).

--

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


## Bonus 

Propuesta de nueva funcionalidad: Sistema de Reseñas y Calificaciones de Productos

Se implementará un sistema de reseñas y calificaciones para los productos publicados en la plataforma. Los usuarios podrán:

Calificar un producto con una escala de 1 a 5 estrellas.

Escribir una reseña detallada sobre su experiencia con el producto o el vendedor.

Visualizar el promedio de calificaciones en cada producto y filtrar búsquedas por puntaje mínimo.

Esta funcionalidad busca mejorar la confianza y transparencia en la plataforma, permitiendo que otros usuarios tomen decisiones más informadas a la hora de comprar.

Justificación de la funcionalidad

Incrementa la usabilidad: los usuarios pueden conocer la opinión de otros compradores antes de adquirir un producto.

Mejora la competitividad: los vendedores tendrán incentivos para ofrecer mejores productos y servicios.

Aporta a la seguridad: ayuda a identificar productos o vendedores poco confiables mediante calificaciones negativas recurrentes.

Fomenta la participación: involucra activamente a los usuarios, generando una comunidad más dinámica.

Patrones de diseño aplicados

Patrón MVC (Model-View-Controller)

Modelo: se crea una entidad Review asociada a un Product y a un User, que almacene la calificación y el comentario.

Vista: en la interfaz del producto, se mostrará el promedio de estrellas y la lista de reseñas.

Controlador: se encargará de gestionar la lógica de agregar, editar y mostrar reseñas.

Justificación: separa claramente la lógica de negocio, la persistencia de datos y la interfaz de usuario, manteniendo la escalabilidad del sistema.

Patrón Observer (Observador)

Cada vez que una reseña nueva sea añadida, el producto será “notificado” para actualizar automáticamente su promedio de calificaciones.

Justificación: permite mantener actualizado el promedio sin necesidad de recalcularlo manualmente en cada consulta.

Patrón Strategy (Estrategia)

Se aplicará para el cálculo de métricas de productos (ejemplo: promedio simple, ponderación por antigüedad de reseñas, exclusión de reseñas sospechosas).

Justificación: permite intercambiar fácilmente distintos algoritmos de cálculo de reputación sin modificar el código central.

Posibles inversiones necesarias

Base de datos: ampliar el modelo con nuevas tablas para reseñas.

Interfaz de usuario: desarrollo de un componente dinámico (por ejemplo, con AJAX o React) para gestionar la publicación de reseñas sin recargar la página.

Moderación de contenido: integrar herramientas de detección automática de lenguaje ofensivo o spam.

** Código:


(Models.py): Modelo asociado a Product y a user:

from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def average_rating(self):
        reviews = self.review_set.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')  # Un usuario solo puede reseñar una vez un producto

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating})"


(Form:py): Formulario para enviar la reseña

from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


(views.py) Vistas


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Review
from .forms import ReviewForm

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.review_set.all().order_by('-created_at')

    if request.method == "POST":
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                return redirect('product_detail', product_id=product.id)
        else:
            return redirect('login')
    else:
        form = ReviewForm()

    return render(request, "product_detail.html", {
        "product": product,
        "reviews": reviews,
        "form": form,
        "average_rating": product.average_rating()
    })



(product_detail.html) Template 


{% extends "base.html" %}
{% load static %}

{% block content %}
<div class="container mt-4">
    <h2>{{ product.name }}</h2>
    <p><strong>Categoría:</strong> {{ product.category }}</p>
    <p><strong>Precio:</strong> ${{ product.price }}</p>
    <p><strong>Promedio de calificación:</strong> {{ average_rating }} ⭐</p>
    <hr>

    <h4>Reseñas</h4>
    {% if reviews %}
        {% for review in reviews %}
            <div class="card mb-2">
                <div class="card-body">
                    <h6>{{ review.user.username }} - {{ review.rating }} ⭐</h6>
                    <p>{{ review.comment }}</p>
                    <small class="text-muted">{{ review.created_at|date:"d/m/Y H:i" }}</small>
                </div>
            </div>
        {% endfor %}
    {% else %}
        <p>No hay reseñas aún.</p>
    {% endif %}

    <hr>
    <h5>Agregar Reseña</h5>
    {% if user.is_authenticated %}
        <form method="POST">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit" class="btn btn-primary">Enviar</button>
        </form>
    {% else %}
        <p>Debes <a href="{% url 'login' %}">iniciar sesión</a> para dejar una reseña.</p>
    {% endif %}
</div>
{% endblock %}



(urls.py) URLS

from django.urls import path
from . import views

urlpatterns = [
    path('producto/<int:product_id>/', views.product_detail, name='product_detail'),
]






