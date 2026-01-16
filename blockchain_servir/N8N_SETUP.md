# Guia de Integração: n8n -> Servir

Para conectar seu fluxo do **n8n** ao nosso backend Python, siga estes passos para configurar o nó final de envio.

## 1. Nó HTTP Request (No n8n)

No final do seu fluxo (após receber a mensagem da Evolution API), adicione um nó **HTTP Request** com as seguintes configurações:

*   **Method**: `POST`
*   **URL**: `http://SEU_IP_OU_DOMINIO:5001/webhook`
    *   *Nota: Se o Python estiver rodando no mesmo servidor do n8n (via Docker), você pode usar o IP interno ou o nome do container.*
*   **Authentication**: None (Por enquanto)
*   **Send Body**: Ativado (`True`)
*   **Body Content Type**: `JSON`
*   **Specify Body**: `Using JSON`

### JSON Body (O que enviar)
Copie e cole exatamente este JSON no campo do corpo da requisição no n8n. Use as expressões (Expression) do n8n para preencher os valores dinâmicos.

```json
{
  "remoteJid": "{{ $json.body.data.key.remoteJid }}",
  "text": "{{ $json.body.data.message.conversation || $json.body.data.message.extendedTextMessage.text }}"
}
```

*Ajuste as variáveis `{{ ... }}` conforme a estrutura que o seu nó anterior da Evolution API entrega.*

## 2. O que o Backend Python Retorna?

O Python vai processar a mensagem e devolver um JSON com a resposta que o bot deve enviar de volta ao usuário.

**Exemplo de Resposta de Sucesso:**
```json
{
  "reply": "👤 *Daniel*\n🏆 Estágio: 🌱 Broto\n⭐ Pontos: 50"
}
```

## 3. Próximo Passo no n8n (Enviar Resposta)

Depois do nó HTTP Request (que chama o Python), adicione outro nó (Evolution API ou HTTP Request) para **enviar a mensagem de volta ao WhatsApp**.

*   Use o valor `{{ $json.reply }}` retornado pelo Python como o texto da mensagem a ser enviada.
