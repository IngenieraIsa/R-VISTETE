from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Usuario, PerfilUsuario
from django.contrib.auth.models import User
import json
from django.urls import reverse

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
        # Buscar el usuario por ID
        usuario = Usuario.objects.get(id=usuario_id)
        perfil, created = PerfilUsuario.objects.get_or_create(usuario=usuario)
        
        context = {
            'usuario': usuario,
            'perfil': perfil,
            'redes_sociales': json.dumps(perfil.redes_sociales) if perfil.redes_sociales else '{}',
            'intereses': perfil.intereses if perfil.intereses else []
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
        # Buscar el usuario por ID
        usuario = Usuario.objects.get(id=usuario_id)
        perfil, created = PerfilUsuario.objects.get_or_create(usuario=usuario)
        
        if request.method == 'POST':
            # Actualizar datos básicos del usuario
            usuario.nombre = request.POST.get('nombre', usuario.nombre)
            usuario.apellido = request.POST.get('apellido', usuario.apellido)
            usuario.save()
            
            # Actualizar datos del perfil
            perfil.descripcion = request.POST.get('descripcion', '')
            perfil.estado = request.POST.get('estado', '')
            perfil.ubicacion = request.POST.get('ubicacion', '')
            perfil.telefono = request.POST.get('telefono', '')
            
            # Procesar redes sociales
            redes_sociales = {}
            for red in ['instagram', 'twitter', 'facebook']:
                if request.POST.get(f'red_{red}'):
                    redes_sociales[red] = request.POST.get(f'red_{red}')
            perfil.redes_sociales = redes_sociales
            
            # Procesar intereses
            intereses = request.POST.get('intereses', '').split(',')
            intereses = [interes.strip() for interes in intereses if interes.strip()]
            perfil.intereses = intereses
            
            perfil.save()
            return redirect('users:ver_perfil')
            
        context = {
            'usuario': usuario,
            'perfil': perfil,
            'redes_sociales': json.dumps(perfil.redes_sociales) if perfil.redes_sociales else '{}',
            'intereses': ','.join(perfil.intereses) if perfil.intereses else ''
        }
        return render(request, 'users/editar_perfil.html', context)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('users:login')

def logout_view(request):
    # Limpiar la sesión
    request.session.flush()
    return redirect('users:login')
