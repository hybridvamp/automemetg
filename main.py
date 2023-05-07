import os
import requests
import time
from pyrogram import Client, filters

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
OWNER_ID = int(os.environ.get("OWNER_ID"))
CHAT_ID = os.environ.get("CHAT_ID")
TIME_GAP = int(os.environ.get("OWNER_ID")) # 30 minutes in seconds

def get_random_meme():
    response = requests.get("https://meme-api.com/gimme")
    data = response.json()
    title = data["title"]
    image_url = data["url"]
    return image_url, title

def send_meme():
    image_url, title = get_random_meme()
    app.send_photo(CHAT_ID, photo=image_url, caption=title)
    app.send_message(OWNER_ID, "Meme sent successfully!")

def send_start_message():
    app.send_message(OWNER_ID, "Bot started successfully!")

with app:
    send_start_message()
    while True:
        send_meme()
        time.sleep(TIME_GAP)
