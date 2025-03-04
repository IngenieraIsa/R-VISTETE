from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Publicacion, Comentario
import json

@login_required(login_url='/users/login/')
def inicio_view(request):
    # Obtener todas las publicaciones ordenadas por fecha
    publicaciones = Publicacion.objects.all().order_by('-fecha_publicacion')
    return render(request, 'inicio.html', {'publicaciones': publicaciones})

@login_required
def get_comentarios(request, publicacion_id):
    try:
        comentarios = Comentario.objects.filter(publicacion_id=publicacion_id).order_by('-fecha_comentario')
        comentarios_data = []
        
        for comentario in comentarios:
            comentarios_data.append({
                'id': comentario.id,
                'usuario_nombre': comentario.usuario.nombre,
                'usuario_foto': comentario.usuario.foto_perfil,
                'comentario': comentario.comentario,
                'fecha_comentario': comentario.fecha_comentario.isoformat()
            })
        
        return JsonResponse(comentarios_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def crear_comentario(request):
    try:
        comentario_texto = request.POST.get('comentario')
        publicacion_id = request.POST.get('publicacion_id')
        
        if not comentario_texto or not publicacion_id:
            return JsonResponse({'error': 'Faltan datos requeridos'}, status=400)
        
        publicacion = Publicacion.objects.get(id=publicacion_id)
        
        comentario = Comentario.objects.create(
            usuario=request.user.usuario,
            publicacion=publicacion,
            comentario=comentario_texto
        )
        
        return JsonResponse({
            'success': True,
            'comentario': {
                'id': comentario.id,
                'usuario_nombre': comentario.usuario.nombre,
                'usuario_foto': comentario.usuario.foto_perfil,
                'comentario': comentario.comentario,
                'fecha_comentario': comentario.fecha_comentario.isoformat()
            }
        })
    except Publicacion.DoesNotExist:
        return JsonResponse({'error': 'Publicación no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
