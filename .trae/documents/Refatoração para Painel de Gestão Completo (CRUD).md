# Plano: Painel Administrativo Completo (CRUD)

## 1. Estrutura de Navegação (`base_admin.html`)
*   Criar um layout base específico para o Admin.
*   Menu de Navegação: Dashboard, Ministérios, Missões, Usuários.

## 2. Gestão de Ministérios (`/admin/ministries`)
*   **Listar**: Tabela com ID, Nome, Ações.
*   **Criar/Editar**: Formulário dedicado (não apenas um input pequeno).
*   **Excluir**: Rota para remover ministério (com validação se há missões vinculadas).

## 3. Gestão de Usuários (`/admin/users`)
*   **Listar**: Tabela com Nome, Email, Role, Pontos.
*   **Ações**:
    *   Botão "Tornar Admin" / "Remover Admin".
    *   Botão "Excluir Usuário".

## 4. Gestão de Missões (`/admin/actions`)
*   **Listar**: Tabela com Nome, Pontos, Ministério, Status.
*   **Editar**: Permite trocar o Ministério ou ajustar pontos de uma missão já criada.
*   **Excluir/Arquivar**: Remove a missão da lista do bot.

## 5. Refatoração do Código (`admin.py`)
*   Separar as rotas de CRUD para manter o código limpo.
*   Criar templates individuais: `admin_ministries.html`, `admin_users.html`, `admin_actions.html`.