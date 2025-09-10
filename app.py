from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
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

def login_required(user_type):
    """
    Decorator to protect routes based on login and user type.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "userID" not in session:
                flash("Please log in first.")
                return redirect(url_for("login"))
            if session.get("usertype") != user_type:
                flash("Access denied.")
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route("/")
def home():
    return render_template("index.html")  # This loads your HTML file

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
@login_required("Admin")
def adminHomepage():
    return render_template("adminHomepage.html")  # This loads your HTML file

@app.route("/modHomepage")
@login_required("Moderator")
def modHomepage():
    return render_template("modHomepage.html")  # This loads your HTML file

@app.route("/subscriberHomepage")
@login_required("Subscriber")
def subscriberHomepage():
    return render_template("subscriberHomepage.html")

@app.route("/subscriberArticle1")
@login_required("Subscriber")
def subscriberArticle1():
    article = {
        "slug": "article1",
        "title": "Circle Line disruption: Service between Marina Bay and Promenade stations has resumed",
        "author": "EchoPress Author",
        "published_at": "1 Sept 2025, 9:10am",
        "updated_at": "1 Sept 2025, 9:30am",
        "image_url": url_for("static", filename="img/SMRT.webp"),
        "paragraphs": [
            ("A train fault on the Circle Line resulted in no train services between Marina Bay and "
             "Promenade for about 35 minutes on Monday (Sept 1) morning. Rail operator SMRT announced "
             "the disruption on social media at 8.41am. It said then that free regular bus services "
             "was available between Marina Bay and Promenade MRT stations. In an update at 9.18am, "
             "SMRT said train services resumed its scheduled operations at about 9.10am. President of "
             "SMRT Trains Lam Sheau Kai said the train fault occurred at about 8.35am, and staff were "
             "immediately deployed to rectify the fault. He said the affected train was moved towards "
             "the overrun tracks to clear the line, and train services are resuming. “We apologise for "
             "the disruption during the morning peak commute and sincerely appreciate your patience and "
             "understanding,” Lam said. Previous disruptions This is the latest incident in a recent "
             "series of train disruptions across Singapore's MRT and LRT networks. Most recently, a "
             "signalling fault on the Downtown Line, which is managed by SBS Transit, delayed train "
             "services between Bukit Panjang and Beauty World MRT stations on Aug 28.")
        ],
    }
    return render_template("subscriberArticle1.html", article=article)


@app.route("/authorHomepage")
@login_required("Author")
def authorHomepage():
    return render_template("authorHomepage.html")

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

        if user:
            # Plain text password (for now, not recommended)
            if password == user["password"]:
                session["userID"] = user["userID"]
                session["usertype"] = user["usertype"]  # store usertype in session
                session["user"] = user["name"]

                # Role-based redirects
                if user["usertype"] == "Admin":
                    return redirect(url_for("adminHomepage"))
                elif user["usertype"] == "Moderator":
                    return redirect(url_for("modHomepage"))
                elif user["usertype"] == "Subscriber":
                    return redirect(url_for("subscriberHomepage"))  # make this route
                elif user["usertype"] == "Author":
                    return redirect(url_for("authorHomepage"))  # make this route
                else:
                    flash("Invalid user type.")
                    return redirect(url_for("login"))
            else:
                flash("Incorrect password.")
        else:
            flash("User not found.")

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
    session.clear()  # removes all session data
    flash("You have been logged out.")
    return redirect(url_for("home"))

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True)
