from django.urls import path
from . import views

urlpatterns = [
    path('mentores/', views.MentorListView.as_view(), name='mentor_list'),
    path('mentores/<int:pk>/', views.MentorDetailView.as_view(), name='mentor_detail'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Área Administrativa
    path('admin-painel/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-painel/disciplinas/', views.DisciplinaListView.as_view(), name='admin_disciplina_list'),
    path('admin-painel/disciplinas/nova/', views.DisciplinaCreateView.as_view(), name='admin_disciplina_create'),
    path('admin-painel/disciplinas/<int:pk>/editar/', views.DisciplinaUpdateView.as_view(), name='admin_disciplina_update'),
    path('admin-painel/disciplinas/<int:pk>/deletar/', views.DisciplinaDeleteView.as_view(), name='admin_disciplina_delete'),
    
    # Gerenciamento de Mentores (Admin)
    path('admin-painel/mentores/', views.AdminMentorListView.as_view(), name='admin_mentor_list'),
    path('admin-painel/mentores/<int:pk>/', views.AdminMentorDetailView.as_view(), name='admin_mentor_detail'),
    
    # Gerenciamento de Alunos (Admin)
    path('admin-painel/alunos/', views.AdminAlunoListView.as_view(), name='admin_aluno_list'),
    path('admin-painel/alunos/<int:pk>/', views.AdminAlunoDetailView.as_view(), name='admin_aluno_detail'),
]
