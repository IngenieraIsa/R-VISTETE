# Generated by Django 5.1.2 on 2025-03-22 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='perfilusuario',
            name='marcas_favoritas',
        ),
        migrations.RemoveField(
            model_name='perfilusuario',
            name='rango_precio_preferido',
        ),
        migrations.AlterField(
            model_name='perfilusuario',
            name='colores_preferidos',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='perfilusuario',
            name='estilos_preferidos',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='perfilusuario',
            name='intereses',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='perfilusuario',
            name='ocasiones_uso',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
