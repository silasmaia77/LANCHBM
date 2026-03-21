import uuid
from datetime import datetime

def gerar_id_pedido():
    """Gera um ID curto e único para o pedido (ex: #A1B2)."""
    return str(uuid.uuid4())[:4].upper()

def calcular_total_carrinho(itens):
    """Calcula o total numérico dos itens (usado para validação)."""
    total = 0.0
    for item in itens:
        qtd = int(item.get('qtd', 1))
        preco = float(item.get('preco', 0.0))
        total += qtd * preco
    return total

# MUDANÇA AQUI: Renomeei 'total_informado' para 'total' para bater com o notebook
def formatar_resumo_pedido(itens: list, total: float, metodo_pagamento: str, endereco: str, nome_cliente: str):
    """
    Gera um recibo detalhado com cálculos linha a linha.
    """
    linhas = []
    linhas.append(f"🧾 *RESUMO DO PEDIDO - BELLA MAYA*")
    linhas.append(f"👤 Cliente: {nome_cliente}")
    linhas.append(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    linhas.append("-" * 25)

    calculo_total = 0.0

    # Detalhamento item a item
    for item in itens:
        nome = item.get('item', 'Produto')
        qtd = int(item.get('qtd', 1))
        preco_unit = float(item.get('preco', 0.0))
        subtotal = qtd * preco_unit

        calculo_total += subtotal

        # Formatação: "2x X-Salada (R$ 20,00) = R$ 40,00"
        linhas.append(f"{qtd}x {nome}")
        linhas.append(f"   (R$ {preco_unit:.2f}) ➡️ R$ {subtotal:.2f}")

    linhas.append("-" * 25)

    # Verifica se o total bate (segurança matemática)
    if abs(calculo_total - total) > 0.5:
        total_final = calculo_total
    else:
        total_final = total

    linhas.append(f"💰 *TOTAL FINAL: R$ {total_final:.2f}*")
    linhas.append(f"💳 Pagamento: {metodo_pagamento}")
    linhas.append(f"📍 Entrega: {endereco}")
    linhas.append("-" * 25)

    return "\n".join(linhas)
