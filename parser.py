import sqlite3
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

BASE_URL = 'https://glazoff.com/top-poslug-z-najvyshhym-rejtyngom/'
TOTAL_PAGES = 3
conn = sqlite3.connect('business.db', check_same_thread=False)
cursor = conn.cursor()

firefox_options = Options()
firefox_options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"


# Ініціалізація браузера (в даному випадку Chrome)
service = Service("C:/SeleniumBasic/geckodriver.exe", port=8000)  # Вкажіть шлях до geckodriver
driver = webdriver.Firefox(service=service, options=firefox_options)
cursor.execute('''
CREATE TABLE IF NOT EXISTS pages(
    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_url TEXT UNIQUE,
    service_name TEXT,
    service_price TEXT,
    service_p TEXT
)
''')


def get_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Webpage downloading error {url}")
        return None


# Отримання даних з веб сторінки
def scrape_page(BASE_URL, TOTAL_PAGES):
    for page in range(1, TOTAL_PAGES + 1):
        url = f'{BASE_URL}/page/{page}'
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


                # Перевірка наявності зниженої ціни
                if service_price_tag.find("ins"):
                    service_price_tag = service_price_tag.find("ins").find("bdi")
                service_price = service_price_tag.text.strip()

                # Перевірка, чи існує послуга з таким URL
                cursor.execute('''
                    SELECT service_id FROM pages WHERE service_url = ?
                ''', (service_url,))
                result = cursor.fetchone()
                service_p = scrape_service_page(service_url)
                if result:
                    # Оновлюємо запис, якщо послуга вже є
                    cursor.execute('''
                        UPDATE pages SET service_price = ? WHERE service_url = ?
                    ''', (service_price, service_url))
                else:
                    # Вставляємо новий запис, якщо послуги ще немає
                    cursor.execute('''
                        INSERT INTO pages (service_url, service_name, service_price, service_p)
                        VALUES(?, ?, ?,?)
                    ''', (service_url, service_name, service_price,service_p))
                print(service_p)
                conn.commit()



def scrape_service_page(service_url):
    soup = get_data(service_url)
    first_paragraph = None
    if soup:
        div = soup.find("div", class_="woocommerce-product-details__short-description")
        if not div:
            first_paragraph = scrape_service_page_dynamic(service_url)
            if first_paragraph is None:
                # Якщо і це повертає None, парсимо з div з id "tab-description"
                first_paragraph = scrape_tab_description(service_url)
        if div:
            service_p = div.find("p")
            first_paragraph = service_p.text.strip()
    else:
        print("Не вдалось знайти абзац на сторінці")
    return first_paragraph

def scrape_tab_description(service_url):
    soup = get_data(service_url)
    if soup:
        # Пошук div з ID "tab-description"
        tab_description_div = soup.find("div", id="tab-description")
        paragraph = tab_description_div.find("p")
        if paragraph:
            # Повертаємо текст вмісту
            return paragraph.text.strip()
        else:
            print("Не вдалось знайти div з ID 'tab-description'")
            return None
    else:
        print("Не вдалось завантажити сторінку для отримання tab-description")
        return None
def scrape_service_page_dynamic(service_url):
    driver.get(service_url)

    try:
        # Очікуємо, поки випадаюче меню та текст завантажаться
        wait = WebDriverWait(driver, 20)
        dropdown = wait.until(EC.presence_of_all_elements_located((By.ID, 'paket')))
        try:
            dropdown = wait.until(EC.element_to_be_clickable((By.ID, 'paket')))
        except Exception as e:
            print(f"Помилка при знаходженні елемента: {e}")
        # Вибір потрібної опції з випадаючого меню
        select = Select(dropdown)

        # Вибираємо опцію "Преміум"
        select.select_by_visible_text("Базовий")

        # Очікування появи динамічного тексту
        dynamic_text = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".woocommerce-variation")))

        # Отримання тексту
        return dynamic_text.text.strip()


    except Exception as e:

        # Перевірка, чи є аргументи у виключення

        if e.args and not e.args[0].startswith("Не вдалось отримати текст"):

            print(f"Помилка при парсингу сторінки: {e}")

        else:
            print("")


# Запуск парсингу
scrape_page(BASE_URL, TOTAL_PAGES)
driver.quit()