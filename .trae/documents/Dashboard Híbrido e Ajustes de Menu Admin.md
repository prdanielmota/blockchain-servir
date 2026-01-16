# Plano: Dashboard de Usuário e Ajustes Admin

## 1. Ajustes no Bot (`webhook.py`)
*   **Menu**: Se Admin, exibir "3️⃣ Criar Missão". Se User, "3️⃣ Propor Missão".
*   **Lógica de Criação**:
    *   Ao finalizar a criação (em `handle_propose_points`):
    *   Se Admin -> Salvar com `status='approved'`.
    *   Se User -> Salvar com `status='pending'` (como já é).

## 2. Refatoração da Rota Dashboard (`admin.py`)
*   Remover a restrição `@login_required` + `if role != 'admin' return 403`.
*   Manter `@login_required`.
*   **Lógica de Dados**:
    *   Se Admin: Carrega todos os usuários, todos os blocos, todas as ações (como hoje).
    *   Se User: Carrega apenas os blocos do próprio usuário (`Block.query.filter_by(user_id=current_user.id)`).

## 3. Refatoração do Template (`dashboard.html`)
*   Criar seção **"Meu Perfil"** no topo (visível para todos): Mostra Card com Pontos, Estágio e Badge.
*   Envolver as tabelas de "Gerenciar Usuários", "Criar Ação" e "Blockchain Explorer (Geral)" em um bloco `{% if current_user.role == 'admin' %}`.
*   Criar tabela **"Minhas Conquistas"** (visível para User): Mostra histórico pessoal.