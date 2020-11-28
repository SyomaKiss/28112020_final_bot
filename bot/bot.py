import os
from pathlib import Path

import telebot

from speech_recognizer.spech2text import speech_to_text


bot = telebot.TeleBot("1248456445:AAGYPzs6PDEvcvRjcv_MyHl97inl9BOksw4", parse_mode=None)

CHAT_ID = 375342602
MODEL_PATH = '/home/semyon/projects/hacks/vosk-api/python/example/model_rus_big'


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    print('id: ', message.chat.id)
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(content_types=['voice'])
def process_images(message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = f'{message.chat.id}_voice_{Path(file_info.file_path).name}'
    with open(filename, 'wb') as new_file:
        new_file.write(downloaded_file)
    recognized_text = speech_to_text(filename, MODEL_PATH)
    bot.reply_to(message, recognized_text)
    os.remove(filename)


@bot.message_handler(content_types=['audio'])
def process_images(message):
    file_info = bot.get_file(message.audio.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = f'{message.chat.id}_audio_{Path(file_info.file_path).name}'
    with open(filename, 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.reply_to(message, 'Got AUDIO! transforming')
    recognized_text = speech_to_text(filename, MODEL_PATH)
    bot.reply_to(message, recognized_text)
    os.remove(filename)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


@bot.message_handler(content_types=['document'])
def process_images(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = f'{message.chat.id}_document_{Path(file_info.file_path).name}'
    with open(filename, 'wb') as new_file:
        new_file.write(downloaded_file)


@bot.message_handler(content_types=['photo'])
def process_images(message):
    content_id = bot.get_file(message.photo[-1].file_id)
    with open(str(message.chat.id) + '_content.jpg', 'wb') as f:
        f.write(bot.download_file(content_id.file_path))

bot.polling()

