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
    return render_template('index.html')  # Главная страница


@app.route('/diary')
def diary():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Проверка авторизации пользователя

    user_id = session['user_id']  # Получаем ID пользователя из сессии
    conn = get_db_connection()

    # Получаем список предметов и оценок пользователя
    subjects_grades = conn.execute('''
        SELECT s.subject_name, m.mark
        FROM subject s
        JOIN marks_all m ON s.subject_id = m.subject_id
        WHERE m.user_id = ?
    ''', (user_id,)).fetchall()

    conn.close()

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

    return render_template('diary.html', grades_data=grades_data, average_grades=average_grades)

@app.route('/emotional_tracker')
def emotional_tracker():
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
            return render_template('login.html', error_message=error_message)  # Передаем сообщение об ошибке

    return render_template('login.html')  # Возврат формы входа при GET-запросе


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Удаляем пользователя из сессии
    session.pop('user_fullname', None)  # Также удаляем ФИО
    return redirect(url_for('home'))

# Страница таблицы пользователя
@app.route('/user_table')
def user_table():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Перенаправление на страницу входа, если пользователь не авторизовался

    user_id = session['user_id']
    conn = get_db_connection()
    user = conn.execute('SELECT last_name, first_name, mail FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if user:
        user_fullname = f"{user['last_name']} {user['first_name']}"
        print(user_fullname)
        user_email = user['mail']
        return render_template('user_table.html', user_fullname=user_fullname, user_email=user_email)
    else:
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)


if __name__ == '__main__':
    app.run(debug=True)
