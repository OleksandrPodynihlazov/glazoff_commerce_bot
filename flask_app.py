from flask import Flask, redirect,request
import sqlite3

app = Flask(__name__)

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
        SELECT link_id FROM click WHERE user_id=?
    ''',(user_id,))
    current_links = cursor.fetchone()[0]
    updated_links = current_links + '|' + link_id if current_links else link_id
    cursor.execute('''
    UPDATE click SET link_id=? WHERE user_id = ?
    ''',(updated_links,user_id))
    connection.commit()
    connection.close()
if __name__ == '__main__':
    app.run(port=5000)