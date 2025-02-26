import sqlite3

# Подключаемся к базе данных (или создаем, если её нет)
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Создаем таблицу заявок
cursor.execute('''
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fio TEXT NOT NULL,
        inn TEXT NOT NULL,
        company_name TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        product TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        documents_received BOOLEAN NOT NULL
    )
''')

# Добавляем тестовые данные
sample_data = [
    ("Иванов Иван Иванович", "1234567890", "ООО Ромашка", "+7 900 123 45 67", "Продукт A", 10, 5000, True),
    ("Петров Петр Петрович", "0987654321", "ООО Тюльпан", "+7 901 234 56 78", "Продукт B", 5, 3000, False)
]

cursor.executemany('''
    INSERT INTO applications (fio, inn, company_name, phone_number, product, quantity, total_price, documents_received)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', sample_data)

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()
