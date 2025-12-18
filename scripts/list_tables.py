import sqlite3
conn = sqlite3.connect('db.sqlite3')
rows = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")]
print('\n'.join(rows))
conn.close()
