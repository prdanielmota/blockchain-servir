# Plano: Correção do Nono Dígito e UX

## 1. Lógica de Busca Flexível (`webhook.py`)
Alterar a busca de usuário para tentar duas variações:
*   **Tentativa 1**: Busca pelo número exato recebido (ex: `559288888888`).
*   **Tentativa 2**: Se falhar e o número tiver 12 dígitos, insere o '9' após o DDD (posição 4) e busca novamente (ex: `5592988888888`).
*   Isso garante que o sistema encontre o usuário independente de como o WhatsApp reporta o ID.

## 2. Link de Cadastro com Telefone (`webhook.py`)
*   Se não encontrar o usuário em nenhuma das tentativas, gerar o link de cadastro passando o número recebido como parâmetro: `?phone=5592...`.

## 3. Receber Telefone no Formulário (`auth.py` / `register.html`)
*   No `GET /cadastro`, pegar o parâmetro `phone` da URL.
*   Preencher automaticamente o campo `<input name="phone">` no HTML.
*   O usuário apenas confirma a senha e nome, agilizando o processo.

## 4. Sanitização no Salvamento (`auth.py`)
*   Garantir que, ao salvar, limpamos caracteres especiais `( ) - +` para manter o banco consistente apenas com números.