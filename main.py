import os
import re
import requests
import time
import random

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
chat_ids = int(os.environ.get('CHAT_ID', '0').split())
owner_id = int(os.environ.get("OWNER_ID"))
time_gap = int(os.environ.get("TIME_GAP"))

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

with app:
    app.send_message(owner_id, "Bot started!")

def send_meme(chat_id, meme_url, meme_title):
    try:
        sent_meme = app.send_photo(chat_id, photo=meme_url, caption=meme_title)
        post_link = sent_meme.link
        app.send_message(owner_id, f'Meme sent to chat ID {chat_id}:\n<a href="{post_link}">POST LINK</a>', disable_web_page_preview=True, parse_mode='html')
    except Exception as e:
        app.send_message(owner_id, f"Error occurred while sending meme to chat ID {chat_id}: {str(e)}")

while True:
    meme_api_link = random.choice(meme_api_links)
    retry_count = 0
    max_retry_count = 5
    while retry_count < max_retry_count:
        try:
            response = requests.get(meme_api_link)
            response.raise_for_status()  # raise an exception for non-2xx status codes
            meme_data = response.json()
            meme_title = meme_data["title"]
            meme_url = meme_data["url"]
            with app:
                for chat_id in chat_ids:
                    send_meme(chat_id, meme_url, meme_title)
            break  # break out of the retry loop if the API call was successful
        except requests.exceptions.HTTPError as e:
            with app:
                app.send_message(owner_id, f"HTTP error occurred while getting meme from API {meme_api_link}: {str(e)}")
        except Exception as e:
            with app:
                app.send_message(owner_id, f"Error occurred while getting meme from API {meme_api_link}: {str(e)}")

        retry_count += 1
        time.sleep(5)  # wait for 5 seconds before retrying

    if retry_count >= max_retry_count:
        with app:
            app.send_message(owner_id, f"Max retry count exceeded for API {meme_api_link}")

    time.sleep(time_gap)
