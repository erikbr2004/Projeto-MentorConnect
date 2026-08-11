Alunos: Pedro de Oliveira Pinto | Erik Barbosa de Castro

Pedro de Oliveira Pinto responsável por: autenticação de usuários e modelagem
Erik Barbosa de Castro responsável por: modelagem HTML e rotas

# UTFPR Mentor Connect

Sistema de mentoria acadêmica em Django.

## Configuração

1. Instalar dependências:
```bash
pip install django
```

2. Rodar migrações:
```bash
python manage.py migrate
```

3. Rodar servidor:
```bash
python manage.py runserver
```

## Gerenciamento de Usuários

### Criar usuário Administrador

O usuário admin tem acesso ao painel administrativo do sistema (`/core/admin-painel/`).

```bash
python manage.py shell
```

```python
from accounts.models import CustomUser

user = CustomUser.objects.create_user('admin', 'admin@email.com', 'senha123')
user.role = 'ADMIN'
user.save()
```

### Trocar senha de um usuário

**Opção 1 - Via terminal:**
```bash
python manage.py changepassword nome_do_usuario
```

**Opção 2 - Via shell do Django:**
```bash
python manage.py shell
```

```python
from accounts.models import CustomUser

user = CustomUser.objects.get(username='nome_do_usuario')
user.set_password('nova_senha')
user.save()
```

### Listar todos os usuários

```bash
python manage.py shell
```

```python
from accounts.models import CustomUser

for u in CustomUser.objects.all():
    print(f'{u.username} - {u.role}')
```

## Funcionalidades

- **Autenticação**: Cadastro distinto para Alunos e Mentores
- **Gestão de Horários**: Mentores podem adicionar, editar e remover disponibilidade
- **Busca**: Alunos podem buscar mentores por nome ou disciplina
- **Agendamento**: Alunos podem solicitar sessões de mentoria
- **Avaliação**: Alunos podem avaliar sessões concluídas
- **Painel Admin**: Gestão de disciplinas, visualização de mentores e alunos

## Estrutura

- `accounts`: Gestão de usuários e perfis
- `core`: Páginas base, disciplinas e painel administrativo
- `agendamentos`: Sessões de mentoria e disponibilidades

## Tipos de Usuário

| Tipo | Descrição |
|------|-----------|
| `ADMIN` | Acesso ao painel administrativo |
| `MENTOR` | Pode oferecer mentorias |
| `ALUNO` | Pode buscar e agendar mentorias |
