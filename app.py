from flask import Flask, render_template
import webbrowser
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.php")  # This loads your HTML file

@app.route("/members")
def members():
    return render_template("Members.html")  # This loads your HTML file

@app.route("/ProjectDoc")
def ProjectDoc():
    return render_template("ProjectDoc.html")  # This loads your HTML file



def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True)
