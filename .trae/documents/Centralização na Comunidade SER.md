# Plano: Centralizar na Comunidade SER

## 1. Migração de Dados (Script)
*   Criar `migrate_comunidade_ser.py`.
*   Verificar se o Ministério ID 1 existe.
    *   Se existir, renomear para "Comunidade SER".
    *   Se não, criar com ID 1.
*   Garantir que todos os usuários atuais estejam vinculados a ele (opcional, mas bom para consistência).

## 2. Cadastro Automático (`auth.py`)
*   No registro (`/cadastro`), após criar o usuário:
    *   Buscar Ministério ID 1.
    *   Adicionar à lista `user.ministries`.

## 3. Sugestão de Missão (`webhook.py`)
*   Na função `handle_propose_name`, quando o usuário cria a missão pendente:
    *   Definir `ministry_id=1` explicitamente.

## 4. Ajustes Visuais
*   Onde aparecer "Geral", agora aparecerá "Comunidade SER".