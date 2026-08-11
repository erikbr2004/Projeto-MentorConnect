from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.timezone import make_aware
from django.db.models import Q
from datetime import datetime, time
from .models import Disponibilidade, Sessao, Avaliacao
from .forms import DisponibilidadeForm, AgendarSessaoForm, AvaliacaoForm


class MentorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_mentor()


class AlunoRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_aluno()


class DisponibilidadeListView(LoginRequiredMixin, MentorRequiredMixin, ListView):
    model = Disponibilidade
    template_name = 'agendamentos/disponibilidade_list.html'
    context_object_name = 'disponibilidades'

    def get_queryset(self):
        return Disponibilidade.objects.filter(mentor__user=self.request.user).order_by('dia_semana', 'hora_inicio')


class DisponibilidadeCreateView(LoginRequiredMixin, MentorRequiredMixin, CreateView):
    model = Disponibilidade
    form_class = DisponibilidadeForm
    template_name = 'agendamentos/disponibilidade_form.html'
    success_url = reverse_lazy('disponibilidade_list')

    def form_valid(self, form):
        form.instance.mentor = self.request.user.mentor_profile
        messages.success(self.request, 'Disponibilidade adicionada com sucesso!')
        return super().form_valid(form)


class DisponibilidadeUpdateView(LoginRequiredMixin, MentorRequiredMixin, UpdateView):
    model = Disponibilidade
    form_class = DisponibilidadeForm
    template_name = 'agendamentos/disponibilidade_form.html'
    success_url = reverse_lazy('disponibilidade_list')

    def get_queryset(self):
        return super().get_queryset().filter(mentor__user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Disponibilidade atualizada com sucesso!')
        return super().form_valid(form)


class DisponibilidadeDeleteView(LoginRequiredMixin, MentorRequiredMixin, DeleteView):
    model = Disponibilidade
    success_url = reverse_lazy('disponibilidade_list')
    template_name = 'agendamentos/disponibilidade_confirm_delete.html'

    def get_queryset(self):
        return super().get_queryset().filter(mentor__user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Disponibilidade removida com sucesso!')
        return super().form_valid(form)


class AgendarSessaoView(LoginRequiredMixin, FormView):
    template_name = 'agendamentos/agendar_sessao.html'
    form_class = AgendarSessaoForm

    def dispatch(self, request, *args, **kwargs):
        self.disponibilidade = get_object_or_404(Disponibilidade, pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['disponibilidade'] = self.disponibilidade
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['disponibilidade'] = self.disponibilidade
        return context

    def form_valid(self, form):
        data = form.cleaned_data['data']
        start_dt = datetime.combine(data, self.disponibilidade.hora_inicio)
        end_dt = datetime.combine(data, self.disponibilidade.hora_fim)
        
        Sessao.objects.create(
            aluno=self.request.user.aluno_profile,
            mentor=self.disponibilidade.mentor,
            data_inicio=start_dt,
            data_fim=end_dt,
            status='PENDENTE'
        )
        messages.success(self.request, 'Solicitação de mentoria enviada com sucesso!')
        return redirect('dashboard')


class AceitarSessaoView(LoginRequiredMixin, MentorRequiredMixin, View):
    def post(self, request, pk):
        sessao = get_object_or_404(Sessao, pk=pk, mentor__user=request.user)
        sessao.status = 'CONFIRMADA'
        sessao.save()
        messages.success(request, 'Sessão confirmada!')
        return redirect('dashboard')


class RejeitarSessaoView(LoginRequiredMixin, MentorRequiredMixin, View):
    def post(self, request, pk):
        sessao = get_object_or_404(Sessao, pk=pk, mentor__user=request.user)
        sessao.status = 'CANCELADA'
        sessao.save()
        messages.warning(request, 'Sessão cancelada/rejeitada.')
        return redirect('dashboard')


class ConcluirSessaoView(LoginRequiredMixin, MentorRequiredMixin, View):
    def post(self, request, pk):
        sessao = get_object_or_404(Sessao, pk=pk, mentor__user=request.user)
        if sessao.status == 'CONFIRMADA':
            sessao.status = 'CONCLUIDA'
            sessao.save()
            messages.success(request, 'Sessão concluída com sucesso!')
        return redirect('dashboard')


class CancelarSessaoAlunoView(LoginRequiredMixin, AlunoRequiredMixin, View):
    """Permite que o aluno cancele uma sessão pendente"""
    def post(self, request, pk):
        sessao = get_object_or_404(
            Sessao, 
            pk=pk, 
            aluno__user=request.user,
            status__in=['PENDENTE', 'CONFIRMADA']
        )
        sessao.status = 'CANCELADA'
        sessao.save()
        messages.info(request, 'Sessão cancelada com sucesso.')
        return redirect('dashboard')


class HistoricoSessoesView(LoginRequiredMixin, ListView):
    model = Sessao
    template_name = 'agendamentos/historico.html'
    context_object_name = 'sessoes'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = Sessao.objects.filter(
            Q(status='CONCLUIDA') | Q(status='CANCELADA')
        )
        
        # Filtro de busca
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(mentor__user__first_name__icontains=q) |
                Q(mentor__user__last_name__icontains=q) |
                Q(aluno__user__first_name__icontains=q) |
                Q(aluno__user__last_name__icontains=q) |
                Q(disciplina__nome__icontains=q)
            )
        
        # Admin vê todas as sessões
        if user.role == 'ADMIN':
            return queryset.order_by('-data_inicio')
        elif user.is_mentor():
            return queryset.filter(mentor__user=user).order_by('-data_inicio')
        elif user.is_aluno():
            return queryset.filter(aluno__user=user).order_by('-data_inicio')
        return Sessao.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context


class AvaliarSessaoView(LoginRequiredMixin, CreateView):
    model = Avaliacao
    form_class = AvaliacaoForm
    template_name = 'agendamentos/avaliacao_form.html'
    success_url = reverse_lazy('historico_sessoes')

    def dispatch(self, request, *args, **kwargs):
        self.sessao = get_object_or_404(
            Sessao, 
            pk=kwargs.get('pk'), 
            aluno__user=request.user, 
            status='CONCLUIDA'
        )
        if hasattr(self.sessao, 'avaliacao'):
            messages.info(request, 'Esta sessão já foi avaliada.')
            return redirect('historico_sessoes')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.sessao = self.sessao
        messages.success(self.request, 'Avaliação enviada com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessao'] = self.sessao
        return context
