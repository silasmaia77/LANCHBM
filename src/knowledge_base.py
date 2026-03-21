import os
from functools import lru_cache
from pathlib import Path

import pandas as pd
from llama_index.core.tools import FunctionTool  # <sources>[2]</sources>


# --- FUNÇÃO AUXILIAR PARA ACHAR O ARQUIVO ---
def encontrar_arquivo_cardapio() -> str | None:
    # Base do projeto: tenta usar o arquivo do script; se não existir (ex.: notebook), usa o cwd
    try:
        base_script = Path(__file__).resolve().parent
    except NameError:
        base_script = Path.cwd()

    base_cwd = Path.cwd()

    caminhos_possiveis = [
        base_cwd / "data" / "cardapio.xlsx",                 # pasta atual/data
        base_cwd.parent / "data" / "cardapio.xlsx",          # uma pasta acima/data
        base_script.parent / "data" / "cardapio.xlsx",       # relativo ao script
    ]

    for caminho in caminhos_possiveis:
        if caminho.exists():
            return str(caminho)

    return None


# --- CONFIGURAÇÃO ---
@lru_cache(maxsize=1)
def carregar_dataframe() -> pd.DataFrame | None:
    file_path = encontrar_arquivo_cardapio()

    if not file_path:
        print("❌ ERRO CRÍTICO: cardapio.xlsx não encontrado em nenhuma pasta!")
        return None

    print(f"📂 Cardápio encontrado em: {file_path}")

    try:
        df = pd.read_excel(file_path, dtype=str)

        # Validação mínima de colunas esperadas
        colunas_esperadas = {"Produto", "Descricao", "Preco"}
        faltando = colunas_esperadas - set(df.columns)
        if faltando:
            raise ValueError(f"Planilha sem colunas esperadas: {faltando}. Colunas encontradas: {list(df.columns)}")

        # Limpeza de Preço (remove R$, espaços, troca vírgula por ponto)
        df["Preco"] = (
            df["Preco"]
            .astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace("\xa0", " ", regex=False)   # espaço "estranho" comum em cópia/cola
            .str.replace(",", ".", regex=False)
            .str.strip()
        )
        df["Preco"] = pd.to_numeric(df["Preco"], errors="coerce").fillna(0.0)

        # Cria a Super Coluna de Busca
        df["Busca"] = (
            df["Produto"].astype(str) + " " + df["Descricao"].astype(str)
        ).str.lower()

        return df

    except Exception as e:
        print(f"Erro ao ler Excel: {e}")
        return None


# --- A FUNÇÃO MÁGICA ---
def buscar_no_cardapio(termo_busca: str) -> str:
    """
    Busca itens no cardápio por nome, código ou ingrediente.
    """
    df = carregar_dataframe()
    if df is None:
        return "Erro: Sistema de cardápio indisponível (arquivo não encontrado ou planilha inválida)."

    termo_busca = (termo_busca or "").lower().strip()
    if not termo_busca:
        return "Diga um termo de busca (ex.: 'pizza', 'coca', 'calabresa')."

    palavras_chave = termo_busca.split()

    def contem_todas_palavras(texto_linha: str) -> bool:
        return all(palavra in texto_linha for palavra in palavras_chave)

    resultados = df[df["Busca"].apply(contem_todas_palavras)]

    if resultados.empty:
        def contem_alguma_palavra(texto_linha: str) -> bool:
            return any(palavra in texto_linha for palavra in palavras_chave)

        resultados_leves = df[df["Busca"].apply(contem_alguma_palavra)]

        if not resultados_leves.empty:
            return (
                f"Não achei exatamente '{termo_busca}', mas encontrei estes parecidos:\n"
                + resultados_leves[["Produto", "Descricao", "Preco"]].to_string(index=False)
            )

        return f"Não encontrei nenhum item correspondente a '{termo_busca}' no cardápio."

    texto_resposta = f"Encontrei {len(resultados)} itens para '{termo_busca}':\n\n"
    for _, row in resultados.iterrows():
        texto_resposta += f"- Código/Nome: {row['Produto']}\n"
        texto_resposta += f"  Descrição: {row['Descricao']}\n"
        texto_resposta += f"  Preço: R$ {float(row['Preco']):.2f}\n"
        texto_resposta += "---\n"

    return texto_resposta


def load_menu_tool() -> FunctionTool:
    return FunctionTool.from_defaults(
        fn=buscar_no_cardapio,
        name="consultar_cardapio",
        description="Use esta ferramenta para buscar PREÇOS e ITENS no cardápio."
    )
