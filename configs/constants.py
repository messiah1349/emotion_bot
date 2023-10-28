import os
from dotenv import load_dotenv

load_dotenv()

TZ = 'Europe/Helsinki'
API_TOKEN = os.getenv('EMOTION_BOT_TOKEN', '') 
