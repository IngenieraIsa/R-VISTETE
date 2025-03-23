# Generated by Django 5.1.2 on 2025-03-23 01:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_publicacion_colores_publicacion_estilo_and_more'),
        ('users', '0002_remove_perfilusuario_marcas_favoritas_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dislike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_dislike', models.DateTimeField(auto_now_add=True)),
                ('publicacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='posts.publicacion')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.usuario')),
            ],
            options={
                'db_table': 'dislikes',
                'unique_together': {('usuario', 'publicacion')},
            },
        ),
    ]
