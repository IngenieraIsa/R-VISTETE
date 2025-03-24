from collections import Counter
from django.db.models import Q
from ..models import Publicacion, PerfilUsuario, Like, Favorito

class RecomendadorPrendas:
    def __init__(self, usuario_id):
        self.usuario_id = usuario_id
        self.perfil = self.analizar_perfil_usuario(usuario_id)
        self.patrones_interaccion = self.analizar_interacciones_publicaciones(usuario_id)
    
    def analizar_perfil_usuario(self, usuario_id):
        """Analiza el perfil del usuario para obtener sus preferencias explícitas"""
        try:
            perfil = PerfilUsuario.objects.get(usuario_id=usuario_id)
            return {
                'preferencias_explicitas': {
                    'talla': perfil.talla,
                    'estilos': perfil.estilos_preferidos,
                    'colores': perfil.colores_preferidos,
                    'ocasiones': perfil.ocasiones_uso,
                    'intereses': perfil.intereses
                },
                'ubicacion': perfil.ubicacion,
                'peso_perfil': 0.8
            }
        except PerfilUsuario.DoesNotExist:
            return None

    def analizar_interacciones_publicaciones(self, usuario_id):
        """Analiza las publicaciones con las que el usuario ha interactuado"""
        publicaciones_likes = Publicacion.objects.filter(
            id__in=Like.objects.filter(usuario_id=usuario_id).values_list('publicacion_id', flat=True)
        )
        
        publicaciones_favoritos = Publicacion.objects.filter(
            id__in=Favorito.objects.filter(usuario_id=usuario_id).values_list('publicacion_id', flat=True)
        )
        
        return {
            'estilos_preferidos': self.analizar_frecuencia_estilos(publicaciones_likes, publicaciones_favoritos),
            'colores_preferidos': self.analizar_frecuencia_colores(publicaciones_likes, publicaciones_favoritos),
            'rango_precios': self.calcular_rango_precios(publicaciones_likes, publicaciones_favoritos),
            'tallas_comunes': self.analizar_tallas_preferidas(publicaciones_likes, publicaciones_favoritos),
            'tipos_preferidos': self.analizar_tipos_prendas(publicaciones_likes, publicaciones_favoritos)
        }

    def analizar_frecuencia_estilos(self, publicaciones_likes, publicaciones_favoritos):
        """Analiza la frecuencia de estilos en las interacciones del usuario"""
        todos_estilos = []
        for pub in publicaciones_likes:
            todos_estilos.extend(pub.estilo)
        for pub in publicaciones_favoritos:
            todos_estilos.extend(pub.estilo)
        return Counter(todos_estilos).most_common()

    def analizar_frecuencia_colores(self, publicaciones_likes, publicaciones_favoritos):
        """Analiza la frecuencia de colores en las interacciones del usuario"""
        todos_colores = []
        for pub in publicaciones_likes:
            todos_colores.extend(pub.colores)
        for pub in publicaciones_favoritos:
            todos_colores.extend(pub.colores)
        return Counter(todos_colores).most_common()

    def calcular_rango_precios(self, publicaciones_likes, publicaciones_favoritos):
        """Calcula el rango de precios preferido basado en las interacciones"""
        precios = []
        for pub in publicaciones_likes:
            precios.append(pub.precio)
        for pub in publicaciones_favoritos:
            precios.append(pub.precio)
        
        if not precios:
            return None
            
        return {
            'min': min(precios),
            'max': max(precios),
            'avg': sum(precios) / len(precios)
        }

    def analizar_tallas_preferidas(self, publicaciones_likes, publicaciones_favoritos):
        """Analiza las tallas más frecuentes en las interacciones"""
        tallas = []
        for pub in publicaciones_likes:
            tallas.append(pub.talla)
        for pub in publicaciones_favoritos:
            tallas.append(pub.talla)
        return Counter(tallas).most_common()

    def analizar_tipos_prendas(self, publicaciones_likes, publicaciones_favoritos):
        """Analiza los tipos de prendas más frecuentes en las interacciones"""
        tipos = []
        for pub in publicaciones_likes:
            tipos.append(pub.tipo)
        for pub in publicaciones_favoritos:
            tipos.append(pub.tipo)
        return Counter(tipos).most_common()

    def precio_en_rango_preferido(self, precio):
        """Verifica si un precio está en el rango preferido del usuario"""
        if not self.patrones_interaccion.get('rango_precios'):
            return True
        
        rango = self.patrones_interaccion['rango_precios']
        margen = (rango['max'] - rango['min']) * 0.2  # 20% de margen
        return rango['min'] - margen <= precio <= rango['max'] + margen

    def calcular_score_relevancia(self, publicacion):
        """Calcula el score de relevancia para una publicación"""
        score = 0
        
        # Coincidencia de talla
        if self.perfil and publicacion.talla == self.perfil['preferencias_explicitas']['talla']:
            score += 0.3
        
        # Coincidencia de estilos
        if self.perfil:
            estilos_comunes = set(publicacion.estilo) & set(self.perfil['preferencias_explicitas']['estilos'])
            score += len(estilos_comunes) * 0.2
        
        # Coincidencia de colores
        if self.perfil:
            colores_comunes = set(publicacion.colores) & set(self.perfil['preferencias_explicitas']['colores'])
            score += len(colores_comunes) * 0.2
        
        # Rango de precio similar
        if self.precio_en_rango_preferido(publicacion.precio):
            score += 0.15
        
        # Tipo de prenda preferido
        tipos_preferidos = [tipo for tipo, _ in self.patrones_interaccion.get('tipos_preferidos', [])]
        if publicacion.tipo in tipos_preferidos:
            score += 0.15
            
        return score

    def generar_razones_recomendacion(self, publicacion):
        """Genera las razones por las que se recomienda una publicación"""
        razones = []
        
        if self.perfil:
            if publicacion.talla == self.perfil['preferencias_explicitas']['talla']:
                razones.append(f"Talla {publicacion.talla} que coincide con tu preferencia")
            
            estilos_comunes = set(publicacion.estilo) & set(self.perfil['preferencias_explicitas']['estilos'])
            if estilos_comunes:
                razones.append(f"Estilos que te gustan: {', '.join(estilos_comunes)}")
            
            colores_comunes = set(publicacion.colores) & set(self.perfil['preferencias_explicitas']['colores'])
            if colores_comunes:
                razones.append(f"Colores que prefieres: {', '.join(colores_comunes)}")
        
        return razones

    def generar_recomendaciones(self):
        """Genera las recomendaciones para el usuario"""
        if not self.perfil:
            # Si no hay perfil, recomendar las publicaciones más recientes
            return Publicacion.objects.filter(
                publico=True
            ).exclude(
                usuario_id=self.usuario_id
            ).order_by('-fecha_publicacion')[:10]

        # Construir query de recomendaciones
        recomendaciones = Publicacion.objects.filter(
            Q(publico=True) &
            (Q(talla=self.perfil['preferencias_explicitas']['talla']) |
            Q(estilo__overlap=self.perfil['preferencias_explicitas']['estilos']) |
            Q(colores__overlap=self.perfil['preferencias_explicitas']['colores']))
        ).exclude(
            usuario_id=self.usuario_id
        )
        
        # Calcular score de relevancia para cada publicación
        recomendaciones_con_score = []
        for pub in recomendaciones:
            score = self.calcular_score_relevancia(pub)
            recomendaciones_con_score.append({
                'publicacion': pub,
                'score': score,
                'razones': self.generar_razones_recomendacion(pub)
            })
        
        # Ordenar por score de relevancia
        return sorted(recomendaciones_con_score, key=lambda x: x['score'], reverse=True) 