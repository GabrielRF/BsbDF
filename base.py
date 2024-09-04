import os
import requests
import shutil
import sqlite3
from atproto import Client, client_utils
from bs4 import BeautifulSoup

def add_to_history(link):
    conn = sqlite3.connect('links_history.db')
    cursor = conn.cursor()
    aux = f'INSERT INTO history (link) VALUES ("{link}")'
    cursor.execute(aux)
    conn.commit()
    conn.close()

def check_history(link):
    conn = sqlite3.connect('links_history.db')
    cursor = conn.cursor()
    aux = f'SELECT * from history WHERE link="{link}"'
    cursor.execute(aux)
    data = cursor.fetchone()
    conn.close()
    return data

def get_post_photo(url):
    response = requests.get(
        url,
        headers = {'User-agent': 'Mozilla/5.1'},
        timeout=3,
        verify=False
    )
    html = BeautifulSoup(response.content, 'html.parser')
    photo = html.find('meta', {'property': 'og:image'})['content']
    return photo

def bluesky_post(author, title, link):
    client = Client(base_url='https://bsky.social')
    client.login('bsbdf.grf.xyz', os.environ.get('BLUESKY_PASSWORD'))
    text_builder = client_utils.TextBuilder()
    text_builder.link(
        f'{author}\n{title}',
        link
    )
    try:
        photo = get_post_photo(link)
        file_name = photo.split("/")[-1]
        with requests.get(photo, stream=True) as r:
            with open(photo.split("/")[-1], 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        with open(file_name, 'rb') as f:
            image_data = f.read()
        client.send_image(
            text=text_builder,
            image=image_data,
            image_alt=title,
        )
        os.remove(file_name)
    except:
        client.send_post(
            text_builder
        )
