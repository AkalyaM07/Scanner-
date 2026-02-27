# big_vuln_test.py

import os
import pickle
import subprocess
import sqlite3

# Hardcoded secrets
password = "admin123"
api_key = "SECRET_API_KEY_123"
secret_token = "my_super_secret_token"

# Unsafe eval usage
def dangerous_eval(user_input):
    return eval(user_input)

# Unsafe exec usage
def dangerous_exec(code):
    exec(code)

# Unsafe deserialization
def load_data():
    file = open("data.pkl", "rb")
    return pickle.load(file)

# Command injection risk
def run_command(user_input):
    os.system("echo " + user_input)

# Subprocess with shell=True
def run_subprocess(user_input):
    subprocess.call("ls " + user_input, shell=True)

# SQL Injection vulnerability
def unsafe_sql(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchall()

# Weak random token
def generate_token():
    import random
    return str(random.random())

# Insecure file permission
def insecure_file_write():
    with open("private.txt", "w") as f:
        f.write("Sensitive information")

# Hardcoded admin check
def is_admin(user):
    if user == "admin":
        return True
    return False

# Debug information exposure
def debug_mode():
    print("Debug Mode Enabled")
    print("Password:", password)

# Main execution
if __name__ == "__main__":
    user_input = input("Enter something: ")
    dangerous_eval(user_input)