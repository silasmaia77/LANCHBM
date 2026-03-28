🍔 Bella Maya Bot - Agente de IA para Atendimento via WhatsApp

📌 Descrição
O Bella Maya Bot é um agente de Inteligência Artificial desenvolvido sob medida para automatizar o atendimento ao cliente de uma lanchonete via WhatsApp. Utilizando IA generativa (OpenAI) e processamento assíncrono, o sistema fornece respostas rápidas, naturais e eficientes, guiando o cliente desde a dúvida sobre o cardápio até a finalização do pedido.

A solução foi projetada para garantir que a lanchonete não perca vendas durante os horários de pico, oferecendo uma experiência de atendimento ágil e humanizada 24 horas por dia.

🎯 Problema que resolve
Estabelecimentos do setor alimentício frequentemente enfrentam:

Alto volume de mensagens concentrado em horários de pico (almoço/jantar).
Demora no atendimento, gerando desistência de clientes.
Sobrecarga da equipe de balcão/atendimento.
Erros manuais na anotação de pedidos.
Este agente resolve esses gargalos automatizando a recepção, tirando dúvidas e organizando os pedidos de forma escalável.

⚙️ Funcionalidades

Atendimento 100% Automatizado: Respostas inteligentes e contextualizadas com a persona da lanchonete.
Processamento Assíncrono: Arquitetura baseada em filas (Redis) para suportar múltiplos clientes simultâneos sem travar.
Integração Oficial: Comunicação com o WhatsApp através da engine WAHA (WhatsApp HTTP API).
Persistência de Dados: Salvamento automático de sessões, relatórios e histórico de pedidos (SQLite/Volumes).

Piloto Automático: Reconexão automática da sessão do WhatsApp em caso de reinicialização do servidor.

🧰 Tecnologias Utilizadas

Linguagem: Python 3
Inteligência Artificial: OpenAI API (Modelos GPT)
Mensageria & WhatsApp: WAHA (WhatsApp HTTP API)
Fila de Processamento: Redis
Banco de Dados: SQLite
Infraestrutura: Docker & Docker Compose

🏗️ Arquitetura do Sistema

O projeto é dividido em microsserviços rodando em contêineres Docker:

WAHA: Recebe as mensagens do WhatsApp e envia via Webhook.
API (App): Porta de entrada que recebe o Webhook e coloca a mensagem na fila.
Redis: Gerencia a fila de mensagens para evitar sobrecarga.
Worker: O "cérebro" que consome a fila, processa a resposta com a OpenAI e devolve para o cliente.

🎥 Demonstração
📹 Vídeo do funcionamento: [https://www.youtube.com/watch?v=JLhC9mD5BBg]
Exemplo de Atendimento

🚀 Como Executar o Projeto

1. Pré-requisitos
Docker e Docker Compose instalados na máquina.
Uma chave de API válida da OpenAI.

2. Instalação e Configuração
Clone o repositório para a sua máquina:

bash
Copiar

git clone https://github.com/silasmaia77/LANCHBM.git
cd bellamaya-bot

Crie o arquivo de variáveis de ambiente (.env) na raiz do projeto e preencha com suas credenciais:

OPENAI_API_KEY=sk-proj-sua-chave-aqui
WEBHOOK_TOKEN=sua-senha-de-webhook-aqui

3. Subindo a Infraestrutura
Execute o comando abaixo para construir as imagens e iniciar todos os serviços em segundo plano:

bash
Copiar

docker-compose up -d --build

4. Conectando o WhatsApp

Abra o navegador e acesse o painel do WAHA: http://localhost:3000
Verifique se a sessão default está com o status WORKING.
Caso seja o primeiro acesso, clique em "Play" e leia o QR Code com o WhatsApp da lanchonete.
O sistema já estará pronto para receber mensagens!

📌 Observação

Este projeto foi desenvolvido com foco em aplicação prática de IA em negócios reais do setor gastronômico, mas sua arquitetura robusta permite que seja facilmente adaptado para clínicas, lojas online e prestadores de serviço em geral.

