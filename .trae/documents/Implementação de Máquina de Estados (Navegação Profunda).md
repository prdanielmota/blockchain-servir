# Plano: Máquina de Estados (Navegação por Menus)

## 1. Atualizar Banco de Dados
*   Adicionar campos `menu_state` (default: 'MAIN') e `menu_context` (para guardar o ID da missão selecionada) na tabela `User`.
*   Criar script de migração simples para atualizar o banco existente.

## 2. Refatorar Lógica do Bot (`webhook.py`)
*   Substituir `process_command` por uma Máquina de Estados.
*   **Estado MAIN**:
    *   1 -> Mostra Perfil (fica em MAIN).
    *   2 -> Muda estado para `MISSIONS_LIST`. Mostra lista.
    *   3 -> Muda estado para `PROPOSE_MISSION`. Pede texto.
*   **Estado MISSIONS_LIST**:
    *   N -> Seleciona missão N da lista temporária. Muda estado para `MISSION_DETAIL`.
    *   0 -> Voltar para MAIN.
*   **Estado MISSION_DETAIL**:
    *   1 -> Executa Missão (Blockchain). Volta para MAIN com mensagem de sucesso.
    *   2 -> Volta para MISSIONS_LIST.
    *   0 -> Volta para MAIN.

## 3. Implementar Navegação
*   Cada resposta do bot atualiza o estado do usuário no banco antes de retornar o texto.
*   Garantir que opção "0" ou "Voltar" sempre funcione.

## 4. Teste
*   Validar o fluxo completo sem digitar nenhum comando de texto, apenas números.