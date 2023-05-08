import os
import requests
import time
from pyrogram import Client

api_id = os.environ.get("API_ID")
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")
meme_api_links = os.environ.get("MEME_API").split()
chat_ids = os.environ.get("CHAT_IDS").split()
owner_id = int(os.environ.get("OWNER_ID"))
time_gap = int(os.environ.get("TIME_GAP"))

chat_ids = [int(chat_id) for chat_id in chat_ids]


app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

with app:
    app.send_message(owner_id, "Bot started!")

while True:
    for meme_api_link in meme_api_links:
        try:
            response = requests.get(meme_api_link)
            meme_data = response.json()
            meme_title = meme_data["title"]
            meme_url = meme_data["url"]
            with app:
                for chat_id in chat_ids:
                    sent_meme = app.send_photo(chat_id, photo=meme_url, caption=meme_title)
                    post_link = sent_meme.link
                    app.send_message(owner_id, f'Meme sent to all chat IDs:\n<a href="{post_link}>POST LINK</a>', disable_web_page_preview=True, parse_mode='html')

        except Exception as e:
            with app:
                app.send_message(owner_id, f"Error occurred: {str(e)}")

    time.sleep(time_gap)
