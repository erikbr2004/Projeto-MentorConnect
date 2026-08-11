from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import CustomUser, AlunoProfile, MentorProfile
from core.models import Disciplina, Curso


class AlunoSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nome')
    last_name = forms.CharField(max_length=30, required=True, label='Sobrenome')
    matricula = forms.CharField(max_length=20, required=True)
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        required=True,
        empty_label="Selecione seu curso"
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.role = 'ALUNO'
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.save()
        AlunoProfile.objects.create(
            user=user,
            matricula=self.cleaned_data.get('matricula'),
            curso=self.cleaned_data.get('curso')
        )
        return user


class MentorSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nome')
    last_name = forms.CharField(max_length=30, required=True, label='Sobrenome')
    bio = forms.CharField(widget=forms.Textarea, required=False)
    disciplinas = forms.ModelMultipleChoiceField(
        queryset=Disciplina.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.role = 'MENTOR'
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.save()
        mentor_profile = MentorProfile.objects.create(
            user=user,
            bio=self.cleaned_data.get('bio')
        )
        mentor_profile.disciplinas.set(self.cleaned_data.get('disciplinas'))
        return user


class MentorProfileForm(forms.ModelForm):
    """Formulário para edição do perfil do Mentor"""
    first_name = forms.CharField(max_length=30, required=True, label='Nome')
    last_name = forms.CharField(max_length=30, required=True, label='Sobrenome')
    email = forms.EmailField(required=False, label='E-mail')

    class Meta:
        model = MentorProfile
        fields = ['bio', 'disciplinas']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'disciplinas': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile.save()
            self.save_m2m()
        return profile


class AlunoProfileForm(forms.ModelForm):
    """Formulário para edição do perfil do Aluno"""
    first_name = forms.CharField(max_length=30, required=True, label='Nome')
    last_name = forms.CharField(max_length=30, required=True, label='Sobrenome')
    email = forms.EmailField(required=False, label='E-mail')

    class Meta:
        model = AlunoProfile
        fields = ['matricula', 'curso']
        widgets = {
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'curso': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile.save()
        return profile
