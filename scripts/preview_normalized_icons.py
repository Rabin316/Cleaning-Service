import sqlite3, os
DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
conn = sqlite3.connect(DB)
c = conn.cursor()
print('original -> normalized')
for (icon,) in c.execute('select distinct icon from cleaning_service'):
    val = icon or ''
    v = val.strip()
    if not v:
        norm = 'fas fa-broom'
    elif ' ' in v:
        norm = v
    elif v.startswith('fa-'):
        norm = f'fas {v}'
    else:
        norm = f'fas fa-{v}'
    print(f'{val} -> {norm}')
conn.close()
