import os
from dotenv import load_dotenv
import streamlit as st
from src.agent_engine import create_agent # Certifique-se de que este caminho está correto

# --- INÍCIO DAS LINHAS DE DEPURACÃO CRÍTICAS ---
# 1. Carrega as variáveis de ambiente do arquivo .env
# Esta linha deve estar no início do seu script principal do Streamlit.
load_dotenv()

# 2. Verifica qual chave está sendo lida por os.getenv()
# Isso nos dirá se o .env foi carregado corretamente e qual valor está disponível.
chave_lida_pelo_streamlit = os.getenv("OPENAI_API_KEY") # ✅ Nome da variável corrigido aqui

print(f"DEBUG STREAMLIT: Chave OpenAI lida por os.getenv(): {chave_lida_pelo_streamlit[:5] if chave_lida_pelo_streamlit else 'NÃO CARREGADA'}...{chave_lida_pelo_streamlit[-5:] if chave_lida_pelo_streamlit else ''}")
print(f"DEBUG STREAMLIT: Tamanho da chave lida por os.getenv(): {len(chave_lida_pelo_streamlit) if chave_lida_pelo_streamlit else '0'}")

# 3. Define a chave da OpenAI para o ambiente, garantindo que o LlamaIndex/OpenAI a utilize.
# O LlamaIndex e a biblioteca OpenAI geralmente leem de os.environ["OPENAI_API_KEY"].
# Definir explicitamente aqui garante que o valor lido do .env seja o que será usado.
if chave_lida_pelo_streamlit:
    os.environ["OPENAI_API_KEY"] = chave_lida_pelo_streamlit # ✅ Nome da variável corrigido aqui
    print("DEBUG STREAMLIT: OPENAI_API_KEY definida em os.environ.")
else:
    print("DEBUG STREAMLIT: ATENÇÃO! OPENAI_API_KEY NÃO FOI LIDA DO .env OU ESTÁ VAZIA.")
# --- FIM DAS LINHAS DE DEPURACÃO CRÍTICAS ---


st.set_page_config(page_title="Bella Maya Admin", layout="wide")

st.title("🍔 Bella Maya - Painel de Teste do Agente")

# Sidebar para configurações
st.sidebar.header("Debug")
chat_id_teste = st.sidebar.text_input("ID do Cliente (Simulação)", "5511999999999@c.us")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do usuário
if prompt := st.chat_input("Digite sua mensagem como se fosse um cliente..."):
    # Adiciona msg do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chama o Agente
    with st.spinner("Agente pensando..."):
        try:
            # O create_agent deve usar a chave que agora está em os.environ
            agent = create_agent(chat_id_teste)
            response = agent.chat(prompt)
            response_text = str(response)

            st.session_state.messages.append({"role": "assistant", "content": response_text})
            with st.chat_message("assistant"):
                st.markdown(response_text)
        except Exception as e:
            st.error(f"Erro no agente: {e}")
