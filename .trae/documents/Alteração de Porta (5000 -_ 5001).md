# Plano de Resolução de Conflito de Porta

## 1. Alterar Porta do Servidor
*   Editar `blockchain_servir/run.py` para usar a porta **5001** em vez de 5000.
*   Isso evita o conflito com o AirPlay do macOS.

## 2. Atualizar Documentação (`N8N_SETUP.md`)
*   Atualizar o guia de integração para indicar a porta 5001 na URL do webhook (`http://SEU_IP:5001/webhook`).
*   Assim você não configura errado no n8n.

## 3. Validar
*   Após a alteração, você poderá rodar o comando novamente e o servidor subirá sem erros.