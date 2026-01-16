# Plano: Correção de Rotas Quebradas

## 1. Ajuste no `dashboard.html`
*   Remover o formulário antigo de "Criar Ministério" que aponta para `admin.create_ministry`.
*   Remover o formulário antigo de "Criar Ação" que aponta para `admin.create_action` (pois agora temos `/admin/actions/new`).
*   Manter apenas os cards de acesso rápido para as novas seções CRUD.

## 2. Ajuste no `admin.py`
*   Remover as funções legadas `create_ministry_legacy` e `create_action` (se não forem mais usadas), para limpar o código.
*   Se ainda precisarmos delas, renomear de volta ou corrigir os templates. A melhor opção é usar o novo CRUD.