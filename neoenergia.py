import os
import requests
import sqlite3
import telebot
import telegraph
from bs4 import BeautifulSoup

def get_news_list():
    response = requests.get('https://www.neoenergia.com/web/brasilia/noticias')
    if response.status_code != 200:
        return False
    return BeautifulSoup(response.content, 'html.parser')

def get_news_content(link):
    response = requests.get(link)
    if response.status_code != 200:
        return False
    response = BeautifulSoup(response.content, 'html.parser')
    content = response.find('div', {'id': 'main-content'})
    text_content = response.findAll('p')
    image = content.find('div', {'class': 'component-image'})
    image = f"https://www.neoenergia.com/{image.img['src']}"
    subtitle = content.find('h2', {'style': 'margin-bottom: 11px;'})
    full_text = ''
    for p in text_content[0:-3]:
        full_text = f'{full_text}\n{p.text}'
    return subtitle.text, full_text, image

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

def create_telegraph_post(title, subtitle, full_text, link, image):
    telegraph_auth = telegraph.Telegraph(
        access_token=os.environ.get(f'TELEGRAPH_TOKEN')
    )
    response = telegraph_auth.create_page(
        f'{title}',
        html_content=(
            f'<img src="{image}"><br><br>' +
            f'<h4>{subtitle}</h4><br><br>' +
            f'{full_text}<br><br>' +
            f'<a href="{link}">Leia a matéria original</a>'
        ),
        author_name=f'@BsbDF'
    )
    return response["url"]

def send_message(title, iv_link, link):
    bot = telebot.TeleBot(os.environ.get(f'BOT_TOKEN'))
    bot.send_message(
        os.environ.get(f'DESTINATION'),
        f'<a href="{iv_link}">󠀠</a><b>{title}</b>\n' 
        f'⚡️ <a href="{link}">Neoenergia</a>',
        parse_mode='HTML'
    )

if __name__ == "__main__":
    html = get_news_list()
    noticias = html.find('div', {'class': 'neo-card-noticia__container'})
    for noticia in noticias.findAll('article', {'class': 'neo-card-noticia__card'})[:2]:
        link = f"https://www.neoenergia.com{noticia.find('a')['href']}"
        if check_history(link):
            continue
        title = noticia.find('a')['title']
        subtitle, full_text, image = get_news_content(link)
        iv_link = create_telegraph_post(title, subtitle, full_text, link, image)
        send_message(title, iv_link, link)
        add_to_history(link)
