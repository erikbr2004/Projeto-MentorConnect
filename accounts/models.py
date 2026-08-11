from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrador'),
        ('ALUNO', 'Aluno'),
        ('MENTOR', 'Mentor'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='ALUNO')

    def is_aluno(self):
        return self.role == 'ALUNO'

    def is_mentor(self):
        return self.role == 'MENTOR'

class AlunoProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='aluno_profile')
    matricula = models.CharField(max_length=20)
    curso = models.ForeignKey('core.Curso', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Aluno: {self.user.username}"

class MentorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='mentor_profile')
    bio = models.TextField(blank=True)
    disciplinas = models.ManyToManyField('core.Disciplina', related_name='mentores', blank=True)

    def __str__(self):
        return f"Mentor: {self.user.username}"
