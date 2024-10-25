import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('db/school.db')
cursor = conn.cursor()

# Создание таблицы grades, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    num INTEGER,
    date TEXT,
    title TEXT
)
''')

# Создание таблицы users, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    role INTEGER,
    last_name TEXT,
    first_name TEXT,
    patronymic TEXT
)
''')


# Функция для добавления оценок
def add_grade(student_id, num, date, title):
    cursor.execute('''
    INSERT INTO grades (student_id, num, date, title)  -- Изменено имя таблицы на grades
    VALUES (?, ?, ?, ?)
    ''', (student_id, num, date, title))
    conn.commit()


# Функция для добавления пользователей
def add_user(role, last_name, first_name, patronymic=None):
    cursor.execute('''
    INSERT INTO users (role, last_name, first_name, patronymic)
    VALUES (?, ?, ?, ?)
    ''', (role, last_name, first_name, patronymic))
    conn.commit()


# Пример добавления пользователя и оценки
# add_user(1, 'Нестеров', 'Павел', 'Николаевич')
# add_user(0, 'Соколова', 'Анастасия', '')
# add_user(0, 'Реутов', 'Максим', '')
# add_user(3, 'Маслеников', 'Игорь', 'Николаевич')
# add_user(3, 'Погребняк', 'Максим', 'Анатольевич')
# add_user(3, 'Костерин', 'Дмитрий', 'Сергеевич')

add_grade(6, 5, '2023-10-01', 'Mathematics test')
add_grade(7, 5, '2023-10-02', 'Mathematics test')
add_grade(7, 5, '2023-10-02', 'Mathematics test')
add_grade(7, 5, '2023-10-03', 'Mathematics test')
add_grade(8, 5, '2023-10-03', 'Mathematics test')
add_grade(8, 5, '2023-10-03', 'Mathematics test')
add_grade(5, 5, '2023-10-01', 'Mathematics test')
add_grade(8, 5, '2023-10-02', 'Mathematics test')
add_grade(10, 5, '2023-10-02', 'Mathematics test')
add_grade(10, 5, '2023-10-03', 'Mathematics test')
add_grade(8, 5, '2023-10-03', 'Mathematics test')
add_grade(8, 5, '2023-10-03', 'Mathematics test')
# Закрытие соединения
conn.close()
