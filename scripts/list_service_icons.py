import sqlite3
import os

DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
if not os.path.exists(DB):
    print('db not found:', DB)
    raise SystemExit(1)

conn = sqlite3.connect(DB)
c = conn.cursor()
try:
    c.execute('select distinct icon from cleaning_service')
    rows = c.fetchall()
    if not rows:
        print('<no icons>')
    else:
        for r in rows:
            print(r[0])
finally:
    conn.close()
