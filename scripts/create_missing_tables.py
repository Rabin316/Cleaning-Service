import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

tables = {}

tables['cleaning_customerprofile'] = '''
CREATE TABLE cleaning_customerprofile (
    id integer primary key autoincrement,
    phone varchar(20) NOT NULL,
    address text NOT NULL,
    city varchar(100) NOT NULL,
    state varchar(100) NOT NULL,
    zip_code varchar(10) NOT NULL,
    profile_picture varchar(100),
    date_of_birth date,
    preferred_time varchar(20) NOT NULL,
    special_instructions text NOT NULL,
    email_notifications integer NOT NULL DEFAULT 1,
    sms_notifications integer NOT NULL DEFAULT 1,
    total_bookings integer NOT NULL DEFAULT 0,
    total_spent numeric NOT NULL DEFAULT 0,
    created_at datetime,
    updated_at datetime,
    user_id integer NOT NULL UNIQUE,
    FOREIGN KEY(user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);
'''

tables['cleaning_notification'] = '''
CREATE TABLE cleaning_notification (
    id integer primary key autoincrement,
    title varchar(200) NOT NULL,
    message text NOT NULL,
    notification_type varchar(20) NOT NULL,
    is_read integer NOT NULL DEFAULT 0,
    link varchar(255) NOT NULL,
    created_at datetime,
    user_id integer NOT NULL,
    FOREIGN KEY(user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);
'''

tables['cleaning_savedaddress'] = '''
CREATE TABLE cleaning_savedaddress (
    id integer primary key autoincrement,
    label varchar(50) NOT NULL,
    address text NOT NULL,
    city varchar(100) NOT NULL,
    state varchar(100) NOT NULL,
    zip_code varchar(10) NOT NULL,
    is_default integer NOT NULL DEFAULT 0,
    created_at datetime,
    user_id integer NOT NULL,
    FOREIGN KEY(user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);
'''

tables['cleaning_favoriteservice'] = '''
CREATE TABLE cleaning_favoriteservice (
    id integer primary key autoincrement,
    added_at datetime,
    user_id integer NOT NULL,
    service_id integer NOT NULL,
    FOREIGN KEY(user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY(service_id) REFERENCES cleaning_service(id) ON DELETE CASCADE
);
'''

for name, sql in tables.items():
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    exists = cur.fetchone()
    if exists:
        print(f"Table {name} already exists, skipping.")
    else:
        print(f"Creating table {name}...")
        cur.executescript(sql)
        print(f"Created {name}.")

conn.commit()
conn.close()
print('Done')
