# UTFPR Mentor Connect — Plataforma de Mentoria Acadêmica

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![SQLite](https://img.shields.io/badge/Banco-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Arquitetura](https://img.shields.io/badge/Arquitetura-MTV%20%7C%20CBV-2E7D32?style=flat-square)](#arquitetura)
[![Idioma](https://img.shields.io/badge/Idioma-pt--BR-009C3B?style=flat-square)](#)

Aplicação web que conecta alunos a mentores dentro da universidade. Mentores publicam sua
disponibilidade semanal, alunos buscam por disciplina e agendam sessões, e todo o ciclo —
solicitação, confirmação, conclusão e avaliação — é acompanhado pela plataforma.

---

## Sobre o projeto

O problema resolvido é simples de enunciar e cheio de regras na prática: **quem pode fazer
o quê, e quando**. Um aluno não pode publicar horários. Um mentor não pode agendar consigo
mesmo. Uma sessão só pode ser avaliada depois de concluída, e só pelo aluno que participou
dela. Cancelar faz sentido em uma sessão pendente, não em uma que já aconteceu.

O projeto trata essas regras como o núcleo do sistema, e não como validações espalhadas
pelos templates. A autorização é aplicada em cada view por meio de mixins do Django
(`LoginRequiredMixin` e `UserPassesTestMixin`), e os querysets são filtrados pelo usuário
autenticado — de modo que um mentor nunca consegue listar ou manipular as sessões de outro,
mesmo alterando a URL manualmente.

---

## Arquitetura

O sistema usa um **usuário customizado com papéis**, estendendo `AbstractUser` em vez de
criar tabelas paralelas de perfil desconectadas da autenticação:

```python
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrador'),
        ('ALUNO', 'Aluno'),
        ('MENTOR', 'Mentor'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='ALUNO')
```

Cada papel tem um perfil próprio ligado por `OneToOneField`, guardando apenas o que faz
sentido para ele — matrícula e curso para o aluno, biografia e disciplinas lecionadas para
o mentor. Isso evita a tabela única com metade das colunas sempre nulas.

```text
CustomUser (role: ADMIN | ALUNO | MENTOR)
├── AlunoProfile ── matricula, curso ──────> Curso
└── MentorProfile ── bio, disciplinas ─────> Disciplina (N:N)
        │
        └── Disponibilidade (dia da semana, hora início, hora fim)

Sessao (aluno, mentor, disciplina, período, status)
└── Avaliacao (nota 1-5, comentário)   [1:1 com a sessão]
```

### Ciclo de vida de uma sessão

```text
                  aluno solicita
                        │
                        v
                   ┌──────────┐   mentor confirma   ┌────────────┐
                   │ PENDENTE │────────────────────>│ CONFIRMADA │
                   └──────────┘                     └────────────┘
                        │                                 │
        aluno ou mentor │                                 │ mentor conclui
             cancelam   │                                 v
                        │                          ┌────────────┐
                        │                          │ CONCLUIDA  │──> aluno avalia
                        v                          └────────────┘
                  ┌────────────┐
                  │ CANCELADA  │
                  └────────────┘
```

Cada transição é uma view distinta com sua própria verificação de permissão. A conclusão só
é aceita a partir de `CONFIRMADA`, e o cancelamento só a partir de `PENDENTE` ou
`CONFIRMADA` — estados terminais não voltam atrás.

---

## Funcionalidades

### Para o aluno
- Cadastro com matrícula e curso.
- Busca de mentores por nome, biografia ou disciplina, com filtro combinado.
- Agendamento de sessões a partir da disponibilidade publicada pelo mentor.
- Dashboard com sessões próximas e pendentes.
- Cancelamento de sessões ainda não realizadas.
- Avaliação de sessões concluídas, com nota de 1 a 5 e comentário.

### Para o mentor
- Cadastro com biografia e seleção das disciplinas que leciona.
- Gestão da disponibilidade semanal: criação, edição e exclusão de faixas de horário.
- Confirmação, recusa e conclusão das sessões solicitadas.
- Dashboard com a agenda e o histórico.

### Para o administrador
- Painel administrativo próprio em `/core/admin-painel/`, separado do Django Admin.
- CRUD de disciplinas.
- Listagem e busca de mentores e alunos, com contagem de sessões totais e concluídas por
  usuário.

---

## Estrutura do repositório

```text
.
├── config/                     # Configurações, URLs raiz, WSGI e ASGI
├── accounts/                   # Usuário customizado, perfis, cadastro e edição
│   ├── models.py               # CustomUser, AlunoProfile, MentorProfile
│   ├── forms.py                # Formulários de cadastro por papel
│   └── views.py
├── core/                       # Páginas base, disciplinas e painel administrativo
│   ├── models.py               # Curso, Disciplina
│   └── views.py                # Busca de mentores, dashboard, gestão administrativa
├── agendamentos/               # Coração do domínio
│   ├── models.py               # Disponibilidade, Sessao, Avaliacao
│   └── views.py                # Transições de estado e histórico
├── templates/                  # base.html, home e telas de autenticação
├── manage.py
└── db_v2.sqlite3               # Base SQLite de desenvolvimento
```

---

## Como executar

Requisitos: Python 3.10 ou superior — o projeto foi desenvolvido em 3.13.

```bash
python -m venv venv
```

```bash
venv\Scripts\activate
```

```bash
pip install django
```

```bash
python manage.py migrate
```

```bash
python manage.py runserver
```

A aplicação fica disponível em `http://127.0.0.1:8000/`.

> Em Linux ou macOS, ative o ambiente virtual com `source venv/bin/activate`.

### Criando um administrador

O papel `ADMIN` dá acesso ao painel administrativo da aplicação:

```bash
python manage.py shell
```

```python
from accounts.models import CustomUser

user = CustomUser.objects.create_user('admin', 'admin@email.com', 'senha123')
user.role = 'ADMIN'
user.save()
```

Alunos e mentores se cadastram pela própria interface, em `/accounts/signup/`.

### Comandos úteis

Trocar a senha de um usuário:

```bash
python manage.py changepassword nome_do_usuario
```

Listar usuários e seus papéis:

```python
from accounts.models import CustomUser

for u in CustomUser.objects.all():
    print(f'{u.username} - {u.role}')
```

---

## Decisões técnicas

- **Class-Based Views** em vez de function views: `ListView`, `DetailView`, `CreateView` e
  `UpdateView` eliminam boilerplate repetido de CRUD, e os mixins de autorização se aplicam
  de forma declarativa e consistente em todas as telas.
- **Autorização no queryset, não no template**: esconder um botão não protege um endpoint.
  As views sobrescrevem `get_queryset()` para restringir os objetos ao usuário autenticado.
- **Usuário customizado desde a primeira migração** — trocar o modelo de usuário depois que
  o projeto já tem dados é notoriamente trabalhoso no Django, então a decisão foi tomada
  antes de qualquer migração.
- **SQLite em desenvolvimento**: zero configuração para quem clona o repositório. Migrar
  para PostgreSQL exige apenas alterar `DATABASES` em `config/settings.py`.
- **Localização em pt-BR** com fuso `America/Sao_Paulo` e `USE_TZ` ativo, para que horários
  de sessão sejam armazenados corretamente.

---

## Conceitos exercitados

- Padrão MTV do Django e organização em apps com responsabilidades separadas
- Modelagem relacional com ORM: 1:1, N:N e chaves estrangeiras com estratégias de exclusão
- Autenticação, autorização e controle de acesso baseado em papéis
- Máquina de estados aplicada a um fluxo de negócio
- Class-Based Views, mixins e formulários do Django
- Migrações e evolução de esquema
- Templates com herança e interface responsiva com Bootstrap

---

## Autores

- Pedro de Oliveira Pinto
- Erik Barbosa de Castro
