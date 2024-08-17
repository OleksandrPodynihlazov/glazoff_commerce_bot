import threading
import time

import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import sqlite3


bot = telebot.TeleBot("7336652335:AAFbiaChNn64qJ9g8x5sSPpYlOeZuESPWBs")
channel_name = "@glazoff_tg"
base_url = 'https://glazoff.com/product-category/poslugy-dlya-internet-magazyniv/'
server_url = 'http://127.0.0.1:5000/track/'
total_pages = 3
class User:
    def __init__(self,user_id,first_name,telegram_name):
        self.user_id = user_id
        self.first_name = first_name
        self.telegram_name = telegram_name
#Обробка запуску бота
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    price_button = types.KeyboardButton('Показати ціни')
    markup.add(price_button)

    global new_user
    new_user=User(message.from_user.id,message.from_user.first_name,message.from_user.username)
    bot.send_message(message.chat.id, "Вітаю! Натисніть на кнопку, щоб побачити список цін.", reply_markup=markup)
    log_user()

# Обробка натискання кнопки з меню до переходу на перегляд цін
@bot.message_handler(func=lambda message: message.text == 'Показати ціни')
def show_prices(message):

    markup = types.ReplyKeyboardMarkup(row_width=1)
    button1 = types.KeyboardButton("Сторінка 1")
    button2 = types.KeyboardButton("Сторінка 2")
    button3 = types.KeyboardButton("Сторінка 3")
    markup.add(button1,button2,button3)

    bot.send_message(message.chat.id,'Оберіть сторінку' , reply_markup=markup)
#Добавити кнопку повернутися назад у меню

#Обробка кнопок зі списками послуг
@bot.message_handler(func=lambda message: message.text in ['Сторінка 1','Сторінка 2','Сторінка 3'])
def handle_prices(message):
    chat_id = message.chat.id
    scraped_data = scrape_page(base_url,total_pages,new_user.user_id)
    if message.text == 'Сторінка 1':
        selected_products = scraped_data[:12]
    elif message.text == 'Сторінка 2':
        selected_products = scraped_data[12:24]
    else:
        selected_products = scraped_data[24:36]
    product_messages = "".join(selected_products)
    bot.send_message(chat_id,product_messages,parse_mode="Markdown")

#Завантаження веб сторінки для отримання даних
def get_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text,'html.parser')
    else:
        print(f"Webpage downloading error {url}")
        return None
#Отримання даних з веб сторінки
def scrape_page(base_url,total_pages,user_id):
    results = []

    for page in range(1,total_pages+1):
        url = f'{base_url}/page/{page}'
        soup = get_data(url)

        if soup:
            services = soup.find("ul", class_="products columns-4")
            services = services.find_all("li")
            for service in services:
                service_name_tag = service.find("h2")
                service_name = service_name_tag.text.strip()
                service_price_tag = service.find("span", class_="price")
                service_url_tag = service.find("a")
                service_url = service_url_tag["href"]
                if service_price_tag.find("ins"):
                    service_price_tag = service_price_tag.find("ins")
                    service_price_tag = service_price_tag.find("bdi")
                service_price = service_price_tag.text.strip()
                results.append(f"[{service_name}]({server_url}{service_url.replace('https://','')}?user_id={user_id}): {service_price}\n\n")

    return results

def load_users():
    connection = sqlite3.connect('click.db')
    cursor = connection.cursor()
    cursor.execute('''
    SELECT user_id FROM click
    ''')
    user_id_list = cursor.fetchall()
    user_id_list = [user for user in user_id_list if isinstance(user,(int))]
    connection.commit()
    connection.close()
    return user_id_list
def send_ads(user_id_list):
    for user in user_id_list:
        try:
            bot.send_message(user,"Тут могла бути ваша реклама")
        except Exception as e:
            print(f"Failed to send message to user: {user} :{e}")
        time.sleep(10)
#ініціалізація бази даних
def init_db():
    connection = sqlite3.connect('click.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS click (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            first_name TEXT,
            telegram_name TEXT,
            link_id TEXT
            )
    ''')
    connection.commit()
    connection.close()
#реєстрація користувача в базі даних
def log_user():
    connection = sqlite3.connect('click.db')
    cursor = connection.cursor()
    cursor.execute('''
    INSERT OR IGNORE INTO click (user_id,first_name, telegram_name,link_id)
    VALUES(?, ?, ?, ?)
    ''',(new_user.user_id,new_user.first_name,new_user.telegram_name,''))
    connection.commit()
    connection.close()


init_db()
load_users()
threading.Thread(target=send_ads(load_users())).start()
bot.polling(none_stop=True)
