# Plano: Correção da Variável prefill_phone

## 1. Ajuste em `auth.py`
*   Mover a definição de `prefill_phone` para o escopo global da função `register`, garantindo que ela exista tanto no GET quanto no POST.
*   Isso resolve o `NameError` e permite que o cadastro funcione tanto vindo do link do WhatsApp quanto digitado diretamente no navegador.

## 2. Validação
*   O erro não deve mais ocorrer ao submeter o formulário.