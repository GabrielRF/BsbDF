import base
import os
import requests
import telebot
import urllib
from bs4 import BeautifulSoup

def get_news_list(attempt=0):
    try:
        response = requests.get(
            f'https://www.caesb.df.gov.br/noticias/',
            timeout=10,
                headers={'User-agent': 'Mozilla/5.1'}
            )
    except:
        return False
    return BeautifulSoup(response.content, 'html.parser')

def get_news_content(html):
    div_content = html.find('div', {'class': 'item-page'})
    title = div_content.find('h2').text.strip()
    return title

def send_message(title, iv_link, link):
    bot = telebot.TeleBot(os.environ.get(f'BOT_TOKEN'))
    bot.send_message(
        os.environ.get(f'DESTINATION'),
        f'<b>{title}</b>\n' 
        f'🚰 <a href="{link}">Site CAESB</a>',
        parse_mode='HTML',
        link_preview_options=telebot.types.LinkPreviewOptions(
            prefer_large_media=True,
            show_above_text=False,
            url=iv_link
        )
    )

if __name__ == "__main__":
    html = get_news_list()
    noticias = html.find('div', {'class': 'entries'})
    for noticia in noticias.findAll('article', {'class': 'entry-card'}):
        try:
            link = noticia.find('a')['href']
        except TypeError:
            continue
        if base.check_history(link):
            continue
        title = noticia.find('h2').text
        iv_link = f'https://t.me/iv?url={urllib.parse.quote_plus(link)}&rhash=fcdff120dfd9b9'
        send_message(title, iv_link, link)
        base.bluesky_post('🚰 CAESB', title, link)
        base.add_to_history(link)
