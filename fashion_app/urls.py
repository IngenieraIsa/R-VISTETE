"""
URL configuration for fashion_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def home_view(request):
    # Debug logging
    print("Home view called")
    print("Session:", request.session.items())
    
    usuario_id = request.session.get('usuario_id')
    print("Usuario ID from session:", usuario_id)
    
    # Si el usuario está autenticado, redirigir a inicio
    if usuario_id:
        print("Usuario autenticado, redirigiendo a inicio")
        return redirect('/inicio/')
    
    # Si no está autenticado, redirigir al login
    print("Usuario no autenticado, redirigiendo a login")
    return redirect('/usuarios/login/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('users.urls')),
    path('inicio/', include('posts.urls')),  # Todas las URLs de posts estarán bajo /inicio/
    path('', home_view, name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

