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


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    price_button = types.KeyboardButton('Показати ціни')
    markup.add(price_button)

    bot.send_message(message.chat.id, "Вітаю! Натисніть на кнопку, щоб побачити список цін.", reply_markup=markup)


# Обробка натискання кнопки
@bot.message_handler(func=lambda message: message.text == 'Показати ціни')
def show_prices(message):
    prices_text = ''
    for line in scraped_data:
        caption = f"{line['Name']}  "
        caption += f"\t {line['Price']}\n\n"
        prices_text += caption
    bot.send_message(message.chat.id, f"Ось список цін:\n{prices_text}")


def get_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text,'html.parser')
    else:
        print(f"Webpage downloading error {url}")
        return None
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
                if service_price_tag.find("ins"):
                    service_price_tag = service_price_tag.find("ins")
                    service_price_tag = service_price_tag.find("bdi")
                service_price = service_price_tag.text.strip()
                results.append({
                    "Name": service_name,
                    "Price": service_price
                })
    return results
scraped_data = scrape_page(base_url,total_pages)


# for data in scraped_data:
#     print(data)
bot.polling(none_stop=True)
