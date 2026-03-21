import os
from src.config import PEDIDOS_DIR, RELATORIOS_DIR

def salvar_txt_pedido(pedido_id, texto_resumo):
    """Salva o pedido individual na pasta data/pedidos"""
    filename = f"pedido_{pedido_id}.txt"
    path = os.path.join(PEDIDOS_DIR, filename)

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(texto_resumo)
        return path
    except Exception as e:
        print(f"Erro ao salvar TXT do pedido: {e}")
        return None

# Futuramente, aqui entraria a lógica de relatório quinzenal lendo do SQLite
def gerar_relatorio_quinzenal():
    pass
