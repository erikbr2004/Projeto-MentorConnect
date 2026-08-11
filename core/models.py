from django.db import models

class Curso(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return self.nome

class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome
