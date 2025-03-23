from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, null=True, blank=True)
    correo = models.CharField(max_length=150, unique=True)
    contrasena = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return f"{self.nombre} {self.apellido if self.apellido else ''}"

class PerfilUsuario(models.Model):
    TALLAS = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL')
    ]

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil')
    descripcion = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=50, null=True, blank=True)
    ubicacion = models.CharField(max_length=200, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    redes_sociales = models.JSONField(null=True, blank=True)
    intereses = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Nuevos campos para preferencias de moda
    talla = models.CharField(max_length=3, choices=TALLAS, null=True, blank=True)
    estilos_preferidos = ArrayField(
        models.CharField(max_length=50),
        null=True,
        blank=True
    )
    colores_preferidos = ArrayField(
        models.CharField(max_length=7),  # Para códigos de color hex
        null=True,
        blank=True
    )
    rango_precio_preferido = models.CharField(max_length=20, null=True, blank=True)
    marcas_favoritas = ArrayField(
        models.CharField(max_length=100),
        null=True,
        blank=True
    )
    ocasiones_uso = ArrayField(
        models.CharField(max_length=100),
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'perfiles_usuario'

    def __str__(self):
        return f"Perfil de {self.usuario.nombre}"

