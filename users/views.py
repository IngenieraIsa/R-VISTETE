from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.http import JsonResponse
from .models import Usuario
from django.contrib.auth.models import User

def login_view(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        contrasena = request.POST.get("contrasena")
        
        try:
            # Intentar autenticar al usuario
            usuario = Usuario.objects.get(correo=correo)
            if usuario.contrasena == contrasena:  # Nota: En producción deberías usar hash
                # Crear o obtener un usuario de Django
                user, created = User.objects.get_or_create(
                    username=correo,
                    email=correo
                )
                if created:
                    user.set_password(contrasena)
                    user.save()
                
                # Iniciar sesión
                login(request, user)
                request.session['usuario_id'] = usuario.id
                return redirect('inicio')
            else:
                return JsonResponse({"error": "Contraseña incorrecta"}, status=401)
        except Usuario.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=401)

    return render(request, "login.html")
