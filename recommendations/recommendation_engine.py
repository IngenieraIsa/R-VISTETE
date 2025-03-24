from textblob import TextBlob
from django.db.models import Count, Avg
from posts.models import Publicacion, Like, Favorito
from users.models import Usuario
import numpy as np

class RecommendationEngine:
    def __init__(self, usuario):
        self.usuario = usuario
        self.likes = Like.objects.filter(usuario=usuario)
        self.favoritos = Favorito.objects.filter(usuario=usuario)

    def analizar_preferencias_usuario(self):
        """Analiza las preferencias del usuario basado en su perfil"""
        preferencias = {
            'estilos': set(self.usuario.estilos_preferidos) if self.usuario.estilos_preferidos else set(),
            'colores': set(self.usuario.colores_preferidos) if self.usuario.colores_preferidos else set(),
            'talla': self.usuario.talla,
            'rango_precios': {
                'min': self.usuario.rango_precio_min,
                'max': self.usuario.rango_precio_max
            },
            'ocasiones': set(self.usuario.ocasiones_uso) if self.usuario.ocasiones_uso else set()
        }
        return preferencias

    def analizar_interacciones(self):
        """Analiza las publicaciones con las que el usuario ha interactuado"""
        publicaciones_liked = Publicacion.objects.filter(like__usuario=self.usuario)
        publicaciones_favoritas = Publicacion.objects.filter(favorito__usuario=self.usuario)

        interacciones = {
            'estilos_preferidos': self._contar_frecuencia(publicaciones_liked, 'estilo'),
            'colores_preferidos': self._contar_frecuencia(publicaciones_liked, 'colores'),
            'rango_precios': self._analizar_rango_precios(publicaciones_liked),
            'tallas_preferidas': self._contar_frecuencia(publicaciones_liked, 'talla')
        }
        return interacciones

    def _contar_frecuencia(self, queryset, campo):
        """Cuenta la frecuencia de valores en un campo específico"""
        frecuencias = {}
        for pub in queryset:
            valores = getattr(pub, campo)
            if isinstance(valores, list):
                for valor in valores:
                    frecuencias[valor] = frecuencias.get(valor, 0) + 1
            else:
                frecuencias[valores] = frecuencias.get(valores, 0) + 1
        return dict(sorted(frecuencias.items(), key=lambda x: x[1], reverse=True))

    def _analizar_rango_precios(self, queryset):
        """Analiza el rango de precios de las publicaciones con las que interactúa el usuario"""
        precios = queryset.values_list('precio', flat=True)
        if not precios:
            return {'min': 0, 'max': 0, 'avg': 0}
        return {
            'min': min(precios),
            'max': max(precios),
            'avg': sum(precios) / len(precios)
        }

    def analizar_sentimiento_descripcion(self):
        """Analiza el sentimiento de la descripción del usuario"""
        if not self.usuario.descripcion:
            return {'polaridad': 0, 'subjetividad': 0}
        
        blob = TextBlob(self.usuario.descripcion)
        return {
            'polaridad': blob.sentiment.polarity,
            'subjetividad': blob.sentiment.subjectivity
        }

    def generar_recomendaciones(self):
        """Genera recomendaciones basadas en todos los análisis"""
        preferencias = self.analizar_preferencias_usuario()
        interacciones = self.analizar_interacciones()
        sentimiento = self.analizar_sentimiento_descripcion()

        # Obtener publicaciones que coincidan con las preferencias
        recomendaciones = Publicacion.objects.all()

        # Filtrar por estilos preferidos
        if preferencias['estilos']:
            recomendaciones = recomendaciones.filter(estilo__overlap=list(preferencias['estilos']))

        # Filtrar por colores preferidos
        if preferencias['colores']:
            recomendaciones = recomendaciones.filter(colores__overlap=list(preferencias['colores']))

        # Filtrar por talla
        if preferencias['talla']:
            recomendaciones = recomendaciones.filter(talla=preferencias['talla'])

        # Filtrar por rango de precios
        if preferencias['rango_precios']['max']:
            recomendaciones = recomendaciones.filter(
                precio__gte=preferencias['rango_precios']['min'],
                precio__lte=preferencias['rango_precios']['max']
            )

        # Excluir publicaciones que ya tienen like o están en favoritos
        recomendaciones = recomendaciones.exclude(
            id__in=self.likes.values_list('publicacion_id', flat=True)
        ).exclude(
            id__in=self.favoritos.values_list('publicacion_id', flat=True)
        )

        # Ordenar por relevancia (aquí puedes implementar tu propia lógica de scoring)
        recomendaciones = recomendaciones.order_by('-fecha_publicacion')[:10]

        return list(recomendaciones)

    def calcular_score_publicacion(self, publicacion):
        """Calcula un score de relevancia para una publicación específica"""
        score = 0
        preferencias = self.analizar_preferencias_usuario()
        
        # Puntos por coincidencia de estilo
        estilos_coincidentes = set(publicacion.estilo) & preferencias['estilos']
        score += len(estilos_coincidentes) * 2

        # Puntos por coincidencia de colores
        colores_coincidentes = set(publicacion.colores) & preferencias['colores']
        score += len(colores_coincidentes)

        # Puntos por talla
        if publicacion.talla == preferencias['talla']:
            score += 3

        # Puntos por rango de precio
        if (preferencias['rango_precios']['min'] <= publicacion.precio <= 
            preferencias['rango_precios']['max']):
            score += 2

        return score 