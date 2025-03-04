from django.db import models

class Usuario(models.Model):
    id = models.AutoField(primary_key=True)  
    nombre = models.CharField(max_length=255)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=255)  # Encriptar en el futuro
    fecha_registro = models.DateTimeField(auto_now_add=True)
    foto_perfil = models.TextField(null=True, blank=True, default='https://i.pinimg.com/564x/19/b8/d6/19b8d6e9b13eef23ec9c746968bb88b1.jpg')  # URL de avatar por defecto

    class Meta:
        db_table = 'usuarios' 

    def __str__(self):
        return self.nombre

