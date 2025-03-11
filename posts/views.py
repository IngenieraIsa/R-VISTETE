from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Sum, Count, Q
from .models import Publicacion, Comentario, Venta, Alquiler, Favorito
from users.models import Usuario
from django.utils import timezone
import json

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
        
        # Obtener las publicaciones
        publicaciones = Publicacion.objects.all().order_by('-fecha_publicacion')
        
        # Obtener los IDs de las publicaciones favoritas del usuario
        favoritos = Favorito.objects.filter(usuario=usuario)
        favoritos_ids = favoritos.values_list('publicacion_id', flat=True)
        
        context = {
            'publicaciones': publicaciones,
            'usuario': usuario,
            'nombre_usuario': usuario.nombre,
            'favoritos': list(favoritos_ids),
            'favoritos_count': favoritos.count()
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

@login_required
def get_comentarios(request, publicacion_id):
    try:
        comentarios = Comentario.objects.filter(publicacion_id=publicacion_id).order_by('-fecha_comentario')
        comentarios_data = []
        
        for comentario in comentarios:
            comentarios_data.append({
                'id': comentario.id,
                'usuario_nombre': f"{comentario.usuario.nombre} {comentario.usuario.apellido}",
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

@login_required
def notificaciones_view(request):
    # Por ahora, solo renderizamos la plantilla con un mensaje
    # En el futuro, aquí cargaremos las notificaciones de la base de datos
    context = {
        'notificaciones': []  # Lista vacía por ahora
    }
    return render(request, 'notificaciones.html', context)

@require_http_methods(["POST"])
def toggle_favorito(request, publicacion_id):
    try:
        # Obtener el usuario y la publicación
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
            return JsonResponse({
                'status': 'removed',
                'message': 'Eliminado de favoritos'
            })
        else:
            # Si no existe, lo creamos
            Favorito.objects.create(usuario=usuario, publicacion=publicacion)
            return JsonResponse({
                'status': 'added',
                'message': 'Agregado a favoritos'
            })
            
    except Publicacion.DoesNotExist:
        return JsonResponse({'error': 'Publicación no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
