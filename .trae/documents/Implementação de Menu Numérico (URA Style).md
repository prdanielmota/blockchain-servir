# Plano: Navegação por Menu Numérico

## 1. Implementar Menu Principal (`webhook.py`)
*   Criar função `get_main_menu()` que retorna o texto formatado com as opções 1, 2 e 3.
*   Ajustar `process_command` para tratar entradas exatas "1", "2", "3".

## 2. Lógica das Opções
*   **"1"**: Retorna Perfil.
*   **"2"**: Retorna Lista de Ações + Instrução de como realizar.
*   **"3"**: Retorna Ajuda/Instrução ("Digite Fazer + ID").

## 3. Manter Comandos de Texto (Híbrido)
*   Manter o reconhecimento de "Fazer X" para a execução da tarefa, já que a execução exige um parâmetro (o ID da missão) que não cabe num menu simples de 1 nível.
*   Manter palavras-chave como atalho (se o usuário digitar "perfil" em vez de "1", também funciona).

## 4. Fallback
*   Se o usuário digitar algo desconhecido, mostrar o Menu Principal novamente em vez de mensagem de erro.