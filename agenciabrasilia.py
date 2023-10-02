import base
import os
import requests
import telebot
import telegraph
from bs4 import BeautifulSoup

def get_news_list():
    try:
        response = requests.get('https://www.agenciabrasilia.df.gov.br/noticias/', timeout=5)
    except requests.exceptions.Timeout:
        return False
    if response.status_code != 200:
        return False
    return BeautifulSoup(response.content, 'html.parser')

def get_news_content(link):
    response = requests.get(link, timeout=5)
    if response.status_code != 200:
        return False
    response = BeautifulSoup(response.content, 'html.parser')
    content = response.find('div', {'id': 'content'})
    author = response.find('p', {'class': 'by'}).text
    text_content = response.findAll('p')
    image = response.find('meta', {'property': 'og:image'})['content']
    subtitle = text_content[1]
    full_text = ''
    text_content.pop(1)
    for p in text_content[2:]:
        full_text = f'{full_text}<br><br>{p.text}'
    return subtitle.text, full_text, image, author

def create_telegraph_post(title, subtitle, full_text, link, image, author):
    telegraph_auth = telegraph.Telegraph(
        access_token=os.environ.get(f'TELEGRAPH_TOKEN')
    )
    response = telegraph_auth.create_page(
        f'{title}',
        html_content=(
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
    html = get_news_list()
    if not html:
        print('Timeout exceeded')
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
