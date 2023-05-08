import os
import re
import requests
import time
import logging

from pyrogram import Client

id_pattern = re.compile(r'^.\d+$')

def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

api_id = os.environ.get("API_ID")
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")
meme_api_links = os.environ.get("MEME_API").split()
chat_ids = [int(ch) if id_pattern.search(ch) else ch for ch in os.environ.get('CHAT_ID', '0').split()]
owner_id = int(os.environ.get("OWNER_ID"))
time_gap = int(os.environ.get("TIME_GAP"))

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

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
                    app.send_message(owner_id, f'Meme sent to chat ID {chat_id}:\n<a href="{post_link}">POST LINK</a>', disable_web_page_preview=True, parse_mode='html')

        except requests.exceptions.ConnectionError as e:
            logging.error(f'Connection error occurred while accessing {meme_api_link}: {str(e)}')
        except KeyError as e:
            logging.error(f'Key error occurred while processing the meme data from {meme_api_link}: {str(e)}')
        except Exception as e:
            logging.error(f"Error occurred while processing the meme data from {meme_api_link}: {str(e)}")

    time.sleep(time_gap)
