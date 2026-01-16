# Plano de Integração via n8n

## 1. Simplificar/Adaptar Webhook do Python
*   Alterar `blockchain_servir/app/routes/webhook.py`.
*   **Nova Lógica**: Aceitar tanto o formato direto da Evolution (complexo) quanto um formato simplificado (limpo) vindo do n8n.
*   **Campos esperados do n8n**: `remoteJid` (quem enviou) e `text` (mensagem) ou `message`.

## 2. Documentação para o n8n (`N8N_SETUP.md`)
Criar um guia rápido de como configurar o nó final do seu fluxo n8n:
*   **Método**: POST.
*   **URL**: A URL onde você vai hospedar este Python.
*   **Body**: JSON com `{ "remoteJid": "...", "text": "..." }`.

## 3. Ajuste de Execução
*   Configurar `run.py` para rodar em modo acessível (`host='0.0.0.0'`) para facilitar a conexão.

Dessa forma, você mantém seu n8n como gateway e o Python foca na lógica de negócio (Gamificação/Blockchain).