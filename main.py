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

    user_id = session['user_id']
    conn = get_db_connection()
    user = conn.execute('SELECT last_name, first_name, patronymic, mail, role FROM users WHERE id = ?', (user_id,)).fetchone()
    news_list = conn.execute('SELECT * FROM news ORDER BY date DESC').fetchall()
    conn.close()

    if user:
        return render_template('index.html', user=user, news=news_list)
    return redirect(url_for('login'))

@app.route('/diary')
def diary():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    user = conn.execute('SELECT last_name, first_name, patronymic, mail, role, subjects FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if not user:
        return redirect(url_for('login'))

    role = user['role']
    if role == 4:  # Ученик
        return render_student_diary(user_id)

    elif role == 3:  # Учитель
        return render_teacher_diary(user_id)

    return redirect(url_for('home'))

def render_student_diary(user_id):
    conn = get_db_connection()
    subjects_grades = conn.execute('''
        SELECT s.subject_name, m.mark
        FROM subject s
        JOIN marks_all m ON s.subject_id = m.subject_id
        WHERE m.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()

    grades_data = {}
    for row in subjects_grades:
        subject_name = row['subject_name']
        mark = row['mark']
        grades_data.setdefault(subject_name, []).append(mark)

    average_grades = {subject: sum(marks) / len(marks) if marks else 0 for subject, marks in grades_data.items()}
    return render_template('diary.html', grades_data=grades_data, average_grades=average_grades)

def render_teacher_diary(user_id):
    conn = get_db_connection()
    subject_row = conn.execute('SELECT subject_id FROM subject WHERE teacher_id = ?', (user_id,)).fetchone()
    conn.close()

    if subject_row is None:
        return render_template('diaryTeacher.html', student_grades={})

    subject_id = subject_row['subject_id']
    conn = get_db_connection()
    studentsT = conn.execute('''
        SELECT u.id, u.last_name, u.first_name
        FROM users u
        WHERE u.subjects LIKE ?
    ''', (f'%{subject_id}%',)).fetchall()

    student_grades = {}
    for student in studentsT:
        user_id = student['id']
        marks = conn.execute('SELECT mark FROM marks_all WHERE user_id = ? AND subject_id = ?', (user_id, subject_id)).fetchall()
        student_grades[f"{student['last_name']} {student['first_name']}"] = [mark['mark'] for mark in marks]

    conn.close()
    average_grades = {student: sum(marks) / len(marks) if marks else 0 for student, marks in student_grades.items()}
    return render_template('diary.html', grades_data=student_grades, average_grades=average_grades)

@app.route('/emotional_tracker')
def emotional_tracker():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('emotional_tracker.html')

@app.route('/courses')
def courses():
    return render_template('courses.html')

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
        existing_user = conn.execute('SELECT * FROM users WHERE mail = ?', (email,)).fetchone()

        if existing_user:
            conn.close()
            return render_template('register.html', error_message="Пользователь с таким email уже существует.")

        conn.execute('INSERT INTO users (last_name, first_name, patronymic, mail, password, role) VALUES (?, ?, ?, ?, ?, ?)',
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
            return redirect(url_for('home'))

        return render_template('login.html', error_message="Неверный email или пароль")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_fullname', None)
    return redirect(url_for('home'))

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
        return render_template('user_table.html', user_fullname=user_fullname, user_email=user['mail'], icon=user['icon'])

    return redirect(url_for('home'))

@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    user = conn.execute('SELECT role FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if user is None or user['role'] != 0:
        return redirect(url_for('home'))

    if request.method == 'POST':
        date = request.form.get('date')
        content = request.form.get('content')
        image = request.form.get('image')
        name = request.form.get('name')

        conn = get_db_connection()
        conn.execute('INSERT INTO news (date, content, image, name) VALUES (?, ?, ?, ?)', (date, content, image, name))
        conn.commit()
        conn.close()

        return redirect(url_for('home'))

    return render_template('add_news.html')

@app.route('/delete_news/<int:news_id>')
def delete_news(news_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    user = conn.execute('SELECT role FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if user is None or user['role'] != 0:
        return redirect(url_for('home'))

    conn = get_db_connection()
    conn.execute('DELETE FROM news WHERE id = ?', (news_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

@app.route('/edit_news/<int:news_id>', methods=['GET', 'POST'])
def edit_news(news_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    user = conn.execute('SELECT role FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if user is None or user['role'] != 0:
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
