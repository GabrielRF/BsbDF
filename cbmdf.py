import base
import os
import requests
import telebot
import telegraph
from bs4 import BeautifulSoup

def get_news_list():
    response = requests.get('https://www.cbm.df.gov.br/noticias/')
    if response.status_code != 200:
        return False
    return BeautifulSoup(response.content, 'html.parser')

def get_news_content(link):
    response = requests.get(link)
    if response.status_code != 200:
        return False
    response = BeautifulSoup(response.content, 'html.parser')
    content = response.find('article')
    text_content = content.findAll()
    full_text = ''
    subtitle = text_content[1].text
    for p in text_content[2:]:
        try:
            full_text = f'{full_text}<br><br>{p.text}'
        except:
            continue
    return full_text, subtitle

def create_telegraph_post(title, subtitle, full_text, link, image):
    telegraph_auth = telegraph.Telegraph(
        access_token=os.environ.get(f'TELEGRAPH_TOKEN')
    )
    response = telegraph_auth.create_page(
        f'{title.strip()}',
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
        f'🔥 <a href="{link}">Site CBM DF</a>',
        parse_mode='HTML'
    )

if __name__ == "__main__":
    html = get_news_list()
    for noticia in html.findAll('article')[:5]:
        link = f"{noticia.find('a')['href']}"
        if base.check_history(link):
            continue
        title = noticia.find('h5').text.strip()
        image = noticia.find('div', {'class': 'uagb-post__image'}).a.img['src']
        try:
            full_text, subtitle = get_news_content(link)
        except:
            continue
        iv_link = create_telegraph_post(title, subtitle, full_text, link, image)
        send_message(title, iv_link, link)
        base.add_to_history(link)
