from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('perfil/', views.ver_perfil, name='ver_perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
]
