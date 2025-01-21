import telebot
from telebot import types
from config import BOT_TOKEN, MY_TELEGRAM_ID, SUPPORT_CONTACT
from database import DatabaseHandler
import datetime


# class for all bot functions
class TelegramBotHandler:
    def __init__(self):
        self.bot = telebot.TeleBot(BOT_TOKEN)
        # init database handling
        self.db = DatabaseHandler()
        # init object for information about user gathered from telegram message
        self.client_data = {}

    def run(self):
        # Bot await for our actions
        self.bot.polling(none_stop=True, interval=0, timeout=600)

    # handling /start function in bot, register new user in bot and show welcome message
    # Output the buttons keyboard for user interacting
    def start_command(self, message):
        markup = types.ReplyKeyboardMarkup(row_width=1)
        markup.add("Переглянути послуги", "Звернутися до підтримки")
        self.bot.send_message(
            message.chat.id,
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
            "Раді допомогти вашому бізнесу зростати! 🚀",
            reply_markup=markup
        )
        user_id = message.from_user.id
        name = None
        email = None
        phone = None
        self.db.save_user(user_id,name,message.from_user.username,email,phone)
    # list of all services from database
    def show_services(self, message):
        # get list of services from database
        services = self.db.get_services()
        markup = types.InlineKeyboardMarkup()
        # showing each service one-by-one
        for service in services:
            markup.add(types.InlineKeyboardButton(service['service_name'], callback_data=str(service['service_id'])))
        self.bot.send_message(message.chat.id, "Ось список наших послуг. Натисніть, щоб дізнатися більше:",
                              reply_markup=markup)

    # handling chosen service
    def select_service(self, call):
        # Вибір послуги, створення замовлення
        user_id = call.from_user.id
        services = self.db.get_services()
        # return first mathing service id in database
        service = next((s for s in services if str(s['service_id']) == call.data), None)
        if service:
            # save what exactly service been chosen
            self.client_data[user_id] = {'service': service['service_name']}
            # add keyboard and buttons
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            markup.add("Замовити послугу", "Дізнатися більше", "Переглянути послуги", "Звернутися до підтримки")
            # send info message about chosen service
            self.bot.send_message(
                call.message.chat.id,
                f"Ви обрали послугу: {service['service_name']}.\n"
                f"Опис послуги: {service['service_p']}\n"
                f"Ціна: {service['service_price']}\n Оберіть дію:",
                reply_markup=markup
            )

    # return url of chosen service
    def more_about_service(self, message):
        user_id = message.from_user.id
        # looking for chosen service
        selected_service = self.client_data[user_id]['service'] if user_id in self.client_data else None
        # return list of all services
        services = self.db.get_services()  # Отримуємо список послуг
        service_url = "URL не знайдено."
        # looking for service url of our interest
        for service in services:
            if service['service_name'] == selected_service:
                service_url = service['service_url']
                break

        # send message with service url
        self.bot.send_message(
            chat_id=message.chat.id,
            text=f"Детальніше про послугу: {service_url}"
        )

    # asking data from user for completing order
    def request_user_data(self, message):
        user_id = message.from_user.id
        if user_id in self.client_data:
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            markup.add("Переглянути послуги", "Звернутися до підтримки")
            self.bot.send_message(
                message.chat.id,
                "Будь ласка, введіть ваші дані через кому:\n"
                "Ім'я, номер телефону, електронна адреса:",
                reply_markup=markup
            )
            # run another function to check data correct input and sent data to admin
            self.bot.register_next_step_handler(message, self.process_order)

    # check if input from user is correct
    # save new order in database
    # send a message to admin about new order
    def process_order(self, message):
        user_id = message.from_user.id
        try:
            if user_id in self.client_data:
                name, phone, email = [s.strip() for s in message.text.split(",")]
                self.client_data[user_id].update({'name': name, 'phone': phone, 'email': email})
                # save to database
                self.db.save_user(user_id, name, message.from_user.username, email, phone)
                self.db.save_order(user_id, self.client_data[user_id]['service'], datetime.datetime.now())

                # send message about order to admin
                order_details = (
                    f"Нове замовлення!\n"
                    f"Ім'я: {name}\n"
                    f"Телеграм нік: {message.from_user.first_name}\n"
                    f"Телеграм тег: @{message.from_user.username}\n"
                    f"Послуга: {self.client_data[user_id]['service']}\n"
                    f"Email: {email}\n"
                    f"Телефон: {phone}"
                )
                self.bot.send_message(MY_TELEGRAM_ID, order_details)
                self.bot.send_message(message.chat.id, "Дякуємо за замовлення! Ми зв'яжемося з вами.")
        # for data inputted in wrong format
        except ValueError:
            self.bot.send_message(message.chat.id, "Будь ласка, введіть коректні дані у форматі: Ім'я, телефон, email.")
            self.request_user_data(message)  # recall previous function

    def handle_callback(self, call):
        # callback for selected service
        if call.data.isdigit():
            self.select_service(call)

    def support_contact(self, message):
        self.bot.send_message(message.chat.id, f"Підтримка: {SUPPORT_CONTACT}")

    # handler for each command
    def register_handlers(self):
        self.bot.message_handler(commands=["start"])(self.start_command)
        self.bot.message_handler(func=lambda m: m.text == "Переглянути послуги")(self.show_services)
        self.bot.message_handler(func=lambda m: m.text == "Дізнатися більше")(self.more_about_service)
        self.bot.message_handler(func=lambda m: m.text == "Звернутися до підтримки")(self.support_contact)
        self.bot.callback_query_handler(func=lambda call: True)(self.handle_callback)
        self.bot.message_handler(func=lambda m: m.text == "Замовити послугу")(self.request_user_data)
