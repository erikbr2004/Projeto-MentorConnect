from django.db import models
from django.conf import settings

class Disponibilidade(models.Model):
    DIAS_SEMANA = (
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    )
    mentor = models.ForeignKey('accounts.MentorProfile', on_delete=models.CASCADE, related_name='disponibilidades')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    def __str__(self):
        return f"{self.mentor} - {self.get_dia_semana_display()} ({self.hora_inicio} - {self.hora_fim})"

class Sessao(models.Model):
    STATUS_CHOICES = (
        ('PENDENTE', 'Pendente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
    )
    aluno = models.ForeignKey('accounts.AlunoProfile', on_delete=models.CASCADE, related_name='sessoes_aluno')
    mentor = models.ForeignKey('accounts.MentorProfile', on_delete=models.CASCADE, related_name='sessoes_mentor')
    disciplina = models.ForeignKey('core.Disciplina', on_delete=models.SET_NULL, null=True, blank=True)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    @property
    def avaliacao_rel(self):
        # Helper para acessar a avaliação no template sem erro se não existir
        try:
            return self.avaliacao
        except Avaliacao.DoesNotExist:
            return None

    def __str__(self):
        return f"Sessão {self.id} - {self.mentor} e {self.aluno} ({self.status})"

class Avaliacao(models.Model):
    sessao = models.OneToOneField(Sessao, on_delete=models.CASCADE, related_name='avaliacao')
    nota = models.IntegerField(choices=[(i, i) for i in range(1, 6)]) # 1 a 5
    comentario = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avaliação Sessão {self.sessao.id} - Nota {self.nota}"
