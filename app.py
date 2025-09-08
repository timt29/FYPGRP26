from flask import Flask, render_template, request, redirect, url_for, session
import webbrowser
import threading

app = Flask(__name__)

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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # TODO: Check credentials from DB
        if email == "test@example.com" and password == "1234":
            session["user"] = email
            return redirect(url_for("home"))
        else:
            return "Invalid login!"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # TODO: Add validation + database saving here
        if password != confirm_password:
            return "Passwords do not match!"
        
        # Redirect after success
        return redirect(url_for("login"))

    return render_template("register.html")

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True)
