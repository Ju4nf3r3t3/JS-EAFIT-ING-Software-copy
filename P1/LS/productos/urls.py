from django.urls import path
from .views import ProductoListView

urlpatterns = [
    path('', ProductoListView.as_view(), name='producto_list'),
]
