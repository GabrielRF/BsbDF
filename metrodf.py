import base
import os
import requests
import telebot
import urllib
from bs4 import BeautifulSoup

def get_news_list():
    response = requests.get('https://metro.df.gov.br/?cat=38', headers={'User-agent': 'Mozilla/5.1'}, timeout=30, verify=False)
    if response.status_code != 200:
        return False
    return BeautifulSoup(response.content, 'html.parser')

def send_message(title, iv_link, link):
    bot = telebot.TeleBot(os.environ.get(f'BOT_TOKEN'))
    bot.send_message(
        os.environ.get(f'DESTINATION'),
        f'<a href="{iv_link}">󠀠</a><b>{title}</b>\n' 
        f'🚇 <a href="{link}">Metro DF</a>',
        parse_mode='HTML',
        link_preview_options=telebot.types.LinkPreviewOptions(
            prefer_large_media=True,
            show_above_text=False,
            url=iv_link
        )
    )

if __name__ == "__main__":
    html = get_news_list()
    for noticia in html.findAll('article')[:5]:
        link = noticia.findAll('a')
        title = link[1].text
        link = link[1]['href']
        if base.check_history(link):
            continue
        iv_link = f'https://t.me/iv?url={urllib.parse.quote_plus(link)}&rhash=57bff8b1f34ad4' 
        send_message(title, iv_link, link)
        base.add_to_history(link)
