from flask import Flask, render_template, request, redirect, url_for, session
import webbrowser
import threading
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key

# MySQL connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  
        password="password", 
        database="nrs"
    )


@app.route("/")
def home():
    return render_template("index.php")  # This loads your HTML file

@app.route("/article1")
def article1():
    return render_template("article1.html")  # This loads your HTML file

@app.route("/article2")
def article2():
    return render_template("article2.html")  # This loads your HTML file

@app.route("/article3")
def article3():
    return render_template("article3.html")  # This loads your HTML file

@app.route("/article4")
def article4():
    return render_template("article4.html")  # This loads your HTML file

@app.route("/adminHomepage")
def adminHomepage():
    return render_template("adminHomepage.html")  # This loads your HTML file

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and user["password"] == password:
            session["user"] = user["name"]   # store username in session
            return redirect(url_for("home"))
        else:
            return "Invalid email or password!"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match!"

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password),
            )
            conn.commit()
            return redirect(url_for("login"))
        except mysql.connector.IntegrityError:
            return "Email already exists!"
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("users", None)
    return redirect(url_for("home"))

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True)
