import base
import os
import requests
import telebot
import urllib
from bs4 import BeautifulSoup

def get_news_list():
    try:
        response = requests.get('https://www.agenciabrasilia.df.gov.br/noticias/', timeout=5, headers={'User-agent': 'Mozilla/5.1'})
    except requests.exceptions.Timeout:
        return False
    if response.status_code != 200:
        return False
    return BeautifulSoup(response.content, 'html.parser')

def send_message(title, iv_link, link):
    bot = telebot.TeleBot(os.environ.get(f'BOT_TOKEN'))
    bot.send_message(
        os.environ.get(f'DESTINATION'),
        f'<b>{title}</b>\n' 
        f'🗞 <a href="{link}">Site Agência Brasília</a>',
        parse_mode='HTML',
        link_preview_options=telebot.types.LinkPreviewOptions(
            prefer_large_media=True,
            show_above_text=False,
            url=iv_link
        )
    )

if __name__ == "__main__":
    html = get_news_list()
    if not html:
        exit()
    noticias = html.find('div', {'class': 'container'})
    for noticia in noticias.findAll('div', {'class': 'col-md-12'})[:5]:
        try:
            link = noticia.find('a')['href']
        except TypeError:
            continue
        if base.check_history(link):
            continue
        title = noticia.find('h3').text
        iv_link = f'https://t.me/iv?url={urllib.parse.quote_plus(link)}&rhash=60af523a41b39d'
        send_message(title, iv_link, link)
        base.bluesky_post('🗞 Agência Brasília', title, link)
        base.add_to_history(link)
