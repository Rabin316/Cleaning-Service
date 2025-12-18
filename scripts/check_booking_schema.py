import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# Check cleaning_booking structure
cur.execute("PRAGMA table_info(cleaning_booking);")
columns = cur.fetchall()
col_names = {col[1] for col in columns}

print("Current cleaning_booking columns:")
for col in columns:
    print(f"  {col[1]}: {col[2]}")

# Expected columns from migration
expected = {
    'id', 'service_id', 'name', 'email', 'phone', 'address',
    'preferred_date', 'preferred_time', 'frequency', 'special_instructions',
    'status', 'payment_status', 'payment_intent_id', 'amount',
    'customer_rating', 'customer_review', 'created_at', 'updated_at',
    'user_id', 'assigned_to_id'
}

missing = expected - col_names
if missing:
    print(f"\nMissing columns: {missing}")
    
    # Add missing columns
    if 'assigned_to_id' in missing:
        try:
            cur.execute('''
                ALTER TABLE cleaning_booking
                ADD COLUMN assigned_to_id integer REFERENCES cleaning_teammember(id) ON DELETE SET NULL
            ''')
            print("Added assigned_to_id column")
        except sqlite3.OperationalError as e:
            print(f"Error adding assigned_to_id: {e}")
else:
    print("\nAll expected columns present!")

conn.commit()
conn.close()
