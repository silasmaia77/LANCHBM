import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # raiz do projeto
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

SQLITE_PATH = os.getenv("SQLITE_PATH", os.path.join(DATA_DIR, "app.db"))

PEDIDOS_DIR = os.path.join(DATA_DIR, "pedidos")
RELATORIOS_DIR = os.path.join(DATA_DIR, "relatorios")
os.makedirs(PEDIDOS_DIR, exist_ok=True)
os.makedirs(RELATORIOS_DIR, exist_ok=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

WAHA_BASE_URL = os.getenv("WAHA_BASE_URL", "http://localhost:3000").rstrip("/")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")
WAHA_SESSION = os.getenv("WAHA_SESSION", "default")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

KITCHEN_GROUP_ID = os.getenv("KITCHEN_GROUP_ID", "")

WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "")
