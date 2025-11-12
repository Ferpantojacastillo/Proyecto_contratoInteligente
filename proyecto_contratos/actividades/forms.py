from django import forms
from .models import Actividad

class ActividadForm(forms.ModelForm):
    fecha = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))
    
    class Meta:
        model = Actividad
        fields = ['nombre', 'descripcion', 'tipo', 'fecha', 'lugar', 'capacidad', 'creditos_equivalentes', 'encargado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'creditos_equivalentes': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'encargado': forms.Select(attrs={'class': 'form-select'}),
        }
