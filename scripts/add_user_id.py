import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# Add missing user_id column to cleaning_booking
try:
    cur.execute('''
        ALTER TABLE cleaning_booking
        ADD COLUMN user_id integer REFERENCES auth_user(id) ON DELETE CASCADE
    ''')
    print("Added user_id column to cleaning_booking")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Column user_id already exists")
    else:
        raise

conn.commit()
conn.close()
print('Done')
