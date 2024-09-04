import base
import os
import requests
import telebot
import urllib
from bs4 import BeautifulSoup

def get_news_list():
    response = requests.get('https://www.neoenergia.com/web/brasilia/noticias', verify=False)
    if response.status_code != 200:
        return False
    return BeautifulSoup(response.content, 'html.parser')

def send_message(title, iv_link, link):
    bot = telebot.TeleBot(os.environ.get(f'BOT_TOKEN'))
    bot.send_message(
        os.environ.get(f'DESTINATION'),
        f'<b>{title}</b>\n'
        f'⚡️ <a href="{link}">Site Neoenergia</a>',
        parse_mode='HTML',
        link_preview_options=telebot.types.LinkPreviewOptions(
            prefer_large_media=True,
            show_above_text=False,
            url=iv_link
        )
    )

if __name__ == "__main__":
    html = get_news_list()
    noticias = html.find('div', {'class': 'neo-card-noticia__container'})
    for noticia in noticias.findAll('article', {'class': 'neo-card-noticia__card'})[:5]:
        link = f"https://www.neoenergia.com{noticia.find('a')['href']}"
        if base.check_history(link):
            continue
        title = noticia.find('a')['title']
        iv_link = f'https://t.me/iv?url={urllib.parse.quote_plus(link)}&rhash=a42b721099d581'
        send_message(title, iv_link, link)
        base.bluesky_post('⚡️ Neoenergia', title, link)
        base.add_to_history(link)
