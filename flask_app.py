from flask import Flask, redirect,request
import sqlite3
import datetime

app = Flask(__name__)

def init_db():
    connection = sqlite3.connect('clicks.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            telegram_name TEXT,
            link_id TEXT,
            datastamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
    ''')
    connection.commit()
    connection.close()

init_db()

@app.route('/track/<link_id>')
def track_link(link_id):
    id = request.args.get('id')


    if link_id == '1':
        return redirect("https://glazoff.com/product/napysannya-tekstiv-na-zamovlennya/")
    elif link_id == '2':
        return  redirect("https://glazoff.com/product/parsyng-ta-zavantazhennya-tovariv-na-sajt/")

def log_click(id,link_id):
    connection = sqlite3.connect('clicks.db')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO clicks (id,link_id)
        VALUES (?, ?)
    ''',(id,link_id))
    connection.commit()
    connection.close()
if __name__ == '__main__':
    app.run(port=5000)