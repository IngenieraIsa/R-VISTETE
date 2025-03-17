from django import forms
from .models import PerfilUsuario
import json

class PerfilForm(forms.ModelForm):
    TALLAS = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL')
    ]

    ESTILOS = [
        ('casual', 'Casual'),
        ('formal', 'Formal'),
        ('deportivo', 'Deportivo'),
        ('elegante', 'Elegante'),
        ('bohemio', 'Bohemio'),
        ('vintage', 'Vintage'),
        ('minimalista', 'Minimalista'),
        ('streetwear', 'Streetwear')
    ]

    COLORES = [
        ('#000000', 'Negro'),
        ('#FFFFFF', 'Blanco'),
        ('#FF0000', 'Rojo'),
        ('#0000FF', 'Azul'),
        ('#008000', 'Verde'),
        ('#FFFF00', 'Amarillo'),
        ('#FFC0CB', 'Rosa'),
        ('#800080', 'Morado'),
        ('#A52A2A', 'Marrón'),
        ('#808080', 'Gris')
    ]

    RANGOS_PRECIO = [
        ('0-50', '$0 - $50'),
        ('51-100', '$51 - $100'),
        ('101-200', '$101 - $200'),
        ('201-500', '$201 - $500'),
        ('501+', 'Más de $500')
    ]

    talla = forms.ChoiceField(choices=TALLAS, required=False)
    estilos_preferidos = forms.MultipleChoiceField(
        choices=ESTILOS,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    colores_preferidos = forms.MultipleChoiceField(
        choices=COLORES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    rango_precio_preferido = forms.ChoiceField(
        choices=RANGOS_PRECIO,
        required=False
    )
    marcas_favoritas = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text='Ingresa tus marcas favoritas separadas por comas',
        required=False
    )
    ocasiones_uso = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text='Ingresa las ocasiones separadas por comas (ej: trabajo, fiesta, casual)',
        required=False
    )
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False
    )
    telefono = forms.CharField(max_length=20, required=False)
    ubicacion = forms.CharField(max_length=100, required=False)
    redes_sociales = forms.JSONField(required=False)

    class Meta:
        model = PerfilUsuario
        fields = ['descripcion', 'telefono', 'ubicacion', 'redes_sociales', 
                 'talla', 'estilos_preferidos', 'colores_preferidos', 
                 'rango_precio_preferido', 'marcas_favoritas', 'ocasiones_uso']

    def clean_marcas_favoritas(self):
        marcas = self.cleaned_data.get('marcas_favoritas', '')
        if marcas:
            return [marca.strip() for marca in marcas.split(',') if marca.strip()]
        return []

    def clean_ocasiones_uso(self):
        ocasiones = self.cleaned_data.get('ocasiones_uso', '')
        if ocasiones:
            return [ocasion.strip() for ocasion in ocasiones.split(',') if ocasion.strip()]
        return []

    def clean_redes_sociales(self):
        redes = self.cleaned_data.get('redes_sociales')
        if isinstance(redes, str):
            try:
                return json.loads(redes)
            except json.JSONDecodeError:
                return {}
        return redes or {} 