from django import forms
from .models import Configuracion

class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = [
            'nombre', 'direccion', 'telefono', 'redes', 'cuit', 'imagen',
            'precios_automaticos', 'mostrar_stock_pendiente', 'moneda', 'moneda_secundaria'
        ]