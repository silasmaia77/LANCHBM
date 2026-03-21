from llama_index.core.tools import FunctionTool
from src.database import salvar_pedido_db, salvar_cliente
from src.knowledge_base import load_menu_tool
import uuid
import os
import requests
import json
import base64
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
WAHA_BASE_URL = os.getenv("WAHA_BASE_URL", "http://localhost:3000")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")
GRUPO_COZINHA_ID = os.getenv("GRUPO_COZINHA_ID", "")

# --- 1. Carrega Cardápio ---
menu_tool = load_menu_tool()

# --- 2. Registrar Cliente ---
def registrar_cliente_action(chat_id: str, nome: str, telefone: str = None):
    try:
        salvar_cliente(chat_id, nome, telefone)
        return f"Cliente {nome} registrado."
    except Exception as e:
        print(f"⚠️ Erro ao registrar cliente: {e}")
        return "Erro ao registrar cliente, mas pode prosseguir."

cliente_tool = FunctionTool.from_defaults(
    fn=registrar_cliente_action,
    name="registrar_cliente",
    description="Registra nome do cliente."
)

# --- AUXILIAR: ENVIAR MENSAGEM ---
def enviar_notificacao_waha(chat_id_destino, mensagem):
    if not chat_id_destino: return
    url = f"{WAHA_BASE_URL}/api/sendText"
    headers = {"Content-Type": "application/json", "X-Api-Key": WAHA_API_KEY}
    payload = {"chatId": chat_id_destino, "text": mensagem, "session": "default"}
    try: requests.post(url, json=payload, headers=headers)
    except Exception as e: print(f"❌ Erro Waha Text: {e}")

# --- AUXILIAR: ENVIAR ARQUIVO (NOVO!) ---
def enviar_arquivo_waha(chat_id_destino, caminho_arquivo):
    if not chat_id_destino or not os.path.exists(caminho_arquivo): return

    url = f"{WAHA_BASE_URL}/api/sendFile"
    headers = {"Content-Type": "application/json", "X-Api-Key": WAHA_API_KEY}

    # Converte para Base64 para enviar via API
    with open(caminho_arquivo, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')

    payload = {
        "chatId": chat_id_destino,
        "file": {
            "mimetype": "text/plain",
            "filename": os.path.basename(caminho_arquivo),
            "data": encoded_string
        },
        "session": "default"
    }
    try:
        print(f"📤 Enviando arquivo TXT para {chat_id_destino}...")
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"❌ Erro Waha File: {e}")

# --- 3. Finalizar Pedido ---
def finalizar_pedido_action(metodo_pagamento: str, endereco: str, total: float, chat_id: str = "cliente_web", resumo_pedido: str = None, itens: list = None, **kwargs):
    """
    Finaliza o pedido, salva no banco, gera TXT e envia para a cozinha.
    """
    nome_cliente = kwargs.get('nome', 'Cliente')
    print(f"\n🛒 PROCESSANDO PEDIDO DE: {nome_cliente}")

    # Formata Itens
    texto_itens = ""
    if itens and isinstance(itens, list):
        for item in itens:
            texto_itens += f"- {item.get('qtd', 1)}x {item.get('item', 'Item')} (R$ {item.get('preco', 0):.2f})\n"
    elif resumo_pedido:
        texto_itens = resumo_pedido
    else:
        texto_itens = "Itens não especificados."

    pedido_id = str(uuid.uuid4())[:8]
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Salva Banco
    try: salvar_pedido_db(pedido_id, chat_id, total, metodo_pagamento, endereco)
    except: pass

    # Texto Final
    texto_final = (
        f"🔥 *PEDIDO #{pedido_id}* - {data_hora}\n"
        f"👤 {nome_cliente} ({chat_id})\n"
        f"-----------------------\n"
        f"{texto_itens}\n"
        f"-----------------------\n"
        f"💰 TOTAL: R$ {total:.2f}\n"
        f"💳 PAGTO: {metodo_pagamento}\n"
        f"📍 LOCAL: {endereco}\n"
    )

    # Salva TXT
    caminho_txt = ""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        pasta_pedidos = os.path.join(os.path.dirname(base_dir), "data", "pedidos")
        os.makedirs(pasta_pedidos, exist_ok=True)
        caminho_txt = os.path.join(pasta_pedidos, f"pedido_{pedido_id}.txt")
        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write(texto_final)
    except: pass

    # Envia para Cozinha (Texto + Arquivo)
    enviar_notificacao_waha(GRUPO_COZINHA_ID, texto_final)
    if caminho_txt:
        enviar_arquivo_waha(GRUPO_COZINHA_ID, caminho_txt)

    return f"Pedido #{pedido_id} confirmado! A cozinha já recebeu."

pedido_tool = FunctionTool.from_defaults(
    fn=finalizar_pedido_action,
    name="finalizar_pedido",
    description="Finaliza o pedido. Requer: total, metodo_pagamento, endereco."
)

all_tools = [menu_tool, cliente_tool, pedido_tool]
