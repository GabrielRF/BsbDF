import base
import io
import os
import requests
import telebot
import telegraph
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv

def get_news_list():
    try:
        response = requests.get('https://www.agenciabrasilia.df.gov.br/noticias/', timeout=5)
    except requests.exceptions.Timeout:
        return False
    if response.status_code != 200:
        return False
    return BeautifulSoup(response.content, 'html.parser')

def get_news_content(link):
    print(f'Noticia {link}')
    time.sleep(20)
    response = requests.get(link, timeout=30)
    if response.status_code != 200:
        return False
    response = BeautifulSoup(response.content, 'html.parser')
    content = response.find('div', {'id': 'content'})
    author = response.find('p', {'class': 'by'}).text
    text_content = response.findAll('p')
    image = response.find('meta', {'property': 'og:image'})['content']
    image = upload_telegraph_image(image)
    subtitle = text_content[1]
    full_text = ''
    text_content.pop(1)
    for p in text_content[2:]:
        full_text = f'{full_text}<br><br>{p.text}'
    return subtitle.text, full_text, image, author

def upload_telegraph_image(image, attempt=0):
    if attempt == 3:
        return None
    telegraph_auth = telegraph.Telegraph(
        access_token=os.environ.get(f'TELEGRAPH_TOKEN')
    )
    time.sleep(20)
    try:
        file = requests.get(image)
    except:
        upload_telegraph_image(image, attempt=attempt+1)
    inmemoryfile = io.BytesIO(file.content)
    path = telegraph_auth.upload_file(inmemoryfile)
    return f'https://telegra.ph{path[0]["src"]}'

def create_telegraph_post(title, subtitle, full_text, link, image, author):
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
        author_name=f'{author}'
    )
    return response["url"]

def send_message(title, iv_link, link):
    bot = telebot.TeleBot(os.environ.get(f'BOT_TOKEN'))
    bot.send_message(
        os.environ.get(f'DESTINATION'),
        f'<a href="{iv_link}">󠀠</a><b>{title}</b>\n' 
        f'🗞 <a href="{link}">Site Agência Brasília</a>',
        parse_mode='HTML'
    )

if __name__ == "__main__":
    load_dotenv()
    html = get_news_list()
    if not html:
        exit()
    noticias = html.find('section', {'class': 'news'})
    for noticia in noticias.findAll('div', {'class': 'col'})[:5]:
        try:
            link = noticia.find('a')['href']
        except TypeError:
            continue
        if base.check_history(link):
            continue
        title = noticia.find('h2').text
        try:
            subtitle, full_text, image, author = get_news_content(link)
        except:
            continue
        iv_link = create_telegraph_post(title, subtitle, full_text, link, image, author)
        send_message(title, iv_link, link)
        base.add_to_history(link)
