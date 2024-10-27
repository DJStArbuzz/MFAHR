import sqlite3
# Подключение к базе данных
conn = sqlite3.connect('db/school.db')
cursor = conn.cursor()
# Создание таблицы grades, если она не существует
cursor.execute('''
CREATE TABLE homework (
    id INTEGER PRIMARY KEY,
    dateBeg TEXT,
        dateFin TEXT,
    teacher_id INTEGER,
    subject_id INTEGER,
    context TEXT
);

''')