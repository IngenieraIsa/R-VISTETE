from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Sum, Count, Q
from .models import Publicacion, Comentario, Venta, Alquiler, Favorito, Like, Dislike
from users.models import Usuario
from django.utils import timezone
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from recommendations.recommendation_engine import RecommendationEngine
from .recommender import RecomendadorPrendas
from django.contrib import messages

#inicio - publicaciones

def inicio_view(request):
    # Debug logging
    print("Inicio view called")
    print("Session:", request.session.items())
    print("Path:", request.path)
    
    # Verificar si el usuario está autenticado
    usuario_id = request.session.get('usuario_id')
    print("Usuario ID from session:", usuario_id)
    
    if not usuario_id:
        print("No usuario_id in session, redirecting to login")
        return redirect('/usuarios/login/')
    
    try:
        # Verificar que el usuario existe
        usuario = Usuario.objects.get(id=usuario_id)
        print("Usuario encontrado:", usuario.nombre)
        
        # Obtener las publicaciones con sus comentarios
        publicaciones = Publicacion.objects.all().order_by('-fecha_publicacion')
        
        # Convertir arrays a strings para la plantilla
        for publicacion in publicaciones:
            publicacion.estilo = ", ".join(publicacion.estilo) if publicacion.estilo else "No especificado"
            publicacion.colores = ", ".join(publicacion.colores) if publicacion.colores else "No especificado"
        
        # Obtener los comentarios para cada publicación
        for publicacion in publicaciones:
            publicacion.comentarios = Comentario.objects.filter(
                publicacion=publicacion
            ).select_related('usuario').order_by('fecha_comentario')
        
        # Obtener los IDs de las publicaciones favoritas del usuario
        favoritos = Favorito.objects.filter(usuario=usuario)
        favoritos_ids = favoritos.values_list('publicacion_id', flat=True)
        
        # Obtener los IDs de las publicaciones con like del usuario
        likes = Like.objects.filter(usuario=usuario)
        likes_ids = likes.values_list('publicacion_id', flat=True)
        
        # Obtener el conteo de likes para cada publicación
        for publicacion in publicaciones:
            publicacion.likes_count = Like.objects.filter(publicacion=publicacion).count()
        
        # Obtener los dislikes del usuario actual si está autenticado
        dislikes_usuario = set()
        if request.user.is_authenticated:
            dislikes_usuario = set(Dislike.objects.filter(usuario=request.user).values_list('publicacion_id', flat=True))
        
        # Agregar conteo de dislikes a cada publicación
        for publicacion in publicaciones:
            publicacion.dislikes_count = Dislike.objects.filter(publicacion=publicacion).count()
        
        context = {
            'publicaciones': publicaciones,
            'usuario': usuario,
            'nombre_usuario': usuario.nombre,
            'favoritos': list(favoritos_ids),
            'favoritos_count': favoritos.count(),
            'likes': list(likes_ids),
            'likes_count': likes.count(),
            'dislikes_usuario': dislikes_usuario
        }
        print("Rendering inicio.html with context")
        return render(request, 'inicio.html', context)
    
    except Usuario.DoesNotExist as e:
        print("Usuario no existe en la base de datos:", str(e))
        request.session.flush()
        return redirect('/usuarios/login/')
    except Exception as e:
        print("Error inesperado:", str(e))
        request.session.flush()
        return redirect('/usuarios/login/')


#comentarios

