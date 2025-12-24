import base
import cloudscraper
import os
import requests
import telebot
import urllib
from bs4 import BeautifulSoup

def get_news_list():
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get("https://www.agenciabrasilia.df.gov.br/noticias/")
    except:
        return False
    if response.status_code != 200:
        return False
    return BeautifulSoup(response.text, 'html.parser')

def send_message(title, iv_link, link):
    bot = telebot.TeleBot(os.environ.get(f'BOT_TOKEN'))
    telebot.util.antiflood(
        bot.send_message,
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
    for noticia in html.findAll('div', {'class': 'content-card-result'})[:5]:
        try:
            link = noticia.find('a')['href']
        except TypeError:
            continue
        if base.check_history(link):
            continue
        base.add_to_history(link)
        title = noticia.find('h3').text
        iv_link = f'https://t.me/iv?url={urllib.parse.quote_plus(link)}&rhash=60af523a41b39d'
        send_message(title, iv_link, link)
        base.bluesky_post('🗞 Agência Brasília', title, link)
