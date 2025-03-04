from django.db import models
from users.models import Usuario  # ✅ Ahora sí podemos importar

class Publicacion(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='usuario_id')  
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    imagen_url = models.TextField()  # Volvemos a usar imagen_url para coincidir con la base de datos
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'publicaciones'  # 🔗 Conectar con la tabla en PostgreSQL
        ordering = ['-fecha_publicacion']  # Ordenar por fecha más reciente

    def __str__(self):
        return f"{self.titulo} - {self.usuario.nombre}"

class Comentario(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='usuario_id')
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, db_column='publicacion_id')
    comentario = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comentarios'  # 🔗 Conectar con la tabla en PostgreSQL
        ordering = ['-fecha_comentario']

    def __str__(self):
        return f"Comentario de {self.usuario.nombre} en {self.publicacion.titulo}"
