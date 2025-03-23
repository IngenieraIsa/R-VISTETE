from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio_view, name='inicio'),  # La página de inicio
    path('publicacion/<int:publicacion_id>/', views.ver_publicacion, name='ver_publicacion'),
    path('mis-likes/', views.ver_likes, name='ver_likes'),
    path('mis-favoritos/', views.ver_favoritos, name='ver_favoritos'),
    path('api/likes/<int:publicacion_id>/', views.toggle_like, name='toggle_like'),
    path('api/favoritos/<int:publicacion_id>/', views.toggle_favorito, name='toggle_favorito'),
    path('api/comentarios/get/<int:publicacion_id>/', views.get_comentarios, name='get_comentarios'),
    path('api/comentarios/agregar/<int:publicacion_id>/', views.agregar_comentario, name='agregar_comentario'),
    path('publicar/', views.publicar_prenda, name='publicar_prenda'),
    path('mis-ventas/', views.mis_ventas_view, name='mis_ventas'),
    path('mis-alquileres/', views.mis_alquileres_view, name='mis_alquileres'),
]
