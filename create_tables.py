import sqlite3

# Подключаемся к базе данных
conn = sqlite3.connect('db/school.db')
cursor = conn.cursor()

# Замените 'user_id' на ID текущего пользователя, который зашел в аккаунт
user_id = 2  # Пример ID пользователя
user_role = cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()

if user_role and user_role[0] == 4:
    # Получаем предметы пользователя
    subjects_ids = cursor.execute("SELECT subjects FROM users WHERE id = ?", (user_id,)).fetchone()[0]

    if subjects_ids:
        subject_ids = map(int, subjects_ids.split())

        for subject_id in subject_ids:
            # Получаем название предмета
            subject_info = cursor.execute("SELECT subject_name FROM subject WHERE subject_id = ?",
                                          (subject_id,)).fetchone()
            if subject_info:
                subject_name = subject_info[0]

                # Получаем оценки по предмету
                marks = cursor.execute(
                    "SELECT mark, mark_date FROM marks_all WHERE user_id = ? AND subject_id = ?",
                    (user_id, subject_id)
                ).fetchall()

                # Выводим предмет и оценки
                print(f"Предмет: {subject_name}")
                if marks:
                    for mark in marks:
                        print(f"Оценка: {mark[0]}, Дата: {mark[1]}")
                else:
                    print("Оценок нет.")
                print()  # Пустая строка для разделения предметов
    else:
        print("У пользователя нет предметов.")
else:
    print("У вас нет доступа к дневнику.")

# Закрываем соединение с базой данных
conn.close()
