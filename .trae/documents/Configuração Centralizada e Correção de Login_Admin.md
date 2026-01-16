# Plano: Configuração Centralizada e Correção de Login

## 1. Criar Arquivo de Configuração (`config.py`)
Criar um arquivo `config.py` na raiz com:
*   `BASE_URL`: URL base do sistema (ex: `http://localhost:5001`).
*   `SQLALCHEMY_DATABASE_URI`: Caminho **absoluto** para o arquivo `servir.db` (evita problemas de pasta).
*   `SECRET_KEY`: Chave de segurança.

## 2. Refatorar Aplicação para Usar Config
*   Atualizar `blockchain_servir/app/__init__.py` para ler do `config.py`.
*   Atualizar `blockchain_servir/app/routes/webhook.py` para usar a `BASE_URL` nas mensagens do Bot.

## 3. Implementar "Primeiro Usuário é Admin"
*   Modificar `blockchain_servir/app/routes/auth.py`.
*   Ao registrar: Verificar se a tabela de usuários está vazia. Se estiver, o novo usuário ganha `role='admin'`.

## 4. Teste e Validação
*   Você tentará se cadastrar novamente.
*   Dessa vez, como o caminho do banco será absoluto, teremos certeza que está salvando no lugar certo.
*   Seu usuário será Admin e o login funcionará.