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
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pointsDomo INTEGER DEFAULT 0,
    pointsFuera INTEGER DEFAULT 0          
)       
''')

conn.commit()
conn.close()
