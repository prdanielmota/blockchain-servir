# Plano de Implementação: Servir (Completo)

## Fase 1: Infraestrutura e Banco de Dados (SQLite)
1.  **Setup**: Configurar Flask com estrutura de pastas escalável (`templates/`, `static/`, `routes/`).
2.  **Schema do Banco (Models)**:
    *   `User`: id, nome, **email** (novo), whatsapp, senha_hash, role (admin/user), pontos, estagio.
    *   `Action`: id, nome, pontos, tipo, ativa.
    *   `Block`: id, timestamp, user_id, action_id, dados_completos, hash_anterior, hash_atual.
3.  **Inicialização**: Script para criar o banco e um usuário Admin padrão.

## Fase 2: Lógica Core (Blockchain & Gamificação)
1.  **Blockchain Manager**: Classe responsável por inserir blocos garantindo o elo criptográfico (Hash anterior + Dados atuais).
2.  **Engine de Pontos**: Lógica que recalcula o estágio do usuário (Broto -> Árvore) toda vez que um novo bloco é adicionado.

## Fase 3: Web App & Dashboard
1.  **Autenticação Web**: Implementar Login/Logout (sessão) para acesso ao painel.
2.  **Página de Cadastro**: Formulário público para novos jovens (Nome, Email, Zap, Senha).
3.  **Dashboard Admin (MVP)**:
    *   Tabela de Usuários (Visão geral).
    *   Tabela "Blockchain Explorer": Visualizar as ações registradas no sistema em tempo real.
    *   Formulário para Criar Novas Ações.

## Fase 4: Integração WhatsApp (Bot)
1.  **Webhook**: Rota para receber mensagens da Evolution API.
2.  **Identificação**: Cruzar o telefone de quem envia a mensagem com o banco de dados.
3.  **Comandos**: Implementar `/perfil`, `/acoes` e `/fazer`.

## Fase 5: Testes
1.  **Fluxo Completo**: Cadastrar usuário no site -> Logar no Dashboard -> Enviar mensagem simulada do Zap -> Verificar se apareceu no Blockchain do Dashboard.