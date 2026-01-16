# Plano: Gestão Completa via Bot (Propostas, Feedback e Aprovação)

## 1. Atualização do Banco (`ActionDefinition`)
*   Adicionar coluna `status` (default: 'approved').
*   Executar migração.

## 2. Fluxo de Proposta (Usuário)
*   Implementar estados `PROPOSE_NAME` e `PROPOSE_POINTS`.
*   Salvar com `status='pending'`.

## 3. Fluxo de Feedback (Todos)
*   Novo estado `ACTION_FEEDBACK` antes de concluir a missão.
*   Pergunta nota de 1 a 5.
*   Salva no Blockchain: `{..., "rating": 5}`.

## 4. Fluxo de Aprovação (Apenas Admin)
*   Alterar `get_main_menu` para mostrar opção "4️⃣ Aprovar Pendentes" se for Admin.
*   **Estado `ADMIN_PENDING_LIST`**: Lista ações com `status='pending'`.
*   **Estado `ADMIN_REVIEW`**:
    *   Mostra detalhes da proposta.
    *   1️⃣ Aprovar -> Atualiza banco para `status='approved'`.
    *   2️⃣ Rejeitar -> Atualiza para `status='rejected'`.