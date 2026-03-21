import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações
WAHA_BASE_URL = os.getenv("WAHA_BASE_URL", "http://localhost:3000")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")

def buscar_grupos_final():
    # Usando a rota que descobrimos que funciona no seu print
    url = f"{WAHA_BASE_URL}/api/default/chats"

    print(f"📡 Conectando direto na rota certa: {url}...\n")

    headers = {"Content-Type": "application/json"}
    if WAHA_API_KEY: headers["X-Api-Key"] = WAHA_API_KEY

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            chats = response.json()
            encontrou = False

            print("👇 SEUS GRUPOS ENCONTRADOS:")
            print("=" * 50)

            for chat in chats:
                # Pega o ID (tenta vários formatos para garantir)
                chat_id = chat.get('id', '')
                if isinstance(chat_id, dict): chat_id = chat_id.get('_serialized', '')

                # SÓ MOSTRA SE FOR GRUPO (termina com @g.us)
                if chat_id.endswith('@g.us'):
                    nome = chat.get('name', '(Sem Nome)')
                    print(f"📂 NOME: {nome}")
                    print(f"🆔 ID:   {chat_id}")
                    print("-" * 50)
                    encontrou = True

            if not encontrou:
                print("⚠️ Nenhum grupo apareceu na lista.")
                print("DICA DE OURO: Pegue o celular do robô e mande um 'Oi' dentro do grupo novo.")
                print("Isso faz o grupo subir para o topo da lista. Depois rode este script de novo.")

        else:
            print(f"❌ Erro: {response.status_code}")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    buscar_grupos_final()
