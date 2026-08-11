from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('signup/aluno/', views.AlunoSignUpView.as_view(), name='aluno_signup'),
    path('signup/mentor/', views.MentorSignUpView.as_view(), name='mentor_signup'),
    path('perfil/editar/', views.PerfilEditarView.as_view(), name='perfil_editar'),
]
