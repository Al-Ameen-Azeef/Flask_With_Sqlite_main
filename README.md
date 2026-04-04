# Flask Contact Management System

A secure Flask-based web application that provides user authentication, email OTP verification, contact form handling, and an admin dashboard.

---

## 🚀 Features

- User Registration & Login
- Email OTP Verification
- Password Reset with OTP
- Contact Form Submission
- Admin Dashboard
- View All Contact Messages
- Delete Users (Admin Only)
- Role-Based Access Control (Admin/User)
- Secure Password Hashing (Werkzeug)
- Session Management & Validation

---

## 🛠 Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** HTML, CSS (Jinja2 Templates)
- **Email Service:** Gmail SMTP

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Al-Ameen-Azeef/Flask_With_Sqlite_main.git
cd Flask_With_Sqlite_main
````

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

```bash
export EMAIL_USER="your_email@gmail.com"
export EMAIL_PASS="your_app_password"
export SECRET_KEY="your_secret_key"
```

### 5. Run the Application

```bash
python app.py
```

---

## 🌐 Access the App

Open your browser and go to:

```
http://127.0.0.1:5000
```

---

## 🔐 Security Features

* Password hashing using Werkzeug
* OTP-based email verification
* OTP expiration & resend protection
* Session validation
* Role-based authorization (Admin/User)

---

## 📂 Project Structure

```
Flask_With_Sqlite_main/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── verify.html
│   ├── dashboard.html
│   ├── admin.html
│   ├── contacts.html
│   ├── profile.html
```

---

## ⚠️ Important Notes

* Do **NOT** upload:

  * `.env` file
  * Database files (`*.db`)
  * Virtual environment (`venv/`)
* Use **Gmail App Password**, not your real password

---

## 📌 Future Improvements

* Password reset UI improvements
* Search & filter functionality
* Pagination for tables
* UI enhancements (Bootstrap / Tailwind)
* Deployment (AWS / Render)

---

## 👨‍💻 Author

**Al-Ameen Azeef**




