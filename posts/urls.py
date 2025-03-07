from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio_view, name='inicio'),  # La página de inicio
    path('api/comentarios/<int:publicacion_id>/', views.get_comentarios, name='get_comentarios'),
    path('api/comentarios/crear/', views.crear_comentario, name='crear_comentario'),
    path('mis-ventas/', views.mis_ventas_view, name='mis_ventas'),
    path('mis-alquileres/', views.mis_alquileres_view, name='mis_alquileres'),
    path('notificaciones/', views.notificaciones_view, name='notificaciones'),
]
