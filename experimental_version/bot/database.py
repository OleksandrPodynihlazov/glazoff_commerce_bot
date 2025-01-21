import sqlite3

class DatabaseHandler:
    def __init__(self, db_name="business.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._initialize_tables()

    # init tables for processing new orders and new users
    def _initialize_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users(
                telegram_id INTEGER PRIMARY KEY,
                first_name TEXT,
                telegram_tag TEXT,
                email TEXT,
                phone_number TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders(
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                service TEXT,
                order_date TIMESTAMP,
                FOREIGN KEY(telegram_id) REFERENCES users(telegram_id)
            )
        ''')
        self.conn.commit()

    #save new user to database
    def save_user(self, user_id, first_name, username, email, phone_number):
        self.cursor.execute('''
            INSERT OR REPLACE INTO users (telegram_id, first_name, telegram_tag, email, phone_number)
            VALUES(?, ?, ?, ?, ?)
        ''', (user_id, first_name, username, email, phone_number))
        self.conn.commit()

    #save new order to database
    def save_order(self, user_id, service, order_date):
        self.cursor.execute('''
            INSERT INTO orders (telegram_id, service, order_date)
            VALUES (?, ?, ?)
        ''', (user_id, service, order_date))
        self.conn.commit()

    # return services from db
    def get_services(self):
        self.cursor.execute('SELECT service_id, service_name, service_price, service_url, service_p FROM pages')
        services = self.cursor.fetchall()
        services_dict = [
            {
                'service_id': service[0],
                'service_name': service[1],
                'service_price': service[2],
                'service_url': service[3],
                'service_p': service[4]
            }
            for service in services
        ]
        return services_dict
