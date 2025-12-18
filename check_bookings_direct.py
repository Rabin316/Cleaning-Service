import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# Check recent bookings
cur.execute('''
    SELECT b.id, s.name, b.user_id, b.status, b.created_at
    FROM cleaning_booking b
    LEFT JOIN cleaning_service s ON b.service_id = s.id
    ORDER BY b.created_at DESC
    LIMIT 10
''')

rows = cur.fetchall()
print("Recent bookings:")
print(f"{'ID':<5} {'Service':<20} {'User ID':<10} {'Status':<15} {'Created'}")
print("-" * 70)

for row in rows:
    booking_id, service_name, user_id, status, created = row
    user_display = str(user_id) if user_id else "None"
    print(f"{booking_id:<5} {service_name:<20} {user_display:<10} {status:<15} {created}")

# Count
cur.execute('SELECT COUNT(*) FROM cleaning_booking WHERE user_id IS NOT NULL')
with_user = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM cleaning_booking WHERE user_id IS NULL')
without_user = cur.fetchone()[0]

print(f"\nTotal bookings: {with_user + without_user}")
print(f"With user_id: {with_user}")
print(f"Without user_id: {without_user}")

conn.close()
