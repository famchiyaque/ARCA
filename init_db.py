# init_db.py
import sqlite3

conn = sqlite3.connect('survey.db')
c = conn.cursor()

c.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
''')

c.execute('''
CREATE TABLE answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    question_number INTEGER,
    answer TEXT,
    resources INTEGER DEFAULT 10,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

conn.commit()
conn.close()
