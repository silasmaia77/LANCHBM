import sqlite3
from contextlib import contextmanager
from src.config import SQLITE_PATH


def _connect():
    conn = sqlite3.connect(SQLITE_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    # Melhorando concorrência entre processos (webhook + worker)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn


@contextmanager
def get_connection():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        cur = conn.cursor()

        # Idempotência de evento (para não duplicar processamento)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processed_events (
                event_id TEXT PRIMARY KEY,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Mensagens (auditoria simples)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                sender_name TEXT,
                message_text TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                direction TEXT NOT NULL, -- 'in' | 'out'
                processed_by_agent INTEGER DEFAULT 0
            )
        """)

        # Pedidos
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id TEXT PRIMARY KEY,
                chat_id TEXT,
                total REAL,
                metodo_pagamento TEXT,
                endereco TEXT,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Clientes
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                chat_id TEXT PRIMARY KEY,
                nome TEXT,
                telefone TEXT,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)


def is_event_processed(event_id: str) -> bool:
    if not event_id:
        return False
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM processed_events WHERE event_id = ?", (event_id,))
        return cur.fetchone() is not None


def mark_event_processed(event_id: str):
    if not event_id:
        return
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO processed_events (event_id) VALUES (?)",
            (event_id,),
        )


def save_message(
    chat_id: str,
    sender_name: str,
    message_text: str,
    timestamp_iso: str,
    direction: str,
    processed_by_agent: int = 0
):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO messages (chat_id, sender_name, message_text, timestamp, direction, processed_by_agent)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (chat_id, sender_name, message_text, timestamp_iso, direction, processed_by_agent),
        )


def salvar_pedido_db(pedido_id, chat_id, total, metodo_pagamento, endereco):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO pedidos (id, chat_id, total, metodo_pagamento, endereco) VALUES (?, ?, ?, ?, ?)",
            (pedido_id, chat_id, float(total), metodo_pagamento, endereco),
        )


# ✅ NOVAS FUNÇÕES (para corrigir o ImportError do test.ipynb)
def salvar_cliente(chat_id: str, nome: str | None = None, telefone: str | None = None):
    """
    Insere ou atualiza um cliente (UPSERT).
    - Se nome/telefone vierem como None, mantém o valor que já existe no banco.
    """
    if not chat_id:
        raise ValueError("chat_id é obrigatório")

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO clientes (chat_id, nome, telefone)
            VALUES (?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                nome = COALESCE(excluded.nome, clientes.nome),
                telefone = COALESCE(excluded.telefone, clientes.telefone)
            """,
            (chat_id, nome, telefone),
        )


def get_cliente(chat_id: str):
    """
    Busca um cliente pelo chat_id.
    Retorna dict (chat_id, nome, telefone, data_cadastro) ou None.
    """
    if not chat_id:
        return None

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT chat_id, nome, telefone, data_cadastro FROM clientes WHERE chat_id = ?",
            (chat_id,),
        )
        row = cur.fetchone()
        if not row:
            return None

        return {
            "chat_id": row["chat_id"],
            "nome": row["nome"],
            "telefone": row["telefone"],
            "data_cadastro": row["data_cadastro"],
        }


# inicializa ao importar
init_db()