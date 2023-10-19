import base
import os
import requests
import telebot
import urllib
from bs4 import BeautifulSoup

def get_news_list(number, attempt=0):
    if attempt == 3:
        return False
    response = requests.get(
        f'https://www.caesb.df.gov.br/{number}',
        timeout=10,
            headers={'User-agent': 'Mozilla/5.1'}
        )
    data =  BeautifulSoup(response.content, 'html.parser')
    if 'Erro 404' in str(data):
        data = get_news_list(number+1, attempt=attempt+1)
    return data

def get_news_content(html):
    div_content = html.find('div', {'class': 'item-page'})
    title = div_content.find('h2').text.strip()
    return title

def send_message(title, iv_link, link):
    bot = telebot.TeleBot(os.environ.get(f'BOT_TOKEN'))
    bot.send_message(
        os.environ.get(f'DESTINATION'),
        f'<a href="{iv_link}">󠀠</a><b>{title}</b>\n' 
        f'🚰 <a href="https://www.caesb.df.gov.br/{link}">Site CAESB</a>',
        parse_mode='HTML'
    )

if __name__ == "__main__":
    try:
        f = open('last_caesb.txt', 'r')
        number = int(f.read())
    except FileNotFoundError:
        number = 1815
    html = get_news_list(number)
    if not html:
        exit()
    title = get_news_content(html)
    f = open('last_caesb.txt', 'w')
    f.write(str(number+1))
    f.close()
    link = f'https://www.caesb.df.gov.br/{number}'
    iv_link = f'https://t.me/iv?url={urllib.parse.quote_plus(link)}&rhash=fcdff120dfd9b9'
    send_message(title, iv_link, number)
