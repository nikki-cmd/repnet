from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            phone TEXT,
            telegram TEXT,
            password TEXT
        )
    ''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS clients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT,
                        inn TEXT,
                        company_name TEXT,
                        phone TEXT,
                        product TEXT,
                        quantity INTEGER,
                        total_amount REAL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('main'))
    return redirect(url_for('auth'))

@app.route('/main')
def main():
    if 'username' in session:
        return render_template('main.html')
    return redirect(url_for('auth'))


@app.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html')
    return redirect(url_for('auth'))

@app.route('/registration', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        phone = request.form['phone']
        telegram = request.form['telegram']
        username = request.form['username']
        password = request.form['password']
        

        # Сохраняем данные в базу данных
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, email, phone, telegram, password)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, phone, telegram, password))
        conn.commit()
        conn.close()

        return redirect(url_for('auth'))  # Переходим на страницу авторизации после успешной регистрации

    return render_template('registration.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM users WHERE username = ?
        ''', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and (password == user[5]):  # Проверка пароля
            session['username'] = user[1]  # Сохраняем имя пользователя в сессии
            return redirect(url_for('main'))  # Перенаправляем на главную страницу

        return "Неверный логин или пароль"

    return render_template('auth.html')

@app.route('/clients', methods=['GET'])
def get_clients():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, fio, inn, company_name, phone, product, quantity, total_amount FROM clients')
    clients = cursor.fetchall()
    conn.close()

    return render_template('clients.html', clients=clients)

@app.route('/statistics')
def statistics():
    if 'username' in session:
        return render_template('statistics.html')
    return redirect(url_for('auth'))  # Если нет авторизации, редирект на авторизацию

@app.route('/requests')
def requests():
    if 'username' in session:
        return render_template('requests.html')
    return redirect(url_for('auth'))  # Если нет авторизации, редирект на авторизацию

@app.route('/add_client', methods=['POST'])
def add_client():
    full_name = request.form['fio']
    inn = request.form['inn']
    company_name = request.form['company_name']
    phone = request.form['phone']
    product = request.form['product']
    quantity = request.form['quantity']
    total_amount = request.form['total_amount']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Убираем id из запроса, так как он генерируется автоматически
    cursor.execute('''INSERT INTO clients (fio, inn, company_name, phone, product, quantity, total_amount)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (full_name, inn, company_name, phone, product, quantity, total_amount))

    conn.commit()
    conn.close()

    return redirect(url_for('get_clients'))


@app.route('/edit_client', methods=['POST'])
def edit_client():
    client_id = request.form.get('client_id')
    fio = request.form.get('fio')
    inn = request.form.get('inn')
    company_name = request.form.get('company_name')
    phone = request.form.get('phone')
    product = request.form.get('product')
    quantity = request.form.get('quantity')
    total_amount = request.form.get('total_amount')
    print(client_id, fio)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''UPDATE clients 
                      SET fio=?, inn=?, company_name=?, phone=?, product=?, quantity=?, total_amount=? 
                      WHERE id=?''',
                   (fio, inn, company_name, phone, product, quantity, total_amount, client_id))
    conn.commit()
    conn.close()

    return redirect(url_for('get_clients'))

@app.route('/request')
def show_requests():  # Изменили имя функции
    if 'username' not in session:
        return redirect(url_for('auth'))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, fio, inn, company_name, phone_number, 
               product, quantity, total_price, documents_received 
        FROM clients
    ''')
    all_requests = cursor.fetchall()
    conn.close()
    
    return render_template('request.html', requests=all_requests)



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth'))

if __name__ == '__main__':
    app.run(debug=True)