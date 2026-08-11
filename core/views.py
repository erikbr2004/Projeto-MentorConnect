from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.models import MentorProfile, AlunoProfile
from core.models import Disciplina
from agendamentos.models import Sessao
from .forms import DisciplinaForm


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin para verificar se o usuário é ADMIN"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'ADMIN'


class MentorListView(LoginRequiredMixin, ListView):
    model = MentorProfile
    template_name = 'core/mentor_list.html'
    context_object_name = 'mentores'

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        disciplina_id = self.request.GET.get('disciplina')

        if q:
            queryset = queryset.filter(
                Q(user__first_name__icontains=q) | 
                Q(user__last_name__icontains=q) |
                Q(bio__icontains=q)
            )
        
        if disciplina_id:
            queryset = queryset.filter(disciplinas__id=disciplina_id)
            
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['disciplinas'] = Disciplina.objects.all()
        return context


class MentorDetailView(LoginRequiredMixin, DetailView):
    model = MentorProfile
    template_name = 'core/mentor_detail.html'
    context_object_name = 'mentor'


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_mentor():
            context['sessoes_pendentes'] = Sessao.objects.filter(
                mentor__user=user, status='PENDENTE'
            ).order_by('data_inicio')
            context['sessoes_proximas'] = Sessao.objects.filter(
                mentor__user=user, status='CONFIRMADA'
            ).order_by('data_inicio')
        elif user.is_aluno():
            context['minhas_sessoes'] = Sessao.objects.filter(
                aluno__user=user
            ).exclude(status__in=['CANCELADA', 'CONCLUIDA']).order_by('-data_inicio')
            
        return context


# ==================== CRUD de Disciplinas (Área Admin) ====================

class DisciplinaListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Disciplina
    template_name = 'core/admin/disciplina_list.html'
    context_object_name = 'disciplinas'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(nome__icontains=q) | Q(codigo__icontains=q)
            )
        return queryset.order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context


class DisciplinaCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Disciplina
    form_class = DisciplinaForm
    template_name = 'core/admin/disciplina_form.html'
    success_url = reverse_lazy('admin_disciplina_list')

    def form_valid(self, form):
        messages.success(self.request, 'Disciplina criada com sucesso!')
        return super().form_valid(form)


class DisciplinaUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Disciplina
    form_class = DisciplinaForm
    template_name = 'core/admin/disciplina_form.html'
    success_url = reverse_lazy('admin_disciplina_list')

    def form_valid(self, form):
        messages.success(self.request, 'Disciplina atualizada com sucesso!')
        return super().form_valid(form)


class DisciplinaDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Disciplina
    template_name = 'core/admin/disciplina_confirm_delete.html'
    success_url = reverse_lazy('admin_disciplina_list')

    def form_valid(self, form):
        messages.success(self.request, 'Disciplina removida com sucesso!')
        return super().form_valid(form)


class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'core/admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_disciplinas'] = Disciplina.objects.count()
        context['total_mentores'] = MentorProfile.objects.count()
        context['total_alunos'] = AlunoProfile.objects.count()
        context['total_sessoes'] = Sessao.objects.count()
        return context


# ==================== Listagem de Mentores e Alunos (Admin) ====================

class AdminMentorListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = MentorProfile
    template_name = 'core/admin/mentor_list.html'
    context_object_name = 'mentores'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(user__username__icontains=q) |
                Q(user__email__icontains=q)
            )
        return queryset.order_by('user__first_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context


class AdminMentorDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = MentorProfile
    template_name = 'core/admin/mentor_detail.html'
    context_object_name = 'mentor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Estatísticas do mentor
        context['total_sessoes'] = Sessao.objects.filter(mentor=self.object).count()
        context['sessoes_concluidas'] = Sessao.objects.filter(mentor=self.object, status='CONCLUIDA').count()
        return context


class AdminAlunoListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = AlunoProfile
    template_name = 'core/admin/aluno_list.html'
    context_object_name = 'alunos'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(user__username__icontains=q) |
                Q(matricula__icontains=q)
            )
        return queryset.order_by('user__first_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context


class AdminAlunoDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = AlunoProfile
    template_name = 'core/admin/aluno_detail.html'
    context_object_name = 'aluno'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Estatísticas do aluno
        context['total_sessoes'] = Sessao.objects.filter(aluno=self.object).count()
        context['sessoes_concluidas'] = Sessao.objects.filter(aluno=self.object, status='CONCLUIDA').count()
        return context
