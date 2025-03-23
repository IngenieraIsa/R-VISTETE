from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Usuario, PerfilUsuario
from posts.models import Publicacion, Venta, Alquiler
from django.contrib.auth.models import User
import json
from django.urls import reverse
from django.contrib import messages
from .forms import PerfilUsuarioForm

def login_view(request):
    # Debug logging
    print("Login view called")
    print("Session:", request.session.items())
    print("Next parameter:", request.GET.get('next'))
    
    # Si el usuario ya está autenticado, redirigir directamente a inicio
    if request.session.get('usuario_id'):
        return redirect('/inicio/')
    
    if request.method == "POST":
        correo = request.POST.get("correo")
        contrasena = request.POST.get("contrasena")
        
        # Validar que se proporcionaron ambos campos
        if not correo or not contrasena:
            return render(request, "users/login.html", {
                "error": "Por favor ingresa tanto el correo como la contraseña"
            })
        
        try:
            # Buscar el usuario en la tabla usuarios
            usuario = Usuario.objects.get(correo=correo)
            
            # Validar la contraseña
            if usuario.contrasena == contrasena:
                # Guardar el ID del usuario en la sesión
                request.session['usuario_id'] = usuario.id
                request.session['nombre_usuario'] = usuario.nombre
                request.session.save()
                
                # Redirigir a la página de inicio usando path absoluto
                return redirect('/inicio/')
            else:
                return render(request, "users/login.html", {
                    "error": "La contraseña es incorrecta",
                    "correo": correo
                })
                
        except Usuario.DoesNotExist:
            return render(request, "users/login.html", {
                "error": "No existe una cuenta con este correo",
                "correo": correo
            })

    return render(request, "users/login.html")

def ver_perfil(request):
    # Verificar si el usuario está autenticado
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('users:login')
    
    try:
        # Buscar el usuario y su perfil
        usuario = Usuario.objects.get(id=usuario_id)
        perfil, created = PerfilUsuario.objects.get_or_create(usuario=usuario)
        
        context = {
            'usuario': usuario,
            'perfil': perfil,
            'estadisticas': {
                'publicaciones': Publicacion.objects.filter(usuario=usuario).count(),
                'ventas': Venta.objects.filter(vendedor=usuario).count(),
                'alquileres': Alquiler.objects.filter(cliente=usuario).count()
            }
        }
        return render(request, 'users/perfil.html', context)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('users:login')

def editar_perfil(request):
    # Verificar si el usuario está autenticado
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('users:login')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        perfil, created = PerfilUsuario.objects.get_or_create(usuario=usuario)
        
        if request.method == 'POST':
            form = PerfilUsuarioForm(request.POST, instance=perfil)
            if form.is_valid():
                # Procesar las redes sociales
                redes_sociales = {
                    'instagram': request.POST.get('instagram', ''),
                    'twitter': request.POST.get('twitter', ''),
                    'facebook': request.POST.get('facebook', '')
                }
                perfil.redes_sociales = redes_sociales
                
                # Guardar el formulario
                form.save()
                messages.success(request, 'Perfil actualizado exitosamente.')
                return redirect('users:ver_perfil')
            else:
                messages.error(request, 'Por favor, corrige los errores en el formulario.')
        else:
            # Preparar datos iniciales
            initial_data = {
                'marcas_favoritas': ', '.join(perfil.marcas_favoritas) if perfil.marcas_favoritas else '',
                'ocasiones_uso': ', '.join(perfil.ocasiones_uso) if perfil.ocasiones_uso else '',
            }
            form = PerfilUsuarioForm(instance=perfil, initial=initial_data)
        
        return render(request, 'users/editar_perfil.html', {
            'form': form,
            'usuario': usuario,
            'perfil': perfil
        })
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('users:login')

def logout_view(request):
    # Limpiar la sesión
    request.session.flush()
    return redirect('users:login')
