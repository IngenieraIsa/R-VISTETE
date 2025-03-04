from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio_view, name='inicio'),  # La página de inicio
    path('api/comentarios/<int:publicacion_id>/', views.get_comentarios, name='get_comentarios'),
    path('api/comentarios/crear/', views.crear_comentario, name='crear_comentario'),
]
