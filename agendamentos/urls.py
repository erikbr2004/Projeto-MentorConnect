from django.urls import path
from . import views

urlpatterns = [
    path('disponibilidade/', views.DisponibilidadeListView.as_view(), name='disponibilidade_list'),
    path('disponibilidade/nova/', views.DisponibilidadeCreateView.as_view(), name='disponibilidade_create'),
    path('disponibilidade/<int:pk>/editar/', views.DisponibilidadeUpdateView.as_view(), name='disponibilidade_update'),
    path('disponibilidade/<int:pk>/deletar/', views.DisponibilidadeDeleteView.as_view(), name='disponibilidade_delete'),
    
    path('agendar/<int:pk>/', views.AgendarSessaoView.as_view(), name='agendar_sessao'),
    
    path('sessao/<int:pk>/aceitar/', views.AceitarSessaoView.as_view(), name='aceitar_sessao'),
    path('sessao/<int:pk>/rejeitar/', views.RejeitarSessaoView.as_view(), name='rejeitar_sessao'),
    path('sessao/<int:pk>/concluir/', views.ConcluirSessaoView.as_view(), name='concluir_sessao'),
    path('sessao/<int:pk>/cancelar/', views.CancelarSessaoAlunoView.as_view(), name='cancelar_sessao'),
    path('sessao/<int:pk>/avaliar/', views.AvaliarSessaoView.as_view(), name='avaliar_sessao'),
    
    path('historico/', views.HistoricoSessoesView.as_view(), name='historico_sessoes'),
]
