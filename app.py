from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = '143@&Hardhik'  # Replace with a secure key

# Database connection
def get_db_connection():
    conn = sqlite3.connect('lost_and_found.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create tables if they don't exist
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        password TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL
    );
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lost_items (
        lost_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        lost_date TEXT NOT NULL,
        lost_place TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS found_items (
        found_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        found_date TEXT NOT NULL,
        found_place TEXT NOT NULL,
        quiz1_question TEXT NOT NULL,
        quiz1_answer TEXT NOT NULL,
        quiz2_question TEXT NOT NULL,
        quiz2_answer TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO users (name, password, email, phone)
            VALUES (?, ?, ?, ?)
            ''', (name, password, email, phone))
            conn.commit()
            user_id = cursor.lastrowid
            flash(f'Registration successful! Your user ID is: {user_id}', 'success')
        except sqlite3.IntegrityError:
            flash('Email already exists. Please use a different email.', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('index'))
    return render_template('register.html')

# Report a lost item
@app.route('/report_lost', methods=['GET', 'POST'])
def report_lost():
    if request.method == 'POST':
        user_id = request.form['user_id']
        item_name = request.form['item_name']
        lost_date = request.form['lost_date']
        lost_place = request.form['lost_place']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO lost_items (user_id, item_name, lost_date, lost_place)
        VALUES (?, ?, ?, ?)
        ''', (user_id, item_name, lost_date, lost_place))
        conn.commit()
        lost_id = cursor.lastrowid
        conn.close()
        
        flash(f'Lost item reported successfully! Lost ID is: {lost_id}', 'success')
        return redirect(url_for('index'))
    return render_template('report_lost.html')

# Report a found item
@app.route('/report_found', methods=['GET', 'POST'])
def report_found():
    if request.method == 'POST':
        user_id = request.form['user_id']
        item_name = request.form['item_name']
        found_date = request.form['found_date']
        found_place = request.form['found_place']
        quiz1_question = request.form['quiz1_question']
        quiz1_answer = request.form['quiz1_answer']
        quiz2_question = request.form['quiz2_question']
        quiz2_answer = request.form['quiz2_answer']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO found_items (user_id, item_name, found_date, found_place, quiz1_question, quiz1_answer, quiz2_question, quiz2_answer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, item_name, found_date, found_place, quiz1_question, quiz1_answer, quiz2_question, quiz2_answer))
        conn.commit()
        found_id = cursor.lastrowid
        conn.close()
        
        flash(f'Found item reported successfully! Found ID is: {found_id}', 'success')
        return redirect(url_for('index'))
    return render_template('report_found.html')

# Search for lost items
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        item_name = request.form['item_name']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM found_items WHERE item_name LIKE ?
        ''', (f'%{item_name}%',))
        found_items = cursor.fetchall()
        conn.close()
        
        if not found_items:
            flash('No matching found items.', 'error')
            return redirect(url_for('index'))
        
        return render_template('search.html', found_items=found_items)
    return render_template('search.html')

# Verify quiz answers and reveal contact details
@app.route('/verify_quiz/<int:found_id>', methods=['POST'])
def verify_quiz(found_id):
    answer1 = request.form['answer1']
    answer2 = request.form['answer2']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT quiz1_answer, quiz2_answer, user_id FROM found_items WHERE found_id = ?', (found_id,))
    item = cursor.fetchone()
    
    if answer1 == item['quiz1_answer'] and answer2 == item['quiz2_answer']:
        cursor.execute('SELECT email, phone FROM users WHERE id = ?', (item['user_id'],))
        user_details = cursor.fetchone()
        conn.close()
        return f"Contact the founder: Email: {user_details['email']}, Phone: {user_details['phone']}"
    else:
        conn.close()
        return "Incorrect answers. Cannot reveal contact details."

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)