import telebot
from telebot import types
import requests
import json
import time
from bs4 import BeautifulSoup


bot = telebot.TeleBot("7336652335:AAFbiaChNn64qJ9g8x5sSPpYlOeZuESPWBs")
channel_name = "@glazoff_tg"
base_url = 'https://glazoff.com/product-category/poslugy-dlya-internet-magazyniv/'
total_pages = 3

#Обробка запуску бота
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    price_button = types.KeyboardButton('Показати ціни')
    markup.add(price_button)

    bot.send_message(message.chat.id, "Вітаю! Натисніть на кнопку, щоб побачити список цін.", reply_markup=markup)
#Додати ініціалізацію користувача до бази даних

# Обробка натискання кнопки з меню до переходу на перегляд цін
@bot.message_handler(func=lambda message: message.text == 'Показати ціни')
def show_prices(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    button1 = types.KeyboardButton("Сторінка 1")
    button2 = types.KeyboardButton("Сторінка 2")
    button3 = types.KeyboardButton("Сторінка 3")
    markup.add(button1,button2,button3)

    bot.send_message(message.chat.id,  reply_markup=markup)
#Добавити кнопку повернутися назад у меню

#Обробка кнопок зі списками послуг
@bot.message_handler(func=lambda message: message.text in ['Сторінка 1','Сторінка 2','Сторінка 3'])
def handle_prices(message):
    chat_id = message.chat.id

    if message.text == 'Сторінка 1':
        selected_products = scraped_data[:12]
    elif message.text == 'Сторінка 2':
        selected_products = scraped_data[12:24]
    else:
        selected_products = scraped_data[24:]
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
def scrape_page(base_url,total_pages):
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
                results.append(f"[{service_name}]({service_url}): {service_price}\n\n")

    return results
scraped_data = scrape_page(base_url,total_pages)


for data in scraped_data:
    print(data)
bot.polling(none_stop=True)
