import base
import os
import requests
import telebot
import telegraph
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
    content = div_content.text.strip().replace(title, '').replace('\t', '')
    text = []
    for line in content.split('\n'):
        if len(line) > 2:
            text.append(line)
    subtitle = text[0]
    text.pop(0)
    full_text = ''
    for p in text:
        full_text = f'{full_text}<br><br>{p}'
    return title, subtitle, full_text

def create_telegraph_post(title, subtitle, full_text, link):
    telegraph_auth = telegraph.Telegraph(
        access_token=os.environ.get(f'TELEGRAPH_TOKEN')
    )
    response = telegraph_auth.create_page(
        f'{title}',
        html_content=(
            f'<h4>{subtitle}</h4><br><br>' +
            f'{full_text}<br><br>' +
            f'<a href="https://www.caesb.df.gov.br/{link}">Leia a matéria original</a>'
        ),
        author_name=f'CAESB'
    )
    return response["url"]

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
    title, subtitle, full_text = get_news_content(html)
    f = open('last_caesb.txt', 'w')
    f.write(str(number+1))
    f.close()
    iv_link = create_telegraph_post(title, subtitle, full_text, number)
    send_message(title, iv_link, number)
