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
    return render_template('diary.html')  # Страница Электронного дневника


@app.route('/emotional_tracker')
def emotional_tracker():
    return render_template('emotional_tracker.html')  # Страница Эмоционального трекера


@app.route('/courses')
def courses():
    return render_template('courses.html')  # Страница Учебных курсов


@app.route('/user_table')
def user_table():
    return render_template('user_table.html')  # Страница Учебных курсов


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


if __name__ == '__main__':
    app.run(debug=True)
