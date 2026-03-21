import os
import json
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from src.queue import enqueue_incoming
from src.database import init_db  # garante DB pronto

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
load_dotenv()

init_db()

app = Flask(__name__)

def _get_event_id(message_data: dict) -> str:
    """
    Tentamos extrair um ID estável para idempotência.
    """
    if not message_data:
        return ""

    msg_id = message_data.get("id")
    # O WAHA às vezes manda o ID como um dicionário, vamos garantir que pegamos a string
    if isinstance(msg_id, dict):
        return msg_id.get("_serialized", "")

    return str(msg_id or message_data.get("_id") or message_data.get("messageId") or "")

@app.get("/health")
def health():
    return jsonify({"ok": True}), 200

@app.route("/webhook", methods=["POST"])
def webhook():
    # 1) Segurança: validar token
    expected = os.getenv("WEBHOOK_TOKEN", "")
    token = request.headers.get("X-Webhook-Token", "")

    if expected and token != expected:
        logging.warning("Webhook rejeitado: X-Webhook-Token inválido/ausente.")
        return jsonify({"status": "unauthorized"}), 401

    # 2) Parse JSON
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "JSON vazio/inválido"}), 400

    logging.info(f"Webhook recebido: {json.dumps(data, ensure_ascii=False)[:2000]}")

    # 3) Só processa evento de mensagem
    if data.get("event") != "message":
        return jsonify({"status": "ignored", "reason": "not_message_event"}), 200

    # CORREÇÃO AQUI: O WAHA envia os dados dentro de "payload"
    message_data = data.get("payload") or {}

    # CORREÇÃO AQUI: O texto vem direto no "body"
    msg_body = message_data.get("body") or ""
    chat_id = message_data.get("from")
    from_me = message_data.get("fromMe", False)

    # Ignora mensagens enviadas por você mesmo
    if from_me:
        return jsonify({"status": "ignored", "reason": "fromMe"}), 200

    # Ignora status do WhatsApp
    if chat_id and "status@broadcast" in chat_id:
        return jsonify({"status": "ignored", "reason": "broadcast"}), 200

    # Ignora mensagens de grupos
    if chat_id and "@g.us" in chat_id:
        return jsonify({"status": "ignored", "reason": "group_message"}), 200

    # Se não tiver texto ou chat_id, ignora
    if not msg_body or not chat_id:
        return jsonify({"status": "ignored", "reason": "missing_body_or_chat_id"}), 200

    # 4) Enfileirar pro worker
    event_id = _get_event_id(message_data)

    enqueue_incoming({
        "event_id": event_id,
        "chat_id": chat_id,
        "text": msg_body,
    })

    # 5) responder rápido
    return jsonify({"status": "queued"}), 200