import datetime
import time
import os
from dotenv import load_dotenv
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import sqlite3
import re

load_dotenv()

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))
MY_TELEGRAM_ID = os.getenv("MY_TELEGRAM_ID")
SUPPORT_CONTACT = os.getenv("SUPPORT_CONTACT")
base_url = os.getenv("BASE_URL")

conn = sqlite3.connect('business.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS users(
        telegram_id INTEGER PRIMARY KEY,
        first_name TEXT,
        telegram_tag TEXT,
        email TEXT,
        phone_number TEXT)
    '''
)

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders(
    order_id INTEGER PRIMARY KEY AUTOINCREMENT ,
    telegram_id INTEGER,
    service TEXT,
    order_date TIMESTAMP,
    FOREIGN KEY(telegram_id) REFERENCES users(telegram_id)
    )
''')

conn.commit()

client_data = {}


def get_services():
    cursor.execute('''
        SELECT service_id,service_name, service_price, service_url, service_p FROM pages
    ''')
    services = cursor.fetchall()  # Отримання всіх рядків з результату запиту

    services_dict = [
        {"service_id": row[0], "service_name": row[1], "service_price": row[2], "service_url": row[3],
         "service_p": row[4]}
        for row in services
    ]
    return services_dict


services = get_services()


class ClientOrder:
    def __init__(self):
        self.service = None
        self.email = None
        self.phone_number = None
        self.name = None


client_data = {}


