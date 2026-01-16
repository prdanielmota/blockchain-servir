# Plano: Gestão Dinâmica de Ministérios

## 1. Atualização do Modelo de Dados (`models.py`)
*   Criar classe `Ministry` (`id`, `name`).
*   Alterar `ActionDefinition` para ter `ministry_id` (FK).
*   Script de migração para criar a nova tabela e atualizar a existente.
*   Criar ministério padrão "Geral" na migração para não quebrar dados antigos.

## 2. Dashboard Admin (`admin.py` / `dashboard.html`)
*   **Nova Rota**: `/ministry/create` (POST).
*   **Interface**: Adicionar seção "Ministérios" no Dashboard.
    *   Listar existentes.
    *   Formulário simples para criar novo.

## 3. Lógica do Bot (`webhook.py`)
*   **Listagem de Missões**:
    *   Passo 1: Buscar todos os ministérios com missões ativas.
    *   Passo 2: Apresentar menu dinâmico (1. Geral, 2. Louvor...).
    *   Passo 3: Filtrar missões pelo `ministry_id` escolhido.
*   **Criação de Missão**:
    *   Passo extra: Perguntar a qual ministério a missão pertence (listando as opções do banco).

## 4. Ajustes Gerais
*   Garantir que missões antigas (sem ministério) sejam migradas para o "Geral".