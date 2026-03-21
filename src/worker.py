import logging
from datetime import datetime

from src.queue import dequeue_incoming
from src.database import (
    is_event_processed,
    mark_event_processed,
    save_message,
)
from src.waha_client import send_message
from src.agent_engine import create_agent

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def _now_iso():
    return datetime.now().isoformat()

def run_forever():
    logging.info("🧵 Worker iniciado. Aguardando jobs...")

    while True:
        job = dequeue_incoming(block_seconds=10)
        if not job:
            continue

        event_id = job.get("event_id") or ""
        chat_id = job.get("chat_id") or ""
        text = job.get("text") or ""

        if not chat_id or not text:
            logging.warning(f"Job inválido (sem chat_id/text): {job}")
            continue

        if event_id and is_event_processed(event_id):
            logging.info(f"Evento já processado (idempotência): {event_id}")
            continue

        try:
            # marca no começo para evitar duplicar em caso de retry do webhook
            if event_id:
                mark_event_processed(event_id)

            logging.info(f"Processando chat={chat_id} text={text[:80]!r}")

            save_message(chat_id, "Cliente", text, _now_iso(), "in", processed_by_agent=0)

            agent = create_agent(chat_id)
            resposta = agent.chat(text)
            response_text = str(resposta)

            # envia
            send_message(chat_id, response_text)

            save_message(chat_id, "Agente Bella Maya", response_text, _now_iso(), "out", processed_by_agent=1)

            logging.info(f"✅ Respondido chat={chat_id}")

        except Exception as e:
            # Se quiser retries de worker: aqui entra backoff + requeue
            logging.error(f"❌ Erro ao processar job: {e}", exc_info=True)

if __name__ == "__main__":
    run_forever()
