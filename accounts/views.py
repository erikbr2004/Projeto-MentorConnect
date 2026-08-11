from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import AlunoSignUpForm, MentorSignUpForm, MentorProfileForm, AlunoProfileForm
from .models import CustomUser, MentorProfile, AlunoProfile


class SignUpView(TemplateView):
    template_name = 'accounts/signup.html'


class AlunoSignUpView(CreateView):
    model = CustomUser
    form_class = AlunoSignUpForm
    template_name = 'accounts/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Aluno'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class MentorSignUpView(CreateView):
    model = CustomUser
    form_class = MentorSignUpForm
    template_name = 'accounts/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'Mentor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class PerfilEditarView(LoginRequiredMixin, UpdateView):
    """View genérica que redireciona para o form correto baseado no tipo de usuário"""
    template_name = 'accounts/perfil_form.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        user = self.request.user
        if user.is_mentor():
            return user.mentor_profile
        elif user.is_aluno():
            return user.aluno_profile
        return None

    def get_form_class(self):
        user = self.request.user
        if user.is_mentor():
            return MentorProfileForm
        elif user.is_aluno():
            return AlunoProfileForm
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'Mentor' if self.request.user.is_mentor() else 'Aluno'
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return redirect(self.success_url)
