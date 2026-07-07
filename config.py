import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', '0'))

UPDATE_INTERVAL = 300

COLORS = {
    'weather': 0x1f8b4c,
    'football': 0xffc72c,
    'lottery': 0xff6b6b,
    'currency': 0x4ecdc4,
    'oil': 0x2ecc71,
    'school': 0x3498db,
    'joke': 0xff9ff3,
}