# Обробка запуску бота
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    price_button = types.KeyboardButton('Переглянути послуги')
    support_button = types.KeyboardButton('Звернутися до підтримки')
    markup.add(price_button, support_button)

    bot.send_message(message.chat.id,
                     "Привіт! 👋\n"
                     "Ласкаво просимо до нашого Telegram-бота!\n"
                     " Тут ви зможете легко замовити наші послуги з налаштування та наповнення інтернет-магазинів.\n"
                     "📦 Що ми пропонуємо?\n"
                     "Парсинг товарів та контенту\n"
                     "Налаштування інтернет-магазинів\n"
                     "Створення індивідуальних рішень для вашого бізнесу\n"
                     "🌐 Перегляньте весь список послуг .\n"
                     "💬 Якщо у вас є питання, натисніть на кнопку нижче, щоб зв’язатися з нашою підтримкою.\n"
                     "🎯 Готові замовити? Просто оберіть потрібну послугу, і ми все зробимо за вас!\n"
                     "Раді допомогти вашому бізнесу зростати! 🚀", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Звернутися до підтримки')
def support(message):
    bot.send_message(message.chat.id,
                     f"Напишіть, будь ласка, сюди, якщо у вас є якісь питання:https://t.me/AlexGlazoff")


@bot.message_handler(func=lambda message: message.text == 'Переглянути послуги')
def show_prices(message):
    markup = types.InlineKeyboardMarkup()

    # Додаємо 34 кнопки
    for service in services:
        service_id, service_name, service_price, service_url, service_p = service
        button = types.InlineKeyboardButton(f"{service['service_name']}", callback_data=str(service['service_id']))
        markup.add(button)  # Додаємо кожну кнопку в новий рядок (вертикальне розміщення)

    # Надсилаємо повідомлення з клавіатурою
    bot.send_message(message.chat.id, "Ось список усіх наших послуг. Натисніть на будь-яку щоб дізнатися більше:",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def button_handler(call: types.CallbackQuery):
    callback_data = call.data
    user_id = call.from_user.id

    selected_services = None
    for service in services:
        if str(service['service_id']) == callback_data:
            selected_services = service
            break
    if selected_services:
        client_data[user_id] = ClientOrder()
        client_data[user_id].service = selected_services['service_name']
        # Створюємо нову звичайну клавіатуру (ReplyKeyboardMarkup)
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button1 = types.KeyboardButton("Замовити послугу")
        button2 = types.KeyboardButton("Дізнатися більше")
        back_button = types.KeyboardButton("Переглянути послуги")
        support_button = types.KeyboardButton('Звернутися до підтримки')
        markup.add(button1, button2, back_button, support_button)

        # Відправляємо повідомлення з новою клавіатурою
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Ви обрали послугу {selected_services['service_name']}.\n"
                 f"{selected_services['service_p']}\n"
                 f"Ціна цієї послуги: {selected_services['service_price']}\n"
                 f" Оберіть дію:",
            reply_markup=markup
        )


# Обробка звичайних повідомлень, коли користувач натискає кнопки "Замовити послугу" або "Дізнатися більше"
@bot.message_handler(func=lambda message: message.text in "Замовити послугу")
def handle_service_options(message):
    user_id = message.from_user.id
    markup = types.ReplyKeyboardMarkup()
    back_button = types.KeyboardButton("Переглянути послуги")
    support_button = types.KeyboardButton('Звернутися до підтримки')
    markup.add(back_button, support_button)
    if user_id in client_data:
        bot.send_message(message.chat.id, "Будь ласка, введіть ваші данні через кому:\n"
                                          "Як до вас звертатися:\n"
                                          "Номер телефону:\n"
                                          "Електронна адреса:", reply_markup=markup)
        if "Переглянути послуги" in message.text:
            bot.register_next_step_handler(message, show_prices)
        bot.register_next_step_handler(message, order_complete)


def order_complete(message):
    user_id = message.from_user.id
    try:
        if user_id in client_data:
            client_data[user_id].name = message.text.split(",")[0].strip()
            client_data[user_id].phone_number = message.text.split(",")[1].strip()
            client_data[user_id].email = message.text.split(",")[2].strip()
            # Зберігаємо дані в базі даних
            cursor.execute('''
                INSERT OR REPLACE INTO users (telegram_id, first_name, telegram_tag, email, phone_number)
                VALUES(?, ?, ?, ?, ?)
            ''', (
                user_id,
                message.from_user.first_name,
                message.from_user.username,
                client_data[user_id].email,
                client_data[user_id].phone_number
            ))
            conn.commit()
            cursor.execute('''
                INSERT INTO orders (telegram_id,service,order_date)
                VALUES ((SELECT telegram_id FROM users WHERE telegram_id = ?),?,?)
            ''', (
                user_id,
                client_data[user_id].service,
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            conn.commit()
            # Створюємо повідомлення для вас із зібраними даними
            order_details = (f"Нове замовлення! \n"
                             f"звертатися як:{client_data[user_id].name}\n"
                             f"Телеграм нік: {message.from_user.first_name}\n"
                             f"Телеграм тег: {message.from_user.username}\n"
                             f"Послуга: {client_data[user_id].service}\n"
                             f"Email: {client_data[user_id].email}\n"
                             f"Телефон: {client_data[user_id].phone_number}")
            bot.send_message(MY_TELEGRAM_ID, order_details)
            bot.send_message(message.chat.id, "Дякуємо за ваше замовлення! Ми зв'яжемося з вами найближчим часом.")
    except IndexError:
        return 0


@bot.message_handler(func=lambda message: message.text == "Дізнатися більше")
def more_about_service(message):
    user_id = message.from_user.id
    # Знаходимо відповідну послугу для цього користувача
    selected_service = client_data[user_id].service if user_id in client_data else None

    # Шукаємо URL для послуги
    for service in services:
        if service['service_name'] == selected_service:
            service_url = service['service_url']
            break
    else:
        service_url = "URL не знайдено."

    # Відправляємо користувачу посилання на сайт послуги
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Детальніше про послугу: {service_url}"
    )


@bot.message_handler(func=lambda message: message.text == "Переглянути послуги")
def go_back(message):
    # Надсилаємо користувачу список послуг
    markup = types.InlineKeyboardMarkup()

    # Додаємо кнопки для кожної послуги
    for service in services:
        button = types.InlineKeyboardButton(f"{service['service_name']}", callback_data=str(service['service_id']))
        markup.add(button)

    # Надсилаємо повідомлення з клавіатурою
    bot.send_message(message.chat.id, "Ось список усіх наших послуг. Натисніть на будь-яку, щоб дізнатися більше:",
                     reply_markup=markup)


bot.polling(none_stop=True)
