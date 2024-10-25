from flask import Flask, render_template, redirect, url_for, session

app = Flask(__name__)  # Исправлено с name на __name__
app.secret_key = 'your_secret_key'  # Замени на свой секретный ключ

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Логика входа (не реализована на этом этапе)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)  # Удаляем пользователя из сессии
    return redirect(url_for('home'))

if __name__ == '__main__':  # Исправлено с name на __name__
    app.run(debug=True)
