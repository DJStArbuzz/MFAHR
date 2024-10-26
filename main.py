from flask import Flask, render_template, redirect, url_for, session, request
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Замени на свой секретный ключ

# Функция для получения соединения с базой данных
def get_db_connection():
    conn = sqlite3.connect('db/school.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
@app.route('/index')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Проверка авторизации пользователя

    user_id = session['user_id']  # Получаем ID пользователя из сессии
    conn = get_db_connection()
    user = conn.execute('SELECT last_name, first_name, patronymic, mail, role FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    conn2 = get_db_connection()
    news_list = conn2.execute('SELECT * FROM news ORDER BY date DESC').fetchall()
    conn2.close()
    print(user['role'])
    if user:
        return render_template('index.html', user=user, news=news_list)
    else:
        return redirect(url_for('login'))  # Если пользователь не найден


@app.route('/diary')
def diary():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Проверка авторизации пользователя

    user_id = session['user_id']  # Получаем ID пользователя из сессии

    conn = get_db_connection()
    conn2 = get_db_connection()

    user = conn.execute('SELECT last_name, first_name, patronymic, mail, role, subjects FROM users WHERE id = ?',
                        (user_id,)).fetchone()
    role = user['role']
    conn.close()
    print(role)
    user_subjects = user['subjects']
    print(user_subjects)

    if (role == 4):
        # Получаем список предметов и оценок пользователя
        subjects_grades = conn2.execute('''
                SELECT s.subject_name, m.mark
                FROM subject s
                JOIN marks_all m ON s.subject_id = m.subject_id
                WHERE m.user_id = ?
            ''', (user_id,)).fetchall()

        conn2.close()

        # Обработка данных для передачи в шаблон
        grades_data = {}

        for row in subjects_grades:

            subject_name = row['subject_name']
            mark = row['mark']
            if subject_name not in grades_data:
                grades_data[subject_name] = []
            grades_data[subject_name].append(mark)

        # Подсчет среднего значения для каждого предмета
        average_grades = {subject: sum(marks) / len(marks) if marks else 0 for subject, marks in grades_data.items()}

        return render_template('diary.html', grades_data=grades_data, average_grades=average_grades, role=user['role'])
    elif (role == 3):
        # Получаем список учеников, которые числятся у него на предметах
        student_grades = {}

        # Получаем subject_id
        subject_row = conn2.execute('SELECT subject_id FROM subject WHERE teacher_id = ?', (user_id,)).fetchone()

        if subject_row is None:
            # Если предмет не найден, возвращаем пустой словарь
            return render_template('diaryTeacher.html', student_grades={})

        subject_id = subject_row['subject_id']  # Извлекаем subject_id
        conn3 = get_db_connection()

        # Ищем студентов, у которых в поле subjects есть subject_id
        studentsT = conn3.execute('''
            SELECT u.id, u.last_name, u.first_name
            FROM users u
            WHERE u.subjects LIKE ?
        ''', (f'%{subject_id}%',)).fetchall()

        # Для каждого студента получаем его оценки
        for student in studentsT:
            student_full_name = f"{student['last_name']} {student['first_name']}"
            user_id = student['id']

            # Получаем оценки для данного студента по subject_id
            marks = conn3.execute('''
                SELECT mark FROM marks_all 
                WHERE user_id = ? AND subject_id = ?
            ''', (user_id, subject_id)).fetchall()

            # Сохраняем оценки в словаре
            student_grades[student_full_name] = [mark['mark'] for mark in marks]

        conn2.close()
        conn3.close()
        # Передача данных в шаблон
        average_grades = {subject: sum(marks) / len(marks) if marks else 0 for subject, marks in student_grades.items()}
        return render_template('diary.html', grades_data=student_grades, average_grades=average_grades, role=user['role'])

    # Если роль не равна 3, перенаправляем на главную страницу
    return redirect(url_for('home'))


@app.route('/emotional_tracker')
def emotional_tracker():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Проверка авторизации
    return render_template('emotional_tracker.html')  # Страница Эмоционального трекера

@app.route('/courses')
def courses():
    return render_template('courses.html')  # Страница Учебных курсов

# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        conn = get_db_connection()

        # Проверяем, существует ли уже пользователь с таким email
        existing_user = conn.execute('SELECT * FROM users WHERE mail = ?', (email,)).fetchone()

        if existing_user:
            error_message = "Пользователь с таким email уже существует."
            conn.close()
            return render_template('register.html', error_message=error_message)

        # Вставляем нового пользователя в таблицу
        conn.execute(
            'INSERT INTO users (last_name, first_name, patronymic, mail, password, role) VALUES (?, ?, ?, ?, ?, ?)',
            (last_name, first_name, middle_name, email, password, role))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE mail = ? AND password = ?', (email, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['user_fullname'] = f"{user['last_name']} {user['first_name']}"
            return redirect(url_for('home'))
        else:
            error_message = "Неверный email или пароль"
            return render_template('login.html', error_message=error_message)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Удаляем пользователя из сессии
    session.pop('user_fullname', None)  # Также удаляем ФИО
    return redirect(url_for('home'))

# Страница таблицы пользователя
@app.route('/user_table')
def user_table():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    user = conn.execute('SELECT last_name, first_name, patronymic, mail, icon FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if user:
        user_fullname = f"{user['last_name']} {user['first_name']} {user['patronymic']}"
        user_email = user['mail']
        icon = user['icon']
        return render_template('user_table.html', user_fullname=user_fullname, user_email=user_email, icon=icon)
    else:
        return redirect(url_for('home'))


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    print(session.get('role'))
    user_id = session['user_id']  # Получаем ID пользователя из сессии
    conn = get_db_connection()
    user = conn.execute('SELECT last_name, first_name, patronymic, mail, role FROM users WHERE id = ?',
                        (user_id,)).fetchone()
    conn.close()
    if 'user_id' not in session or user['role'] != 0:
        return redirect(url_for('home'))  # Только для администраторов

    if request.method == 'POST':
        date = request.form.get('date')
        content = request.form.get('content')
        image = request.form.get('image')  # Путь к изображению
        name = request.form.get('name')

        conn = get_db_connection()
        conn.execute('INSERT INTO news (date, content, image, name) VALUES (?, ?, ?, ?)', (date, content, image, name))
        conn.commit()
        conn.close()

        return redirect(url_for('home'))

    return render_template('add_news.html')


@app.route('/delete_news/<int:news_id>')
def delete_news(news_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT role FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if user is None or user['role'] != 0:  # Не администратор
        return redirect(url_for('home'))

    conn = get_db_connection()
    conn.execute('DELETE FROM news WHERE id = ?', (news_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('home'))


@app.route('/edit_news/<int:news_id>', methods=['GET', 'POST'])
def edit_news(news_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT role FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    print(user['role'])
    if user is None or user['role'] != 0:  # Не администратор
        return redirect(url_for('home'))

    conn = get_db_connection()
    if request.method == 'POST':
        date = request.form.get('date')
        content = request.form.get('content')
        image = request.form.get('image')
        name = request.form.get('name')
        conn.execute('UPDATE news SET date = ?, content = ?, image = ?, name = ? WHERE id = ?', (date, content, image, name, news_id))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))

    news_item = conn.execute('SELECT * FROM news WHERE id = ?', (news_id,)).fetchone()
    conn.close()

    return render_template('edit_news.html', news=news_item)


@app.route('/news')
def news():
    conn = get_db_connection()
    news_list = conn.execute('SELECT * FROM news ORDER BY date DESC').fetchall()
    conn.close()
    return render_template('news.html', news=news_list)



if __name__ == '__main__':
    app.run(debug=True)