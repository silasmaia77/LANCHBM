import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Pega as configurações exatas que o robô está usando
WAHA_BASE_URL = os.getenv("WAHA_BASE_URL", "http://localhost:3000")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")
KITCHEN_GROUP_ID = os.getenv("KITCHEN_GROUP_ID", "")

def testar_envio():
    print("🔥 INICIANDO TESTE DE ENVIO PARA COZINHA 🔥")
    print(f"📡 URL: {WAHA_BASE_URL}")
    print(f"🆔 ID Configurado: {KITCHEN_GROUP_ID}")

    if not KITCHEN_GROUP_ID:
        print("❌ ERRO: O ID do grupo está vazio no arquivo .env!")
        return

    url = f"{WAHA_BASE_URL}/api/sendText"
    headers = {"Content-Type": "application/json"}
    if WAHA_API_KEY: headers["X-Api-Key"] = WAHA_API_KEY

    # Tenta mandar mensagem
    payload = {
        "chatId": KITCHEN_GROUP_ID,
        "text": "🔔 TESTE DE COZINHA: Se você ler isso, a configuração está certa! 🔔",
        "session": "default"
    }

    try:
        print("🚀 Enviando mensagem...")
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 201 or response.status_code == 200:
            print("✅ SUCESSO! O servidor aceitou a mensagem.")
            print("👉 Verifique agora no WhatsApp do grupo se chegou.")
        else:
            print(f"❌ FALHA: O servidor respondeu com erro {response.status_code}")
            print(f"Detalhe: {response.text}")

    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")

if __name__ == "__main__":
    testar_envio()
