import base
import datetime
import feedparser
import requests
import os
import telebot
import xmltodict
from telebot import types

def get_alerts():
    feed = feedparser.parse('https://apiprevmet3.inmet.gov.br/avisos/rss')
    for item in feed['items']:
        alert = {}
        if 'Distrito Federal' not in str(item['description']):
            continue
        alert['title'] = item['title']
        response = requests.get(item['link'])
        data = xmltodict.parse(response.content)
        creation = data['alert']['info']['onset']
        creation = datetime.datetime.strptime(creation, '%Y-%m-%dT%H:%M:%S%z')
        alert['creation'] = datetime.datetime.strftime(creation, '%d/%m/%Y %H:%M')
        expires = data['alert']['info']['expires']
        expires = datetime.datetime.strptime(expires, '%Y-%m-%dT%H:%M:%S%z')
        alert['expires'] = datetime.datetime.strftime(expires, '%d/%m/%Y %H:%M')
        alert['description'] = data['alert']['info']['description']
        alert['instructions'] = data['alert']['info']['instruction']
        alert['event'] = data['alert']['info']['event'] 
        alert['link'] = data['alert']['info']['web']
        if creation.date() == datetime.datetime.today().date():
            return alert
        return False

def create_message(alert):
    message = (
        f'🌤 <b>INMET Alerta</b>\n\n'
        f'❗️ <code>{alert["event"].title()}</code>\n' +
        f'Início: {alert["creation"]}\n' +
        f'Fim: {alert["expires"]}\n\n' +
        f'⚠️ <i>{alert["description"]}</i>\n\n' +
        f'ℹ️ {alert["instructions"]}'
    )
    return message

def create_bluesky_message(alert):
    message = (
        f'❗️ {alert["event"].title()}\n' +
        f'Início: {alert["creation"]}\n' +
        f'Fim: {alert["expires"]}\n' +
        f'⚠️ {alert["description"]}'
    )
    return message

def send_message(message, alert):
    bot = telebot.TeleBot(os.environ.get(f'BOT_TOKEN'))
    btn_link = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(f'🌤 Ver Alerta', url=alert['link'])
    btn_link.row(btn)
    msg = bot.send_message(
        os.environ.get(f'DESTINATION'),
        message,
        reply_markup=btn_link,
        parse_mode='HTML'
    )
    bot.pin_chat_message(
        os.environ.get(f'DESTINATION'),
        msg.id,
        disable_notification=True
    )
    bot.delete_message(
        os.environ.get(f'DESTINATION'),
        msg.id+1
    )

if __name__ == "__main__":
    alert = get_alerts()
    if alert:
        if base.check_history(alert['link']):
            exit()
        send_message(create_message(alert), alert)
        base.bluesky_post('🌤 INMET Alerta', create_bluesky_message(alert), alert['link'])
        base.add_to_history(alert['link'])
