from flask import Flask, render_template_string
import sqlite3
import os

app = Flask(__name__)
DB = 'app.db'

def init_db():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL
            )
        ''')
        conn.execute("INSERT INTO messages (content) VALUES ('Premier message — déployé par Jenkins !')")
        conn.commit()
        conn.close()

@app.route('/')
def home():
    init_db()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT content FROM messages ORDER BY id DESC")
    messages = [row[0] for row in cur.fetchall()]
    conn.close()
    return render_template_string('''
        <html>
        <head><title>Flask + SQLite</title></head>
        <body>
            <h1>✅ Déploiement Jenkins + Docker</h1>
            <ul>
            {% for msg in messages %}
                <li>{{ msg }}</li>
            {% endfor %}
            </ul>
            <p><i>Fichier DB : {{ db_path }}</i></p>
        </body>
        </html>
    ''', messages=messages, db_path=os.path.abspath(DB))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)