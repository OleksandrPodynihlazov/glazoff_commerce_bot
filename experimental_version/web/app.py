from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = "../business.db"

@app.route("/services",methods=["GET"])
def get_services():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pages")
        rows = cursor.fetchall()

        services=[
            {
                "service_id":row[0],
                "service_url":row[1],
                "service_name":row[2],
                "service_p":row[3],
                "service_price":row[4],
            }
            for row in rows
        ]

        conn.close()


        return jsonify(services)
    except Exception as e:
        return jsonify({"error":str(e)}),500
if __name__ == "__main__":
    app.run(debug=True)