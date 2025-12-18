import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# Add missing columns to cleaning_booking
missing_cols = {
    'payment_status': "varchar(20) NOT NULL DEFAULT 'pending'",
    'payment_intent_id': 'varchar(255)',
    'amount': 'decimal(10, 2)',
    'customer_rating': 'integer',
    'customer_review': 'TEXT',
}

for col_name, col_def in missing_cols.items():
    try:
        cur.execute(f'ALTER TABLE cleaning_booking ADD COLUMN {col_name} {col_def}')
        print(f"Added {col_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(f"Column {col_name} already exists")
        else:
            print(f"Error adding {col_name}: {e}")

conn.commit()
conn.close()
print('Done')
