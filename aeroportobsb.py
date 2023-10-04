import base
import io
import os
import requests
import telebot
import telegraph
from bs4 import BeautifulSoup

def get_news_list():
    response = requests.get('https://www.bsb.aero/passageiros/noticias')
    if response.status_code != 200:
        return False
    return BeautifulSoup(response.content, 'html.parser')

def upload_telegraph_image(image, attempt=0):
    print(image)
    telegraph_auth = telegraph.Telegraph(
        access_token=os.environ.get(f'TELEGRAPH_TOKEN')
    )
    file = requests.get(image)
    inmemoryfile = io.BytesIO(file.content)
    path = telegraph_auth.upload_file(inmemoryfile)
    return f'https://telegra.ph{path[0]["src"]}'

def get_news_content(link):
    post = {}
    response = requests.get(f'https://www.bsb.aero{link}')
    if response.status_code != 200:
        return False
    response = BeautifulSoup(response.content, 'html.parser')
    image = response.find('meta', {'property': 'og:image'})['content']
    try:
        post['image'] = upload_telegraph_image(f'https://www.bsb.aero{image}')
    except:
        post['image'] = False
    html = response.find('section')
    post['title'] = html.find('h1').text.strip()
    text = html.findAll('p')
    text.pop(0)
    post['subtitle'] = text[0].text.strip()
    text.pop(0)
    full_text = ''
    for p in text:
        full_text = f'{full_text}<br><br>{p.text.strip()}'
    post['text'] = full_text
    post['link'] = f'https://www.bsb.aero{link}'
    return post

def create_telegraph_post(post):
    telegraph_auth = telegraph.Telegraph(
        access_token=os.environ.get(f'TELEGRAPH_TOKEN')
    )
    response = telegraph_auth.create_page(
        f'{post["title"]}',
        html_content=(
            f'<img src="{post["image"]}">' +
            f'<h4>{post["subtitle"]}</h4><br><br>' +
            f'{post["text"]}<br><br>' +
            f'<a href="{post["link"]}">Leia a matéria original</a>'
        ),
        author_name=f'Aeroporto de Brasília'
    )
    return response["url"]

def send_message(post, iv_link):
    bot = telebot.TeleBot(os.environ.get(f'BOT_TOKEN'))
    bot.send_message(
        os.environ.get(f'DESTINATION'),
        f'<a href="{iv_link}">󠀠</a><b>{post["title"]}</b>\n' + 
        f'✈️ <a href="{post["link"]}">Site Bsb.Aero</a>',
        parse_mode='HTML'
    )

if __name__ == "__main__":
    html = get_news_list()
    for noticia in html.findAll('a'):
        if 'noticia' not in noticia['href']:
            continue
        link = f"{noticia['href']}"
        if base.check_history(link):
            continue
        try:
            post = get_news_content(link)
        except TypeError:
            exit()
        iv_link = create_telegraph_post(post)
        send_message(post, iv_link)
        base.add_to_history(link)
