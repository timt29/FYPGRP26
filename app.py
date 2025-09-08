from flask import Flask, render_template
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

@app.route("/login")
def login():
    return render_template("login.php")  # This loads your HTML file

@app.route("/register")
def register():
    return render_template("register.php")  # This loads your HTML file

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True)
