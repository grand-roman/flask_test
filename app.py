from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Файл для хранения пользователей
USERS_FILE = 'users.json'

# Кофейные напитки с ценами в баллах
coffee_drinks = [
    {"id": 1, "name": "Эспрессо", "price": 10, "description": "Классический крепкий кофе"},
    {"id": 2, "name": "Капучино", "price": 15, "description": "Кофе с молочной пенкой"},
    {"id": 3, "name": "Латте", "price": 18, "description": "Кофе с большим количеством молока"},
    {"id": 4, "name": "Американо", "price": 12, "description": "Разбавленный эспрессо"},
    {"id": 5, "name": "Моккачино", "price": 20, "description": "Кофе с шоколадом и молоком"},
    {"id": 6, "name": "Флэт Уайт", "price": 16, "description": "Кофе с тонкой молочной пенкой"},
]

# Инициализация файла пользователей
def init_users_file():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)

# Загрузка пользователей
def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

# Сохранение пользователя
def save_user(username, password):
    users = load_users()
    # Проверяем, существует ли пользователь
    for user in users:
        if user['username'] == username:
            return False
    
    # Добавляем нового пользователя
    users.append({
        'username': username,
        'password': password,
        'points': 100  # Начальные баллы
    })
    
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    return True

# Поиск пользователя
def find_user(username, password):
    users = load_users()
    for user in users:
        if user['username'] == username and user['password'] == password:
            return user
    return None

# Обновление баллов пользователя
def update_user_points(username, points_change):
    users = load_users()
    for user in users:
        if user['username'] == username:
            user['points'] += points_change
            break
    
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

@app.route('/')
def index():
    user_info = None
    if 'username' in session:
        users = load_users()
        for user in users:
            if user['username'] == session['username']:
                user_info = user
                break
    
    return render_template('index.html', 
                         drinks=coffee_drinks, 
                         user=user_info)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if save_user(username, password):
            # Автоматически логиним после регистрации
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('register.html', error="Пользователь уже существует")
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = find_user(username, password)
        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Неверное имя пользователя или пароль")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/buy/<int:drink_id>')
def buy_drink(drink_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Находим напиток
    drink = None
    for d in coffee_drinks:
        if d['id'] == drink_id:
            drink = d
            break
    
    if not drink:
        return redirect(url_for('index'))
    
    # Проверяем баллы пользователя
    users = load_users()
    user = None
    for u in users:
        if u['username'] == session['username']:
            user = u
            break
    
    if user and user['points'] >= drink['price']:
        # Списываем баллы
        update_user_points(session['username'], -drink['price'])
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    init_users_file()
    app.run(debug=True)
