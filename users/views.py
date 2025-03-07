from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Usuario, PerfilUsuario
from django.contrib.auth.models import User
import json

def login_view(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        contrasena = request.POST.get("contrasena")
        
        try:
            # Intentar encontrar el usuario personalizado
            usuario = Usuario.objects.get(correo=correo)
            if usuario.contrasena == contrasena:  # Nota: En producción deberías usar hash
                # Crear o obtener el usuario de Django
                if usuario.user is None:
                    # Crear nuevo usuario de Django
                    user = User.objects.create_user(
                        username=correo,
                        email=correo,
                        password=contrasena
                    )
                    # Vincular con nuestro modelo Usuario
                    usuario.user = user
                    usuario.save()
                else:
                    user = usuario.user
                
                # Iniciar sesión
                login(request, user)
                return redirect('inicio')
            else:
                return JsonResponse({"error": "Contraseña incorrecta"}, status=401)
        except Usuario.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=401)

    return render(request, "login.html")

@login_required
def ver_perfil(request):
    try:
        # Buscar el usuario por el correo del usuario autenticado
        usuario = Usuario.objects.get(correo=request.user.email)
        perfil, created = PerfilUsuario.objects.get_or_create(usuario=usuario)
        
        context = {
            'usuario': usuario,
            'perfil': perfil,
            'redes_sociales': json.dumps(perfil.redes_sociales) if perfil.redes_sociales else '{}',
            'intereses': perfil.intereses if perfil.intereses else []
        }
        return render(request, 'perfil.html', context)
    except Usuario.DoesNotExist:
        return redirect('login')

@login_required
def editar_perfil(request):
    try:
        # Buscar el usuario por el correo del usuario autenticado
        usuario = Usuario.objects.get(correo=request.user.email)
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
            return redirect('ver_perfil')
            
        context = {
            'usuario': usuario,
            'perfil': perfil,
            'redes_sociales': json.dumps(perfil.redes_sociales) if perfil.redes_sociales else '{}',
            'intereses': ','.join(perfil.intereses) if perfil.intereses else ''
        }
        return render(request, 'editar_perfil.html', context)
    except Usuario.DoesNotExist:
        return redirect('login')
