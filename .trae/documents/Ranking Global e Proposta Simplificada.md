# Plano: Ranking Global e Refinamento de Propostas

## 1. Ajuste no Fluxo de Proposta (`webhook.py`)
*   Alterar `handle_propose_name`.
*   **Se Usuário**:
    *   Pula etapa de pontos.
    *   Salva proposta imediatamente com `points=0` e `status='pending'`.
    *   Mensagem: "Proposta enviada! Um Admin definirá a pontuação."
*   **Se Admin**:
    *   Mantém fluxo atual (pede pontos e salva aprovada).

## 2. Ajuste na Aprovação (`webhook.py`)
*   Novo estado: `ADMIN_SET_POINTS`.
*   Ao escolher "1. Aprovar" em uma missão com 0 pontos:
    *   Bot pergunta: "Defina a pontuação para esta missão:".
    *   Só após a resposta, salva como `approved` com os pontos definidos.

## 3. Implementar Ranking no Dashboard (`admin.py` / `dashboard.html`)
*   **Controller**: Consultar Top 10 usuários por pontos.
*   **Template**:
    *   Adicionar seção "🏆 Ranking Global" visível para Admin (e talvez para User também? Por enquanto só Admin pediu).
    *   Exibir posição, nome, insígnia e pontos.