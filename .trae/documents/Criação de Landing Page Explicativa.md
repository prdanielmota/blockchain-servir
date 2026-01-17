# Plano: Fluxo Otimizado (Admin x User)

## 1. Simplificar Visualização (`get_actions_list`)

* Remover estado `SELECT_VIEW_CATEGORY`.

* Ao clicar em "2", buscar todas as missões permitidas (Geral + Ministérios do Usuário).

* Exibir lista formatada com tags de ministério.

## 2. Simplificar Proposta (`handle_main_menu` -> 3)

* **Lógica Condicional**:

  * Se `user.role == 'admin'`: Vai para `PROPOSE_CATEGORY` (Escolhe onde criar).

  * Se `user.role != 'admin'`: Vai direto para `PROPOSE_NAME` e define contexto = '1' (Geral).

## 3. Ajustar `handle_propose_name`

* Garantir que ele leia o contexto corretamente (que pode ter vindo automático como '1' ou escolhido pelo admin).

## 4. Limpeza

* Remover código morto de seleção de categoria para visualização.

