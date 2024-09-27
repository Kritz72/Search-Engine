from flask import Flask, render_template, request, redirect, jsonify, session
from config import Config
import sqlite3
import requests
from datetime import datetime
import os
# Connect to the SQLite database and create tables if they do not exist
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''DROP TABLE IF EXISTS users''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            emailid TEXT NOT NULL,
            password TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    cursor.execute('''DROP TABLE IF EXISTS search_history''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            query TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Create a Flask app instance
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Define a route for the root URL '/'
@app.route('/')
def hello_world():
    username = session.get('username')
    return render_template('Homepage.html', username=username)

# Define a route for '/about'
@app.route('/about')
def about():
    return 'This is a Flask sample application.'

@app.route('/ab', methods=['POST', 'GET'])
def ab():
    if request.method == 'POST':
        username = request.form['Username']
        password = request.form['Password']
        phone = request.form['phone']
        emailId = request.form['Email']
        print(username)
        print(password)
        print(phone)
        print(emailId)

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, emailid, password, phone) VALUES (?, ?, ?, ?)', (username, emailId, password, phone))
        conn.commit()
        cursor.execute('SELECT * FROM users')
        variable = cursor.fetchall()

        # Close the database connection
        conn.close()
        return redirect('/login')
    return render_template('Reg2.html')

# Define a route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Query the users table for the entered username and password
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        print(user)

        # Close the database connection
        conn.close()

        if user:
            session['username'] = username  # Create a session for the logged-in user
            session['user_id'] = user[0]  # Store user ID in session
            return redirect('/')
        else:
            return "Invalid username or password. Please try again."

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the user from the session
    session.pop('user_id', None)  # Remove the user ID from the session
    return redirect('/login')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': app.config['GOOGLE_API_KEY'],
        'cx': app.config['GOOGLE_CSE_ID'],
        'q': query
    }
    response = requests.get(url, params=params)
    print(response.json())
    if response.status_code == 200:
        results = response.json().get('items', [])
    else:
        results = []

    # Log the search query to the database
    if 'user_id' in session:
        user_id = session['user_id']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO search_history (user_id, query) VALUES (?, ?)', (user_id, query))
        conn.commit()
        conn.close()
        username=session['username']
    
    return render_template('search_page.html', results=results, username=username)

@app.route('/search_history')
def search_history():
    if 'user_id' in session:
        user_id = session['user_id']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT query, timestamp FROM search_history WHERE user_id = ? ORDER BY timestamp DESC', (user_id,))
        search_history = cursor.fetchall()
        conn.close()
        username=session['username']
        return render_template('history.html', search_history=search_history,username=username)
    else:
        return redirect('/login')

# Run the Flask app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)