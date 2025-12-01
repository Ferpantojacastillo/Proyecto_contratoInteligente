from django import forms
from .models import Actividad
from usuarios.models import Usuario

class ActividadForm(forms.ModelForm):
    fecha = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))
    encargado_manual = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del maestro (si no existe, se creará)'}))
    
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
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
      
        try:
            self.fields['encargado'].queryset = Usuario.objects.none()
           
            self.fields['encargado'].empty_label = '---'
        except Exception:
            pass
