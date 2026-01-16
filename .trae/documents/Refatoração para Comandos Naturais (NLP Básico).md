# Plano: Interação Natural (Sem Comandos com /)

## 1. Refatorar `process_command` em `webhook.py`
Substituir a lógica rígida de `/` por detecção de palavras-chave.

*   **Intenção: Perfil**
    *   Gatilhos: `perfil`, `pontos`, `minha conta`, `insígnia`, `insignia`.
    *   Ação: Retornar resumo do usuário.

*   **Intenção: Listar Ações**
    *   Gatilhos: `ações`, `acoes`, `missões`, `missoes`, `tarefas`, `lista`.
    *   Ação: Listar ações disponíveis.

*   **Intenção: Realizar Ação**
    *   Gatilhos: `fazer X`, `concluir X`, `realizar X`, `missão X`.
    *   Lógica: Usar Regex para capturar o ID numérico após essas palavras.
    *   Exemplo: "Quero fazer a missão 5" -> Captura ID 5.

*   **Fallback (Menu)**
    *   Se não entender, responder com um texto amigável sugerindo as palavras-chave acima, sem usar barras.

## 2. Teste
*   Verificar se "ver meus pontos" aciona o perfil.
*   Verificar se "fazer 1" registra a ação.