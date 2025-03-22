import os
from dotenv import load_dotenv

load_dotenv()

SECURITY_BOT_TOKEN = os.getenv("SECURITY_BOT_TOKEN")
WAITER_BOT_TOKEN = os.getenv("WAITER_BOT_TOKEN")
