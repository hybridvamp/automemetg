import os
import re
import requests
import time
import random
import sqlite3
import mysql.connector
from pyrogram import Client, enums

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
mysql_url = os.environ.get("MYSQL_URL")
meme_apis = [os.environ.get(f"MEME_API{i}") for i in range(2, 6)]
chat_ids = [int(ch.strip("'")) for ch in os.environ.get('CHAT_ID', '0').split()]
owner_id = int(os.environ.get("OWNER_ID"))
time_gap = int(os.environ.get("TIME_GAP"))

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

conn = mysql.connector.connect(host=mysql_url, user='user', password='password', database='sent_memes_db', autocommit=True)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS sent_memes (url text primary key)''')

with app:
    app.send_message(owner_id, "Bot started!")

def send_meme(chat_id, meme_url, meme_title, meme_api_link):
    try:
        sent_meme = app.send_photo(chat_id, photo=meme_url, caption=meme_title)
        post_link = sent_meme.link
        app.send_message(owner_id, f'Meme sent to chat ID {chat_id}:\n<a href="{post_link}">POST LINK</a> \n\nAPI Used: {meme_api_link}', disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        app.send_message(owner_id, f"Error occurred while sending meme to chat ID {chat_id}: {str(e)} Link: \n\n{meme_api_link}")

while True:
    meme_api_link = random.choice([m for m in meme_apis if m])  # Randomly select an API from those with values
    if not meme_api_link:
        with app:
            app.send_message(owner_id, "No valid MEME_API found. Check your environment variables.")
        time.sleep(time_gap)
        continue
        
    retry_count = 0
    max_retry_count = 5
    while retry_count < max_retry_count:
        try:
            response = requests.get(meme_api_link)
            response.raise_for_status()
            meme_data = response.json()
            meme_title = meme_data["title"]
            meme_url = meme_data["url"]
            c.execute('SELECT url FROM sent_memes WHERE url=%s', (meme_url,))
            if c.fetchone() is not None:
                continue
            with app:
                for chat_id in chat_ids:
                    send_meme(chat_id, meme_url, meme_title, meme_api_link)
            c.execute('INSERT INTO sent_memes (url) VALUES (%s)', (meme_url,))
            break  
        except requests.exceptions.HTTPError as e:
            with app:
                app.send_message(owner_id, f"HTTP error occurred while getting meme from API {meme_api_link}: {str(e)}")
        except Exception as e:
            with app:
                app.send_message(owner_id, f"Error occurred while getting meme from API {meme_api_link}: {str(e)}")
        retry_count += 1
        time.sleep(5)

    if retry_count >= max_retry_count:
        with app:
            app.send_message(owner_id, f"Max retry count exceeded for API {meme_api_link}")

    time.sleep(time_gap)
