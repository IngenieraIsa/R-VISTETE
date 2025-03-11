from django.db import models
from users.models import Usuario  # ✅ Ahora sí podemos importar

class Publicacion(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='usuario_id')
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(null=True)
    imagen_url = models.TextField(null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=10, default='venta', choices=[('venta', 'Venta'), ('alquiler', 'Alquiler')])
    deposito = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        db_table = 'publicaciones'  # 🔗 Conectar con la tabla en PostgreSQL
        ordering = ['-fecha_publicacion']  # Ordenar por fecha más reciente

    def __str__(self):
        return f"{self.titulo} - {self.usuario.nombre}"

class Compra(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='usuario_id')
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, db_column='publicacion_id')
    fecha_compra = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'compras'

    def __str__(self):
        return f"Compra de {self.publicacion.titulo} por {self.usuario.nombre}"

class Like(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='usuario_id')
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, db_column='publicacion_id')
    fecha_like = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'likes'

    def __str__(self):
        return f"Like de {self.usuario.nombre} en {self.publicacion.titulo}"

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

class Venta(models.Model):
    id = models.AutoField(primary_key=True)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, db_column='publicacion_id')
    vendedor = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='vendedor_id', related_name='ventas_realizadas')
    comprador = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='comprador_id', related_name='compras_realizadas')
    precio_final = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada')
    ], default='pendiente')
    metodo_pago = models.CharField(max_length=50)
    direccion_envio = models.TextField()
    notas = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ventas'
        ordering = ['-fecha_venta']

    def __str__(self):
        return f"Venta de {self.publicacion.titulo} a {self.comprador.nombre}"

class Alquiler(models.Model):
    id = models.AutoField(primary_key=True)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, db_column='publicacion_id')
    propietario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='propietario_id', related_name='alquileres_realizados')
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='cliente_id', related_name='prendas_alquiladas')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    precio_por_dia = models.DecimalField(max_digits=10, decimal_places=2)
    deposito = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=[
        ('reservado', 'Reservado'),
        ('activo', 'Activo'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado')
    ], default='reservado')
    metodo_pago = models.CharField(max_length=50)
    direccion_envio = models.TextField()
    notas = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'alquileres'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"Alquiler de {self.publicacion.titulo} a {self.cliente.nombre}"

    def save(self, *args, **kwargs):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")
        super().save(*args, **kwargs)

class Favorito(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='usuario_id')
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, db_column='publicacion_id')
    fecha_favorito = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favoritos'
        unique_together = ('usuario', 'publicacion')
        ordering = ['-fecha_favorito']

    def __str__(self):
        return f"Favorito de {self.usuario.nombre} - {self.publicacion.titulo}"
