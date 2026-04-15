from flask import Flask, request
import sqlite3, os

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    user = request.form['user']
    pwd = request.form['pwd']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # SQL Injection
    query = f"SELECT * FROM users WHERE username='{user}' AND password='{pwd}'"
    cursor.execute(query)

    if cursor.fetchone():
        return "Welcome " + user  # XSS
    else:
        return "Login Failed"

@app.route('/run')
def run():
    cmd = request.args.get('cmd')
    return os.popen(cmd).read()  # Command Injection

app.run(debug=True)