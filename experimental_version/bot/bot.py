from handlers import TelegramBotHandler

if __name__ == "__main__":
    bot_handler = TelegramBotHandler()
    bot_handler.register_handlers()
    bot_handler.run()
