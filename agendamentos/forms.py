from django import forms
from django.core.exceptions import ValidationError
from .models import Disponibilidade, Sessao, Avaliacao

class DisponibilidadeForm(forms.ModelForm):
    class Meta:
        model = Disponibilidade
        fields = ['dia_semana', 'hora_inicio', 'hora_fim']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time'}),
        }

class AgendarSessaoForm(forms.Form):
    data = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Data da Sessão"
    )
    
    def __init__(self, *args, **kwargs):
        self.disponibilidade = kwargs.pop('disponibilidade', None)
        super().__init__(*args, **kwargs)

    def clean_data(self):
        data = self.cleaned_data['data']
        if self.disponibilidade:
            if data.weekday() != self.disponibilidade.dia_semana:
                dia_nome = self.disponibilidade.get_dia_semana_display()
                raise ValidationError(f"A data selecionada não é {dia_nome}.")
        return data

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['nota', 'comentario']
        widgets = {
            'nota': forms.Select(attrs={'class': 'form-select'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'nota': 'Nota (1 a 5)',
            'comentario': 'Comentário sobre a mentoria'
        }
