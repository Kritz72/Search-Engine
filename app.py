from flask import Flask, render_template, request, redirect, jsonify
from config import Config
import sqlite3
import requests
# Connect to the SQLite database
conn = sqlite3.connect('database.db')

# Function to create a table in the SQLite database
cursor = conn.cursor()
cursor.execute('''DROP TABLE IF EXISTS users''')
conn.commit()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        emailid TEXT NOT NULL,
        password TEXT NOT NULL,
        phone TEXT NOT NULL
    )
''')
conn.commit()
conn.close()

# Create a Flask app instance
app = Flask(__name__)
app.config.from_object(Config)

# Define a route for the root URL '/'
@app.route('/')
def hello_world():
    return render_template('Homepage.html')

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
            
            return redirect('/')
        else:
            return "Invalid username or password. Please try again."

    return render_template('login.html')

# @app.route('/search', methods=['GET'])
# def search():
#     query = request.args.get('query')
#     if not query:
#         return jsonify({'error': 'No query provided'}), 400

#     url = 'https://www.googleapis.com/customsearch/v1'
#     params = {
#         'key': app.config['GOOGLE_API_KEY'],
#         'cx': app.config['GOOGLE_CSE_ID'],
#         'q': query
#     }
#     response = requests.get(url, params=params)

#     if response.status_code == 200:
#         return jsonify(response.json())
#     else:
#         return jsonify({'error': 'Error fetching results from Google API'}), response.status_code

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

    return render_template('search_page.html', results=results)


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
