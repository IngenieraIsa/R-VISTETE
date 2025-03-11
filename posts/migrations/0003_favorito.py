# Generated by Django 5.1.2 on 2025-03-11 01:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_publicacion_deposito_publicacion_tipo_and_more'),
        ('users', '0002_remove_usuario_foto_perfil_remove_usuario_user_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorito',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_favorito', models.DateTimeField(auto_now_add=True)),
                ('publicacion', models.ForeignKey(db_column='publicacion_id', on_delete=django.db.models.deletion.CASCADE, to='posts.publicacion')),
                ('usuario', models.ForeignKey(db_column='usuario_id', on_delete=django.db.models.deletion.CASCADE, to='users.usuario')),
            ],
            options={
                'db_table': 'favoritos',
                'ordering': ['-fecha_favorito'],
                'unique_together': {('usuario', 'publicacion')},
            },
        ),
    ]
