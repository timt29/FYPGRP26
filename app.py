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

@app.route("/subscriberArticle2")
def subscriberArticle2():
    if not session.get("user"):
        return redirect(url_for("login"))

    article = {
        "slug": "article2",
        "title": "Woman charged over possessing almost 200 etomidate-laced vapes, buying another 50",
        "author": "EchoPress Author",
        "published_at": "Sep 04, 2025, 05:45 PM",
        "updated_at": "Sep 05, 2025, 12:16 AM",
        "image_url": url_for("static", filename="img/sel-kpod.jpeg"),
        "paragraphs": [
            "SINGAPORE – A woman was charged over possessing 195 etomidate-laced vapes, or Kpods, and buying another 50 such pods on separate occasions in 2024.",
            "On Sept 4, Law Jia Yi, 23, was handed five charges in relation to vapes.",
            "She was also charged over possessing a knife with a 20cm-long blade, a card knife and a screwdriver without lawful purposes in August 2024 at a carpark in Yishun.",
            "For Law’s vape-related charges, she allegedly had 55 Kpods and four vapes in Yishun Avenue 5 on Aug 9, 2024.",
            "That month, she also purportedly bought 50 Kpods in Geylang. It was not stated in court documents where or whom she bought them from.",
            "Separately, Law is accused of possessing 49 vape pods in Yishun, which were later analysed and found to contain etomidate.",
            "Law also allegedly had 98 vape pods and two vapes in Sentosa, in Siloso Road. She is also said to have had 91 Kpods at the same location.",
            "Law’s case has been scheduled for a pre-trial conference on Sept 11.",
            "On Sept 3, a 17-year-old boy was charged with possessing a vape device containing a cannabis-related substance.",
            "In his National Day Rally speech in August, Prime Minister Lawrence Wong said the Government will treat vaping as a drug issue and impose stiffer penalties.",
            "Since Sept 1, first-time etomidate abusers below 18 years old will be fined $500, while adults will be fined $700. This is a $200 increase for each group.",
            "They must also attend mandatory rehabilitation for up to six months.",
            "Sellers of Kpods will face higher penalties under the Misuse of Drugs Act.",
            "Those who import Kpods will face between three and 20 years’ jail, and between five and 15 strokes of the cane.",
            "Those convicted of selling or distributing Kpods will face between two and 10 years’ jail, and receive between two and five strokes of the cane.",
            "The public can report vaping offences to the Tobacco Regulation Branch on 6684-2036 or 6684-2037 from 9am to 9pm daily, or online at go.gov.sg/reportvape",
            "Those using Kpods can seek help through a national programme called QuitVape. More information on vaping can be found at gov.sg/stopvaping, a microsite launched in August to consolidate resources, helplines and reporting avenues.",
            "The authorities have said that those who voluntarily seek support to quit vaping will not face any penalties for doing so."
        ],
    }

    return render_template("subscriberArticle2.html", article=article)

@app.route("/subscriberArticle3")
def subscriberArticle3():
    if not session.get("user"):
        return redirect(url_for("login"))

    article = {
        "slug": "article3",
        "title": "Jail for money mule who was promised $100 a day to withdraw cash for scammers",
        "author": "EchoPress Author",
        "published_at": "Sep 05, 2025, 02:05 PM",
        "updated_at": "Sep 05, 2025, 03:20 PM",
        "image_url": url_for("static", filename="img/scam.jpg"),
        "paragraphs": [
            "SINGAPORE – A financially strapped man withdrew scam proceeds in cash from ATMs to earn $100 a day so that he could buy diapers and milk powder for his newborn child.",
            "Yves Quah Jun Boon, 24, was sentenced to eight months’ jail on Sept 5 after he withdrew more than $150,000 from various ATMs in one day in June 2023.",
            "He pleaded guilty to money laundering and a charge under the Computer Misuse Act.",
            "Deputy Public Prosecutor Tan Jing Min said Quah often confided in his primary school friend, identified in court documents as Wei Jian, about his financial struggles – he needed money to pay for the needs of his newborn child.",
            "In June 2023, Wei Jian told Quah about an opportunity to earn $100 a day by withdrawing cash from ATMs.",
            "That month, Wei Jian and Quah met another man, named Ryan, to collect seven ATM cards registered under three different names, SIM cards and a mobile phone.",
            "Ryan told Quah that it was guaranteed to be a “safe job” and that the personal identification number, or PIN, for all the ATM cards was the same. Despite suspecting that he was asked to withdraw criminal proceeds, Quah went ahead with the job.",
            "On June 25, he withdrew $151,280 from ATMs at Woodlands Civic Centre and Ngee Ann City.",
            "When an ATM card prevented him from withdrawing money, he threw the card away.",
            "DPP Tan said Quah made at least 20 unauthorised withdrawals on that day.",
            "Quah then handed over the cash to a member of a money laundering syndicate, identified in court documents as Siyuan, at the Ngee Ann City carpark.",
            "Siyuan told Quah that $120 was missing and the amount would be deducted from Quah’s salary. This effectively meant that Quah would not be paid for what he did that day.",
            "Soon after this took place, the police arrived at the carpark, acting on a tip-off. Quah, Siyuan and Wei Jian were arrested and the $151,280 in cash was seized.",
            "The prosecutor asked for an eight-month jail term for Quah.",
            "She said: “The accused was not a traditional money mule... but he was part of the ecosystem that launders criminal proceeds, by withdrawing monies that had been deposited into money mules’ bank accounts.”",
            "Those convicted of money laundering can be jailed for up to 10 years, fined up to $500,000, or both."
        ],
    }

    return render_template("subscriberArticle3.html", article=article)

@app.route("/subscriberArticle4")
def subscriberArticle4():
    if not session.get("user"):
        return redirect(url_for("login"))

    article = {
        "slug": "article4",
        "title": "Fire breaks out at Tuas industrial building; no injuries reported",
        "author": "EchoPress Author",
        "published_at": "Sep 06, 2025, 10:25 AM",
        "updated_at": "Sep 06, 2025, 12:00 PM",
        "image_url": url_for("static", filename="img/fire.jpeg"),
        "paragraphs": [
            "SINGAPORE – A fire broke out at an industrial building in Tuas on Saturday morning (Sept 6).",
            "The Singapore Civil Defence Force (SCDF) said it was alerted to the fire at 10.25am.",
            "Thick black smoke could be seen billowing from the building when firefighters arrived at the scene.",
            "SCDF officers deployed six water jets to contain the blaze and prevent it from spreading.",
            "The fire was extinguished within two hours, and damping down operations are ongoing.",
            "There were no reported injuries. Investigations into the cause of the fire are under way."
        ],
    }

    return render_template("subscriberArticle4.html", article=article)


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
