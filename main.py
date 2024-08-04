import telebot
import requests
import json
import time
from bs4 import BeautifulSoup


bot_token = telebot.TeleBot("7336652335:AAFbiaChNn64qJ9g8x5sSPpYlOeZuESPWBs")
channel_name = "@glazoff_tg"
page_counter =1
def show_scrapped_data(page_counter):
    page_counter +=1
    glazoff_web_site = "https://glazoff.com/product-category/poslugy-dlya-internet-magazyniv/"+"page/"+str(page_counter)
    return glazoff_web_site

response = requests.get(show_scrapped_data())
html_content = response.content

def scrape_data(html_code):
    soup = BeautifulSoup(html_code, "html.parser")
    services_arr = []
    services = soup.find("ul",class_="products columns-4")
    services = services.find_all("li")
    for service in services:
        service_name_tag = service.find("h2")
        service_name = service_name_tag.text.strip()
        service_price_tag = service.find("span",class_="price")
        if service_price_tag.find("ins"):
            service_price_tag = service_price_tag.find("ins")
            service_price_tag=service_price_tag.find("bdi")
        service_price = service_price_tag.text.strip()
        services_arr.append({
        "Name":service_name,
        "Price":service_price
        })
    return services_arr
show_scrapped_data()
show_scrapped_data()
show_scrapped_data()
bot_token.polling(none_stop=True)
