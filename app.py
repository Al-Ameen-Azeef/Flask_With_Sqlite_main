import sqlite3
import random
import smtplib
import time
import os
from email.mime.text import MIMEText

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_key_change_me")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,
    PERMANENT_SESSION_LIFETIME=1800
)

def get_db():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contact (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        message TEXT,
        username TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        is_verified INTEGER DEFAULT 0,
        otp TEXT,
        otp_expiry INTEGER,
        is_admin INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

def send_otp(email, otp):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not sender or not password:
        print("Email credentials not set!")
        return

    msg = MIMEText(f"Your OTP is: {otp}")
    msg['Subject'] = "OTP Verification"
    msg['From'] = sender
    msg['To'] = email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.sendmail(sender, email, msg.as_string())
        server.quit()
        print("OTP sent successfully!")
    except Exception as e:
        print("Email error:", e)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'user' not in session:
            flash("Login required!")
            return redirect('/login')

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO contact (name,email,message,username) VALUES (?,?,?,?)",
            (request.form['name'], request.form['email'], request.form['message'], session['user'])
        )

        conn.commit()
        conn.close()

        flash("Message sent!")
        return redirect('/')

    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        conn = get_db()
        cursor = conn.cursor()

        username = request.form['username']
        email = request.form['email']
        raw_password = request.form['password']

        if len(username) < 3:
            flash("Username too short")
            return redirect('/register')

        if "@" not in email:
            flash("Invalid email")
            return redirect('/register')

        if len(raw_password) < 6:
            flash("Password must be at least 6 characters")
            return redirect('/register')

        password = generate_password_hash(raw_password)

        otp = str(random.randint(100000,999999))
        expiry = int(time.time()) + 300

        try:
            cursor.execute(
                "INSERT INTO users (username,email,password,otp,otp_expiry) VALUES (?,?,?,?,?)",
                (username,email,password,otp,expiry)
            )
            conn.commit()

            send_otp(email, otp)
            session['verify_user'] = username

            return redirect('/verify')

        except:
            flash("User already exists!")
            return redirect('/register')

        finally:
            conn.close()

    return render_template('register.html')

@app.route('/verify', methods=['GET','POST'])
def verify():
    if request.method == 'POST':
        conn = get_db()
        cursor = conn.cursor()

        username = session.get('verify_user')
        if not username:
            flash("Session expired. Register again.")
            return redirect('/register')

        otp = request.form['otp']

        if 'otp_attempts' not in session:
            session['otp_attempts'] = 0

        session['otp_attempts'] += 1

        if session['otp_attempts'] > 5:
            flash("Too many attempts. Try later.")
            return redirect('/login')

        cursor.execute("SELECT otp, otp_expiry FROM users WHERE username=?", (username,))
        data = cursor.fetchone()

        if data and data['otp'] == otp and int(time.time()) < data['otp_expiry']:
            cursor.execute("UPDATE users SET is_verified=1 WHERE username=?", (username,))
            conn.commit()
            session.pop('otp_attempts', None)
            flash("Verified!")
            return redirect('/login')

        flash("Invalid OTP")
        conn.close()

    return render_template('verify.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (request.form['username'],))
        user = cursor.fetchone()

        if user:
            if user['is_verified'] == 0:
                flash("Verify email first!")
                return redirect('/verify')

            if check_password_hash(user['password'], request.form['password']):
                session['user'] = user['username']
                return redirect('/dashboard')

            flash("Wrong password")
        else:
            flash("User not found")

        conn.close()

    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        email = request.form['email']
        cursor.execute(
            "UPDATE users SET email=? WHERE username=?",
            (email, session['user'])
        )
        conn.commit()

    cursor.execute(
        "SELECT username, email FROM users WHERE username=?",
        (session['user'],)
    )
    user = cursor.fetchone()

    conn.close()

    return render_template('profile.html', user=user)

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    cursor = conn.cursor()

    # Check admin
    cursor.execute("SELECT is_admin FROM users WHERE username=?", (session['user'],))
    is_admin = cursor.fetchone()['is_admin']

    if not is_admin:
        flash("Unauthorized access!")
        return redirect('/dashboard')

    # Get all users
    cursor.execute("SELECT id, username, email FROM users")
    users = cursor.fetchall()

    # Get all contacts
    cursor.execute("SELECT * FROM contact")
    contacts = cursor.fetchall()

    conn.close()

    return render_template('admin.html', users=users, contacts=contacts)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html', username=session['user'])

@app.route('/contacts')
def contacts():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    cursor = conn.cursor()

    # Get admin status
    cursor.execute("SELECT is_admin FROM users WHERE username=?", (session['user'],))
    result = cursor.fetchone()

    if not result:
        return redirect('/login')

    is_admin = result['is_admin']

    # 🔥 IMPORTANT LOGIC
    if is_admin == 1:
        cursor.execute("SELECT * FROM contact")
    else:
        cursor.execute("SELECT * FROM contact WHERE username=?", (session['user'],))

    contacts = cursor.fetchall()
    conn.close()

    return render_template('contacts.html', contacts=contacts)

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    cursor = conn.cursor()

    # Check admin
    cursor.execute("SELECT is_admin FROM users WHERE username=?", (session['user'],))
    is_admin = cursor.fetchone()['is_admin']

    if not is_admin:
        flash("Unauthorized!")
        return redirect('/dashboard')

    # Prevent deleting yourself
    cursor.execute("SELECT username FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    if user and user['username'] == session['user']:
        flash("You cannot delete yourself!")
        return redirect('/admin')

    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    flash("User deleted successfully!")
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

