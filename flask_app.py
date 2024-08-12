from flask import Flask, redirect,request
import sqlite3

app = Flask(__name__)

def init_db():
    connection = sqlite3.connect('click.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS click (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            first_name TEXT,
            telegram_name TEXT,
            link_id TEXT,
            datastamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
    ''')
    connection.commit()
    connection.close()

init_db()

@app.route('/track/<path:link_id>')
def track_link(link_id):
    link_id=link_id.replace('/track/','')
    user_id = request.args.get('user_id')
    if link_id and user_id:
        log_click(user_id,link_id)
        return redirect(f'https://{link_id}')
    else:
        # Return an error message if user_id or link_id is missing
        return "Missing user_id or link_id", 400
def log_click(user_id,link_id):
    connection = sqlite3.connect('click.db')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO click (user_id,link_id)
        VALUES (?, ?)
    ''',(user_id,link_id))
    connection.commit()
    connection.close()
if __name__ == '__main__':
    app.run(port=5000)