from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB = 'app.db'

def init_db():
    conn = sqlite3.connect(DB)
    # Table existante (messages)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
    ''')
    # Nouvelle table : projets avec deadline
    conn.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            deadline TEXT NOT NULL
        )
    ''')
    # Insérer un message initial s'il n'existe pas déjà
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM messages")
    if cur.fetchone()[0] == 0:
        conn.execute("INSERT INTO messages (content) VALUES ('Premier message — déployé par Jenkins !')")
    conn.commit()
    conn.close()

# === Fonctions pour les projets ===
def get_all_projects():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, name, deadline FROM projects ORDER BY deadline")
    projects = cur.fetchall()
    conn.close()
    return projects

def add_project(name, deadline):
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO projects (name, deadline) VALUES (?, ?)", (name, deadline))
    conn.commit()
    conn.close()

def get_project_by_id(project_id):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, name, deadline FROM projects WHERE id = ?", (project_id,))
    project = cur.fetchone()
    conn.close()
    return project

def update_project(project_id, name, deadline):
    conn = sqlite3.connect(DB)
    conn.execute("UPDATE projects SET name = ?, deadline = ? WHERE id = ?", (name, deadline, project_id))
    conn.commit()
    conn.close()

def delete_project(project_id):
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()

# === Routes ===
@app.route('/')
def home():
    init_db()
    # Données de la table messages (ton ancien code)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT content FROM messages ORDER BY id DESC")
    messages = [row[0] for row in cur.fetchall()]
    conn.close()

    # Données des projets (nouveau)
    projects = get_all_projects()

    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Flask + SQLite + CRUD Projets</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 30px; }
                h2 { margin-top: 40px; }
                form { margin: 10px 0 20px; }
                input, button { padding: 6px; margin: 4px; }
                input[type="text"], input[type="date"] { width: 200px; }
                ul { list-style: none; padding: 0; }
                li { background: #f9f9f9; padding: 8px; margin: 4px 0; border-radius: 4px; display: flex; justify-content: space-between; }
                .actions a { margin-left: 8px; text-decoration: none; color: #007bff; }
                .delete { color: #dc3545 !important; }
            </style>
        </head>
        <body>
            <h1>✅ Déploiement Jenkins + Docker</h1>
            <ul>
            {% for msg in messages %}
                <li>{{ msg }}</li>
            {% endfor %}
            </ul>
            <p><i>Fichier DB : {{ db_path }}</i></p>

            <!-- Section CRUD Projets -->
            <h2>📁 Gestion des Projets (CRUD)</h2>
            <form method="POST" action="/projects">
                <input type="text" name="name" placeholder="Nom du projet" required>
                <input type="date" name="deadline" value="{{ '%04d-%02d-%02d'|format(now.year, now.month, now.day) }}" required>
                <button type="submit">Ajouter</button>
            </form>

            <ul>
            {% for p in projects %}
                <li>
                    <strong>{{ p.name }}</strong> — 📅 {{ p.deadline }}
                    <span class="actions">
                        <a href="/projects/{{ p.id }}/edit">Modifier</a>
                        <a href="/projects/{{ p.id }}/delete" class="delete" onclick="return confirm('Supprimer ?')">Supprimer</a>
                    </span>
                </li>
            {% else %}
                <li>Aucun projet.</li>
            {% endfor %}
            </ul>
        </body>
        </html>
    ''', messages=messages, projects=projects, db_path=os.path.abspath(DB), now=datetime.now())

# === CRUD Routes ===
@app.route('/projects', methods=['POST'])
def create_project():
    name = request.form.get('name', '').strip()
    deadline = request.form.get('deadline', '').strip()
    if name and deadline:
        add_project(name, deadline)
    return redirect(url_for('home'))

@app.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    project = get_project_by_id(project_id)
    if not project:
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        deadline = request.form.get('deadline', '').strip()
        if name and deadline:
            update_project(project_id, name, deadline)
        return redirect(url_for('home'))

    return render_template_string('''
        <h2>Modifier le projet</h2>
        <form method="POST">
            <input type="text" name="name" value="{{ project.name }}" required>
            <input type="date" name="deadline" value="{{ project.deadline }}" required>
            <button type="submit">Mettre à jour</button>
            <a href="/">Annuler</a>
        </form>
        <style>body { font-family: Arial; margin: 30px; }</style>
    ''', project=project)

@app.route('/projects/<int:project_id>/delete')
def remove_project(project_id):
    delete_project(project_id)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)