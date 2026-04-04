import base
import io
import os
import requests
import telebot
import urllib
from bs4 import BeautifulSoup

def get_news_list():
    response = requests.get('https://www.bsb.aero/passageiros/noticias')
    if response.status_code != 200:
        return False
    return BeautifulSoup(response.content, 'html.parser')

def get_news_content(link):
    post = {}
    response = requests.get(f'https://www.bsb.aero{link}')
    if response.status_code != 200:
        return False
    response = BeautifulSoup(response.content, 'html.parser')
    html = response.find('section')
    post['title'] = html.find('h1').text.strip()
    post['link'] = f'https://www.bsb.aero{link}'
    return post

def send_message(post, iv_link):
    bot = telebot.TeleBot(os.environ.get(f'BOT_TOKEN'))
    bot.send_message(
        os.environ.get(f'DESTINATION'),
        f'<a href="{iv_link}">󠀠</a><b>{post["title"]}</b>\n' + 
        f'✈️ <a href="{post["link"]}">Site Bsb.Aero</a>',
        parse_mode='HTML'
    )

if __name__ == "__main__":
    html = get_news_list()
    for noticia in html.find_all('a'):
        if 'noticia' not in noticia['href']:
            continue
        link = f"{noticia['href']}"
        if base.check_history(link):
            continue
        post = get_news_content(link)
        iv_link = f'https://t.me/iv?url={urllib.parse.quote_plus(link)}&rhash=7a780507b3d9ea'
        send_message(post, iv_link)
        base.add_to_history(link)
