from textblob import TextBlob
from collections import Counter
from django.db.models import Q
import numpy as np

class SentimentAnalyzer:
    def __init__(self, usuario_id):
        self.usuario_id = usuario_id
        self.likes = []
        self.favoritos = []
        self.comentarios = []
        self.preferencias = {
            'publico': Counter(),
            'estilos': Counter(),
            'colores': Counter(),
            'tallas': Counter()
        }
        self.sentiment_scores = {}

    def analizar_likes(self, likes_queryset):
        """Analiza los patrones en las publicaciones que el usuario ha dado like"""
        for like in likes_queryset:
            pub = like.publicacion
            self.likes.append(pub)
            self._actualizar_preferencias(pub)

    def analizar_favoritos(self, favoritos_queryset):
        """Analiza los patrones en las publicaciones que el usuario ha marcado como favoritos"""
        for fav in favoritos_queryset:
            pub = fav.publicacion
            self.favoritos.append(pub)
            self._actualizar_preferencias(pub, peso=1.5)  # Damos más peso a los favoritos

    def analizar_comentarios(self, comentarios_queryset):
        """Analiza el sentimiento de los comentarios del usuario en las publicaciones"""
        for comentario in comentarios_queryset:
            pub = comentario.publicacion
            self.comentarios.append(pub)
            
            # Análisis de sentimiento del comentario
            blob = TextBlob(comentario.comentario)
            sentiment = blob.sentiment.polarity
            
            # Guardamos el score de sentimiento
            if pub.id not in self.sentiment_scores:
                self.sentiment_scores[pub.id] = []
            self.sentiment_scores[pub.id].append(sentiment)
            
            # Si el comentario es positivo, actualizamos preferencias
            if sentiment > 0:
                self._actualizar_preferencias(pub, peso=1 + sentiment)

    def _actualizar_preferencias(self, publicacion, peso=1.0):
        """Actualiza los contadores de preferencias basado en una publicación"""
        self.preferencias['publico'][publicacion.publico] += peso
        for estilo in publicacion.estilo:
            self.preferencias['estilos'][estilo] += peso
        for color in publicacion.colores:
            self.preferencias['colores'][color] += peso
        self.preferencias['tallas'][publicacion.talla] += peso

    def obtener_score_relevancia(self, publicacion):
        """Calcula qué tan relevante es una publicación para el usuario"""
        score = 0.0
        
        # Score basado en público objetivo
        if publicacion.publico in self.preferencias['publico']:
            score += self.preferencias['publico'][publicacion.publico] * 0.25

        # Score basado en estilos
        for estilo in publicacion.estilo:
            if estilo in self.preferencias['estilos']:
                score += self.preferencias['estilos'][estilo] * 0.25

        # Score basado en colores
        for color in publicacion.colores:
            if color in self.preferencias['colores']:
                score += self.preferencias['colores'][color] * 0.25

        # Score basado en talla
        if publicacion.talla in self.preferencias['tallas']:
            score += self.preferencias['tallas'][publicacion.talla] * 0.25

        return score

    def generar_recomendaciones(self, publicaciones_queryset, limit=10):
        """Genera recomendaciones basadas en las preferencias del usuario"""
        recomendaciones = []
        
        for pub in publicaciones_queryset:
            # No recomendamos publicaciones que ya tienen interacción
            if pub in self.likes or pub in self.favoritos:
                continue
                
            score = self.obtener_score_relevancia(pub)
            if score > 0:
                recomendaciones.append((pub, score))
        
        # Ordenamos por score y retornamos las top N recomendaciones
        recomendaciones.sort(key=lambda x: x[1], reverse=True)
        return recomendaciones[:limit]

    def obtener_razones_recomendacion(self, publicacion):
        """Genera explicaciones de por qué se recomienda una publicación"""
        razones = []
        
        if publicacion.publico in self.preferencias['publico']:
            razones.append(f"Te gustan las prendas para {publicacion.publico}")
            
        estilos_comunes = set(publicacion.estilo) & set(self.preferencias['estilos'].keys())
        if estilos_comunes:
            razones.append(f"Coincide con tus estilos preferidos: {', '.join(estilos_comunes)}")
            
        colores_comunes = set(publicacion.colores) & set(self.preferencias['colores'].keys())
        if colores_comunes:
            razones.append(f"Usa colores que te gustan: {', '.join(colores_comunes)}")
            
        if publicacion.talla in self.preferencias['tallas']:
            razones.append(f"Es de tu talla preferida: {publicacion.talla}")
            
        return razones 