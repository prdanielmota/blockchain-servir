# Plano: Gestão de Membros por Ministério e Redesign Neo-Brutalismo

## 1. Banco de Dados (Muitos-para-Muitos)
*   Criar tabela de associação `user_ministries` em `models.py`.
*   Adicionar relacionamento `ministries` na classe `User`.
*   Criar script de migração `migrate_user_ministry.py`.

## 2. Admin: Atribuir Ministérios
*   Criar nova rota/template para Editar Usuário Completo (`/admin/users/edit/<id>`).
*   Substituir o botão simples de "Toggle Role" por um botão "Editar" que leva a esse formulário.
*   No formulário: Checkboxes para selecionar os ministérios do usuário.

## 3. Bot: Filtragem Personalizada
*   No `webhook.py`, atualizar a função `get_ministries_list`.
*   Lógica: `User.ministries` + Ministério ID 1 (Geral).

## 4. Design System: Neo-Brutalismo
*   Atualizar CSS global em `base_admin.html` (e `base.html` se usado).
*   **Estilo**:
    *   Bordas pretas grossas (2px/3px).
    *   Sombras sólidas deslocadas (`box-shadow: 5px 5px 0 #000`).
    *   Cores: Fundo bege/papel, Cards brancos ou coloridos, Botões vibrantes.
    *   Fontes: Monospace ou Sans-serif pesada para títulos.