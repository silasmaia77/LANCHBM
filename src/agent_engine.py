import os
import requests
from datetime import datetime
from dotenv import load_dotenv

from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.tools import FunctionTool
from llama_index.core.memory import ChatMemoryBuffer

from src.knowledge_base import load_menu_tool
from src.database import salvar_pedido_db
from src.config import WAHA_BASE_URL, WAHA_API_KEY, KITCHEN_GROUP_ID, PEDIDOS_DIR

load_dotenv()

_user_sessions = {}

def _waha_headers():
    h = {"Content-Type": "application/json"}
    if WAHA_API_KEY:
        h["X-Api-Key"] = WAHA_API_KEY
    return h

def _enviar_para_cozinha(texto: str):
    if not KITCHEN_GROUP_ID:
        return
    url = f"{WAHA_BASE_URL}/api/sendText"
    payload = {"chatId": KITCHEN_GROUP_ID, "text": texto, "session": os.getenv("WAHA_SESSION", "default")}
    try:
        requests.post(url, json=payload, headers=_waha_headers(), timeout=8)
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem para cozinha via WAHA: {e}")

def _salvar_txt(pedido_id: str, texto: str):
    try:
        path = os.path.join(PEDIDOS_DIR, f"pedido_{pedido_id}.txt")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(texto)
    except Exception as e:
        print(f"❌ Erro ao salvar TXT do pedido: {e}")

def create_agent(chat_id: str):
    global _user_sessions

    if chat_id in _user_sessions:
        return _user_sessions[chat_id]

    menu_tool = load_menu_tool()

    # Tool com closure capturando chat_id (o LLM não precisa passar chat_id)
    # Adicionamos o parâmetro 'observacoes' aqui!
    def finalizar_pedido_action(nome: str, itens: str, observacoes: str, total: float, pagamento: str, endereco: str):
        pedido_id = datetime.now().strftime("%Y%m%d%H%M%S")
        data_hora_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")

        resumo_completo = (
            f"✅ *PEDIDO CONFIRMADO* #{pedido_id}\n"
            f"📅 *Data/Hora:* {data_hora_atual}\n"
            f"👤 *Cliente:* {nome}\n"
            f"📍 *Endereço:* {endereco}\n"
            f"--------------------------------\n"
            f"🍔 *ITENS DO PEDIDO:*\n{itens}\n"
            f"--------------------------------\n"
            f"📝 *OBSERVAÇÕES PARA A COZINHA:*\n{observacoes}\n"
            f"--------------------------------\n"
            f"💰 *TOTAL:* R$ {total:.2f}\n"
            f"💳 *Pagamento:* {pagamento}\n"
            f"--------------------------------\n"
            f"🚀 *Status:* Enviado para a cozinha! Aguarde a entrega. 😋"
        )

        # --- LÓGICA DO PIX DIRETO NO CÓDIGO ---
        if "pix" in pagamento.lower():
            resumo_completo += (
                "\n\n📲 *PAGAMENTO VIA PIX:*\n"
                "Por favor, acesse o link abaixo para gerar seu código Pix:\n"
                "👉 https://pagamento.bellamaya.com.br/pix/gerar\n\n"
                "⚠️ *IMPORTANTE:* Você pode me enviar o comprovante por aqui ou apresentar para o entregador na hora da entrega! 🏍️"
            )
        # ------------------------------------------

        try:
            # Mantemos a chamada do DB original para não quebrar seu banco de dados
            salvar_pedido_db(pedido_id, chat_id, total, pagamento, endereco)
        except Exception as e:
            print(f"❌ Erro ao salvar pedido no DB: {e}")

        _salvar_txt(pedido_id, resumo_completo)
        _enviar_para_cozinha(resumo_completo)
        return resumo_completo

    pedido_tool = FunctionTool.from_defaults(fn=finalizar_pedido_action, name="finalizar_pedido")

    system_prompt = """
Você é o atendente virtual da *Lanchonete Bella Maya*.
Seu tom de voz deve ser sempre profissional, muito educado, prestativo e utilizar emojis (🍔, ✅, 🍟, 🥤).

REGRAS DE ATENDIMENTO (SIGA O PASSO A PASSO RIGOROSAMENTE):

PASSO 1 - SAUDAÇÃO: Ao receber um cumprimento, dê as boas-vindas e pergunte o nome do cliente.
PASSO 2 - CARDÁPIO: Se pedirem, envie o link: https://encurtador.com.br/FitY
PASSO 3 - CONSULTA OBRIGATÓRIA (PREÇOS E INGREDIENTES): 
   - ASSIM QUE O CLIENTE PEDIR QUALQUER ITEM (lanches, bebidas, sobremesas), você DEVE usar a ferramenta de cardápio para buscar o NOME CORRETO, PREÇO EXATO e INGREDIENTES. 
   - É ESTRITAMENTE PROIBIDO adivinhar preços ou nomes. Leia a planilha sempre!
   - DICA DE BUSCA: O cliente pode digitar errado (ex: "coa" em vez de "coca"). Se a ferramenta não achar de primeira, pesquise por termos genéricos como "Refrigerante", "Lata" ou "Coca". Seja persistente!
PASSO 4 - RESUMO E OBSERVAÇÕES (MUITO IMPORTANTE): 
   - Liste os itens pedidos com os INGREDIENTES entre parênteses. Ex: "1x *BM10 - Americano* (Presunto, mussarela, ovo e bacon) - R$ 30,00".
   - Mostre a matemática clara (ex: 2x R$ 30,00 = R$ 60,00) e o Total.
   - OBRIGATÓRIO: Após mostrar o total, VOCÊ DEVE PERGUNTAR se o cliente tem alguma observação para a cozinha (ex: tirar cebola, ponto da carne, enviar maionese). NÃO peça o endereço ainda. Espere o cliente responder.
PASSO 5 - ENDEREÇO E PAGAMENTO: Após o cliente responder sobre as observações, peça o endereço completo de entrega e a forma de pagamento.
PASSO 6 - FINALIZAÇÃO E ENVIO PARA COZINHA: 
   - Use a ferramenta 'finalizar_pedido'.
   - FORMATAÇÃO DOS ITENS: "[Quantidade]x [Código] - [Nome do Item] ([Ingredientes])". NUNCA coloque as observações misturadas aqui nos itens.
   - CAMPO OBSERVAÇÕES: Passe todas as observações do cliente (ex: "Enviar maionese verde e ketchup", "Sem cebola no BM10") no campo específico 'observacoes' da ferramenta. Se não houver, escreva "Nenhuma".
   - A ferramenta vai gerar um recibo completo. Comece a sua última mensagem dizendo: "✅ *Pedido Confirmado!* O número do seu pedido é [INSERIR NÚMERO AQUI]". Em seguida, mostre EXATAMENTE todo o texto que a ferramenta gerou.

REGRAS DE FORMATAÇÃO PARA O WHATSAPP (MUITO IMPORTANTE):
- Você está conversando pelo WhatsApp. 
- NUNCA use formatação Markdown padrão como asteriscos duplos (**texto**) ou hashtags (###).
- Para destacar palavras em negrito, use APENAS um asterisco de cada lado: *texto*.
- Para itálico, use APENAS underline: _texto_.
    """.strip()

    agent = OpenAIAgent.from_tools(
        tools=[menu_tool, pedido_tool],
        llm=OpenAI(model="gpt-4o-mini", temperature=0),
        memory=ChatMemoryBuffer.from_defaults(token_limit=4000),
        system_prompt=system_prompt,
        verbose=True,
    )

    _user_sessions[chat_id] = agent
    return agent