@require_http_methods(["GET"])
def get_comentarios(request, publicacion_id):
    try:
        # Verificar si el usuario está autenticado
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
            
        # Obtener los comentarios de la publicación
        comentarios = Comentario.objects.filter(
            publicacion_id=publicacion_id
        ).select_related('usuario').order_by('-fecha_comentario')
        
        comentarios_data = []
        for comentario in comentarios:
            comentarios_data.append({
                'id': comentario.id,
                'usuario_nombre': comentario.usuario.nombre,
                'comentario': comentario.comentario,
                'fecha_comentario': comentario.fecha_comentario.strftime('%d/%m/%Y %H:%M')
            })
        
        return JsonResponse(comentarios_data, safe=False)
    except Exception as e:
        print("Error al obtener comentarios:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

#crear comentarios
@login_required
@require_http_methods(["POST"])
def crear_comentario(request):
    try:
        # Imprimir información de depuración
        print("Datos recibidos:", request.POST)
        print("Usuario:", request.user)
        
        comentario_texto = request.POST.get('comentario')
        publicacion_id = request.POST.get('publicacion_id')
        
        if not comentario_texto or not publicacion_id:
            return JsonResponse({
                'error': 'Faltan datos requeridos',
                'comentario_presente': bool(comentario_texto),
                'publicacion_presente': bool(publicacion_id)
            }, status=400)
        
        try:
            publicacion = Publicacion.objects.get(id=publicacion_id)
        except Publicacion.DoesNotExist:
            return JsonResponse({'error': 'Publicación no encontrada'}, status=404)
        
        try:
            comentario = Comentario.objects.create(
                usuario=request.user.usuario,
                publicacion=publicacion,
                comentario=comentario_texto
            )
        except Exception as e:
            print("Error al crear comentario:", str(e))
            return JsonResponse({'error': f'Error al crear el comentario: {str(e)}'}, status=500)
        
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
    except Exception as e:
        print("Error general:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

#ventas
@login_required(login_url='/users/login/')
def mis_ventas_view(request):
    try:
        # Asegurarnos de que el usuario tenga un perfil
        usuario = request.user.usuario
        
        # Obtener las publicaciones del usuario actual
        mis_publicaciones = Publicacion.objects.filter(usuario=usuario)
        
        # Obtener las ventas realizadas
        ventas = Venta.objects.filter(vendedor=usuario)
        
        # Calcular estadísticas
        estadisticas = {
            'total_publicaciones': mis_publicaciones.count(),
            'total_vendidas': ventas.filter(estado='completada').count(),
            'total_ingresos': ventas.filter(estado='completada').aggregate(Sum('precio_final'))['precio_final__sum'] or 0,
            'ventas_pendientes': ventas.filter(estado='pendiente').count(),
            'ventas_mes_actual': ventas.filter(
                estado='completada',
                fecha_venta__month=timezone.now().month,
                fecha_venta__year=timezone.now().year
            ).count()
        }

        # Filtrar publicaciones según parámetros
        estado = request.GET.get('estado')
        busqueda = request.GET.get('busqueda')

        if estado:
            if estado == 'vendida':
                mis_publicaciones = mis_publicaciones.filter(id__in=ventas.filter(estado='completada').values('publicacion_id'))
            elif estado == 'disponible':
                mis_publicaciones = mis_publicaciones.exclude(id__in=ventas.filter(estado='completada').values('publicacion_id'))

        if busqueda:
            mis_publicaciones = mis_publicaciones.filter(
                Q(titulo__icontains=busqueda) | Q(descripcion__icontains=busqueda)
            )

        # Obtener el historial de ventas para cada publicación
        publicaciones_data = []
        for pub in mis_publicaciones:
            ventas_pub = ventas.filter(publicacion=pub).order_by('-fecha_venta')
            publicaciones_data.append({
                'publicacion': pub,
                'ventas': ventas_pub,
                'total_ventas': ventas_pub.filter(estado='completada').count(),
                'ultima_venta': ventas_pub.first()
            })

        return render(request, 'mis_ventas.html', {
            'publicaciones': publicaciones_data,
            'estadisticas': estadisticas,
            'filtro_estado': estado,
            'busqueda': busqueda
        })
    except Usuario.DoesNotExist:
        # Si el usuario no tiene perfil, redirigir a completar perfil
        return redirect('completar_perfil')

#alquileres
@login_required(login_url='/users/login/')
def mis_alquileres_view(request):
    try:
        # Asegurarnos de que el usuario tenga un perfil
        usuario = request.user.usuario
        
        # Obtener las publicaciones del usuario actual
        mis_publicaciones = Publicacion.objects.filter(usuario=usuario)
        
        # Obtener los alquileres realizados
        alquileres = Alquiler.objects.filter(propietario=usuario)
        
        # Calcular estadísticas
        hoy = timezone.now().date()
        estadisticas = {
            'total_publicaciones': mis_publicaciones.count(),
            'total_alquiladas': alquileres.filter(estado='completado').count(),
            'actualmente_alquiladas': alquileres.filter(
                estado='activo',
                fecha_inicio__lte=hoy,
                fecha_fin__gte=hoy
            ).count(),
            'total_ingresos': alquileres.filter(estado='completado').aggregate(
                total=Sum('precio_por_dia')
            )['total'] or 0,
            'depositos_activos': alquileres.filter(estado='activo').aggregate(
                total=Sum('deposito')
            )['total'] or 0
        }

        # Filtrar publicaciones según parámetros
        estado = request.GET.get('estado')
        fecha_desde = request.GET.get('fecha_desde')
        busqueda = request.GET.get('busqueda')

        if estado:
            if estado == 'alquilada':
                mis_publicaciones = mis_publicaciones.filter(
                    id__in=alquileres.filter(estado='activo').values('publicacion_id')
                )
            elif estado == 'disponible':
                mis_publicaciones = mis_publicaciones.exclude(
                    id__in=alquileres.filter(estado='activo').values('publicacion_id')
                )

        # Obtener el calendario de alquileres para cada publicación
        publicaciones_data = []
        for pub in mis_publicaciones:
            alquileres_pub = alquileres.filter(publicacion=pub).order_by('fecha_inicio')
            proximos_alquileres = alquileres_pub.filter(
                Q(estado='reservado') | Q(estado='activo'),
                fecha_fin__gte=hoy
            )
            publicaciones_data.append({
                'publicacion': pub,
                'alquileres': alquileres_pub,
                'proximos_alquileres': proximos_alquileres,
                'disponible': not proximos_alquileres.filter(
                    fecha_inicio__lte=hoy,
                    fecha_fin__gte=hoy
                ).exists()
            })

        return render(request, 'mis_alquileres.html', {
            'publicaciones': publicaciones_data,
            'estadisticas': estadisticas,
            'filtro_estado': estado,
            'fecha_desde': fecha_desde,
            'busqueda': busqueda
        })
    except Usuario.DoesNotExist:
        # Si el usuario no tiene perfil, redirigir a completar perfil
        return redirect('completar_perfil')

#notificaciones
@login_required
def notificaciones_view(request):
    try:
        # Obtener recomendaciones personalizadas
        recomendador = RecomendadorPrendas(request.user.id)
        recomendaciones = recomendador.generar_recomendaciones(limit=5)
        
        context = {
            'recomendaciones': recomendaciones,
        }
        return render(request, 'posts/notificaciones.html', context)
    except Exception as e:
        context = {
            'error': 'No se pudieron cargar las recomendaciones en este momento.',
            'recomendaciones': []
        }
        return render(request, 'posts/notificaciones.html', context)


#favoritos
@require_http_methods(["POST"])
def toggle_favorito(request, publicacion_id):
    try:
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
            
        usuario = Usuario.objects.get(id=usuario_id)
        publicacion = Publicacion.objects.get(id=publicacion_id)
        
        # Verificar si ya existe el favorito
        favorito = Favorito.objects.filter(usuario=usuario, publicacion=publicacion).first()
        
        if favorito:
            # Si existe, lo eliminamos
            favorito.delete()
            favoritos_count = Favorito.objects.filter(usuario=usuario).count()
            return JsonResponse({
                'status': 'removed',
                'message': 'Eliminado de favoritos',
                'favoritos_count': favoritos_count
            })
        else:
            # Si no existe, lo creamos
            Favorito.objects.create(usuario=usuario, publicacion=publicacion)
            favoritos_count = Favorito.objects.filter(usuario=usuario).count()
            return JsonResponse({
                'status': 'added',
                'message': 'Agregado a favoritos',
                'favoritos_count': favoritos_count
            })
            
    except Publicacion.DoesNotExist:
        return JsonResponse({'error': 'Publicación no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

#ver favoritos
def ver_favoritos(request):
    # Verificar si el usuario está autenticado
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('/usuarios/login/')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        # Obtener todos los favoritos del usuario
        favoritos = Favorito.objects.filter(usuario=usuario).select_related('publicacion')
        
        context = {
            'favoritos': favoritos,
            'usuario': usuario,
            'nombre_usuario': usuario.nombre,
            'favoritos_count': favoritos.count()
        }
        return render(request, 'favoritos.html', context)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('/usuarios/login/')

#likes
@require_http_methods(["POST"])
def toggle_like(request, publicacion_id):
    try:
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
            
        usuario = Usuario.objects.get(id=usuario_id)
        publicacion = Publicacion.objects.get(id=publicacion_id)
        
        # Verificar si ya existe el like
        like = Like.objects.filter(usuario=usuario, publicacion=publicacion).first()
        
        if like:
            # Si existe, lo eliminamos
            like.delete()
            likes_count = Like.objects.filter(publicacion=publicacion).count()
            user_likes_count = Like.objects.filter(usuario=usuario).count()
            return JsonResponse({
                'status': 'removed',
                'message': 'Like removido',
                'likes_count': likes_count,
                'user_likes_count': user_likes_count
            })
        else:
            # Si no existe, lo creamos
            Like.objects.create(usuario=usuario, publicacion=publicacion)
            likes_count = Like.objects.filter(publicacion=publicacion).count()
            user_likes_count = Like.objects.filter(usuario=usuario).count()
            return JsonResponse({
                'status': 'added',
                'message': 'Like agregado',
                'likes_count': likes_count,
                'user_likes_count': user_likes_count
            })
            
    except Publicacion.DoesNotExist:
        return JsonResponse({'error': 'Publicación no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

#ver likes
def ver_likes(request):
    # Verificar si el usuario está autenticado
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('/usuarios/login/')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        # Obtener todas las publicaciones que el usuario ha dado like
        likes = Like.objects.filter(usuario=usuario).select_related('publicacion')
        
        context = {
            'likes': likes,
            'usuario': usuario,
            'nombre_usuario': usuario.nombre,
            'likes_count': likes.count()
        }
        return render(request, 'likes.html', context)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('/usuarios/login/')

#agregar comentarios a las publicaciones
@require_http_methods(["POST"])
def agregar_comentario(request, publicacion_id):
    try:
        # Verificar si el usuario está autenticado
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
            
        # Obtener el usuario y la publicación
        usuario = Usuario.objects.get(id=usuario_id)
        publicacion = Publicacion.objects.get(id=publicacion_id)
        
        # Obtener el comentario del cuerpo de la petición
        data = json.loads(request.body)
        comentario_texto = data.get('comentario')
        
        if not comentario_texto:
            return JsonResponse({'error': 'El comentario no puede estar vacío'}, status=400)
            
        # Crear el comentario
        comentario = Comentario.objects.create(
            usuario=usuario,
            publicacion=publicacion,
            comentario=comentario_texto
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Comentario agregado',
            'usuario_nombre': usuario.nombre,
            'comentario': comentario_texto,
            'fecha': comentario.fecha_comentario.strftime('%d/%m/%Y %H:%M')
        })
            
    except Publicacion.DoesNotExist:
        return JsonResponse({'error': 'Publicación no encontrada'}, status=404)
    except Exception as e:
        print("Error al agregar comentario:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

#publicar prendas
@login_required
def publicar_prenda(request):
    if request.method == 'POST':
        try:
            # Obtener el usuario de la sesión
            usuario_id = request.session.get('usuario_id')
            if not usuario_id:
                messages.error(request, 'Usuario no autenticado')
                return redirect('login')

            # Obtener datos del formulario
            titulo = request.POST.get('titulo')
            descripcion = request.POST.get('descripcion')
            tipo = request.POST.get('tipo')
            precio = request.POST.get('precio')
            deposito = request.POST.get('deposito') if tipo == 'alquiler' else None
            publico = request.POST.get('publico')
            talla = request.POST.get('talla')
            estilos = request.POST.getlist('estilo[]')
            colores = request.POST.getlist('colores[]')

            # Validar campos requeridos
            if not all([titulo, tipo, precio, publico, talla, estilos, colores]):
                messages.error(request, 'Por favor completa todos los campos obligatorios')
                return redirect('publicar')

            # Procesar imagen si se proporcionó
            imagen_url = None
            if 'imagen' in request.FILES:
                imagen = request.FILES['imagen']
                # Guardar la imagen y obtener la URL
                path = default_storage.save(f'prendas/{imagen.name}', ContentFile(imagen.read()))
                imagen_url = default_storage.url(path)

            # Crear la publicación
            publicacion = Publicacion.objects.create(
                usuario_id=usuario_id,
                titulo=titulo,
                descripcion=descripcion,
                imagen_url=imagen_url,
                precio=precio,
                tipo=tipo,
                deposito=deposito,
                publico=publico,
                talla=talla,
                estilo=estilos,
                colores=colores
            )

            messages.success(request, 'Publicación creada exitosamente')
            return redirect('inicio')

        except Exception as e:
            messages.error(request, f'Error al crear la publicación: {str(e)}')
            return redirect('publicar')

    return render(request, 'posts/publicar.html')

#ver publicaciones
@login_required
def ver_publicacion(request, publicacion_id):
    try:
        # Obtener la publicación
        publicacion = Publicacion.objects.get(id=publicacion_id)
        
        # Verificar si el usuario ha dado like
        usuario_id = request.session.get('usuario_id')
        tiene_like = Like.objects.filter(usuario_id=usuario_id, publicacion=publicacion).exists()
        tiene_favorito = Favorito.objects.filter(usuario_id=usuario_id, publicacion=publicacion).exists()
        
        # Obtener comentarios
        comentarios = Comentario.objects.filter(publicacion=publicacion).order_by('-fecha_comentario')
        
        context = {
            'publicacion': publicacion,
            'tiene_like': tiene_like,
            'tiene_favorito': tiene_favorito,
            'comentarios': comentarios,
        }
        
        return render(request, 'posts/ver_publicacion.html', context)
    except Publicacion.DoesNotExist:
        return redirect('inicio')

@login_required
def recomendaciones_view(request):
    try:
        usuario = request.user.usuario
        engine = RecommendationEngine(usuario)
        
        # Obtener recomendaciones
        recomendaciones = engine.generar_recomendaciones()
        
        # Obtener análisis de preferencias
        preferencias = engine.analizar_preferencias_usuario()
        interacciones = engine.analizar_interacciones()
        sentimiento = engine.analizar_sentimiento_descripcion()
        
        context = {
            'recomendaciones': recomendaciones,
            'preferencias': preferencias,
            'interacciones': interacciones,
            'sentimiento': sentimiento,
            'usuario': usuario
        }
        
        return render(request, 'recomendaciones.html', context)
    except Exception as e:
        print(f"Error al generar recomendaciones: {str(e)}")
        return redirect('inicio')

@login_required
def toggle_dislike(request, publicacion_id):
    try:
        # Obtener el usuario actual y la publicación
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=401)
            
        usuario = Usuario.objects.get(id=usuario_id)
        publicacion = get_object_or_404(Publicacion, id=publicacion_id)
        
        # Verificar si ya existe un dislike
        dislike = Dislike.objects.filter(usuario=usuario, publicacion=publicacion).first()
        
        if dislike:
            # Si ya existe un dislike, lo eliminamos
            dislike.delete()
            is_disliked = False
        else:
            # Si no existe, primero eliminamos cualquier like existente
            Like.objects.filter(usuario=usuario, publicacion=publicacion).delete()
            # Luego creamos el nuevo dislike
            Dislike.objects.create(usuario=usuario, publicacion=publicacion)
            is_disliked = True
        
        # Obtener el nuevo conteo de dislikes
        dislikes_count = Dislike.objects.filter(publicacion=publicacion).count()
        
        return JsonResponse({
            'success': True,
            'is_disliked': is_disliked,
            'dislikes_count': dislikes_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

#ver dislikes
def ver_dislikes(request):
    # Verificar si el usuario está autenticado
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('/usuarios/login/')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        # Obtener todas las publicaciones que el usuario ha dado dislike
        dislikes = Dislike.objects.filter(usuario=usuario).select_related('publicacion')
        
        context = {
            'dislikes': dislikes,
            'usuario': usuario,
            'nombre_usuario': usuario.nombre,
            'dislikes_count': dislikes.count()
        }
        return render(request, 'posts/dislikes.html', context)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('/usuarios/login/')

@login_required
def obtener_recomendaciones(request):
    """Vista para obtener recomendaciones personalizadas"""
    recomendador = RecomendadorPrendas(request.user.id)
    recomendaciones = recomendador.generar_recomendaciones()
    
    # Si las recomendaciones son un queryset (caso sin perfil)
    if hasattr(recomendaciones, 'model'):
        return JsonResponse({
            'recomendaciones': [
                {
                    'id': pub.id,
                    'titulo': pub.titulo,
                    'imagen_url': pub.imagen_url,
                    'precio': pub.precio,
                    'score': 0,
                    'razones': ['Publicación reciente que podría interesarte']
                } for pub in recomendaciones
            ]
        })
    
    # Si son recomendaciones con score
    return JsonResponse({
        'recomendaciones': [
            {
                'id': rec['publicacion'].id,
                'titulo': rec['publicacion'].titulo,
                'imagen_url': rec['publicacion'].imagen_url,
                'precio': rec['publicacion'].precio,
                'score': rec['score'],
                'razones': rec['razones']
            } for rec in recomendaciones[:10]  # Limitamos a 10 recomendaciones
        ]
    })
