from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask import jsonify
import uuid
from functools import wraps
import webbrowser
import threading
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key

# ---------- DB ----------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="nrs"
    )

# ---------- Auth wrapper ----------
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

# ---------- Public pages ----------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/article1")
def article1():
    return render_template("article1.html")

@app.route("/article2")
def article2():
    return render_template("article2.html")

@app.route("/article3")
def article3():
    return render_template("article3.html")

@app.route("/article4")
def article4():
    return render_template("article4.html")

# ---------- Role homepages ----------
@app.route("/adminHomepage")
@login_required("Admin")
def adminHomepage():
    return render_template("adminHomepage.html")

@app.route("/modHomepage")
@login_required("Moderator")
def modHomepage():
    return render_template("modHomepage.html")

@app.route("/subscriberHomepage")
@login_required("Subscriber")
def subscriberHomepage():
    # fetch warnings for this subscriber
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT message, created_at FROM warnings WHERE userID = %s", (session["userID"],))
    warnings = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("subscriberHomepage.html", warnings=warnings)

# ---------- Subscriber article pages (with pin support) ----------
@app.route("/subscriberArticle1")
def subscriberArticle1():
    if not session.get("user"):
        return redirect(url_for("login"))

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
    pinned = set(session.get("pinned_articles", []))
    return render_template("subscriberArticle1.html", article=article, is_pinned=(article["slug"] in pinned))

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
    pinned = set(session.get("pinned_articles", []))
    return render_template("subscriberArticle2.html", article=article, is_pinned=(article["slug"] in pinned))

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
    pinned = set(session.get("pinned_articles", []))
    return render_template("subscriberArticle3.html", article=article, is_pinned=(article["slug"] in pinned))

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
    pinned = set(session.get("pinned_articles", []))
    return render_template("subscriberArticle4.html", article=article, is_pinned=(article["slug"] in pinned))

# ---------- Create article (draft / publish flashes) ----------
@app.route("/article-editor", methods=["GET", "POST"])
def create_edit_delete_article():
    if not session.get("user"):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": False, "message": "Please log in first.",
                            "redirect": url_for("login")}), 401
        return redirect(url_for("login"))

    # GET = open editor (create mode) or edit mode via ?edit=<id>
    if request.method == "GET":
        edit_id = (request.args.get("edit") or "").strip()
        article = _store_find(edit_id) if edit_id else None  # uses helpers from earlier
        return render_template("subscriberCreateArticle.html", article=article)

    # POST = AJAX save/publish from editor
    is_ajax  = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    action   = (request.form.get("action") or "").strip()     # 'draft' | 'publish'
    edit_id  = (request.form.get("id") or "").strip()
    title    = (request.form.get("title") or "").strip()
    category = (request.form.get("category") or "").strip()
    content  = (request.form.get("content") or "").strip()
    image    = request.files.get("image")
    image_name = image.filename if image else ""

    if action not in ("draft", "publish") or not title or not category or not content:
        msg = "Please complete the form."
        return (jsonify({"ok": False, "message": msg}), 400) if is_ajax else redirect(url_for("create_edit_delete_article"))

    status   = "draft" if action == "draft" else "published"
    articles = _store_get_all()  # helpers from earlier message

    if edit_id:
        target = _store_find(edit_id)
        if not target:
            msg = "Article not found."
            return (jsonify({"ok": False, "message": msg}), 404) if is_ajax else redirect(url_for("my_articles"))
        target.update({
            "title": title, "category": category, "content": content,
            "image_name": image_name or target.get("image_name", ""), "status": status
        })
        msg = "✅ Your edits have been saved as a draft." if status == "draft" else "🚀 Your edits have been published!"
    else:
        import uuid
        new_id = uuid.uuid4().hex[:12]
        articles.append({
            "id": new_id, "title": title, "category": category, "content": content,
            "image_name": image_name, "status": status
        })
        msg = "✅ Your story has been saved as a draft." if status == "draft" else "🚀 Your story has been uploaded successfully!"

    session.modified = True
    if is_ajax:
        return jsonify({"ok": True, "message": msg, "redirect": url_for("subscriberHomepage")})
    flash(msg, "success")
    return redirect(url_for("subscriberHomepage"))

# ---------- Pin API ----------
@app.route("/pin-article", methods=["POST"])
def pin_article():
    if not session.get("user"):
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    slug = data.get("slug")
    if not slug:
        return jsonify({"ok": False, "error": "missing slug"}), 400

    pinned = session.get("pinned_articles", [])
    if not isinstance(pinned, list):
        pinned = list(pinned)

    if slug in pinned:
        pinned.remove(slug)
        changed_to = "unpin"
    else:
        pinned.append(slug)
        changed_to = "pin"

    session["pinned_articles"] = pinned
    return jsonify({"ok": True, "state": changed_to})

# --- HELPERS ------------------------------------------------------
def _store_get_all():
    """Return the list that keeps the subscriber's articles in session."""
    if "my_articles" not in session:
        session["my_articles"] = []  # each item: {id,title,category,content,image_name,status}
    return session["my_articles"]

def _store_find(aid):
    for a in _store_get_all():
        if a["id"] == aid:
            return a
    return None

# --- MY ARTICLES LIST ---------------------------------------------
@app.route("/my-articles")
def my_articles():
    if not session.get("user"):
        return redirect(url_for("login"))
    articles = _store_get_all()
    return render_template("subscriberMyArticles.html", articles=articles)

# --- CREATE / EDIT (same page) -----------------------------------
@app.route("/create-article", methods=["GET", "POST"])
def create_article():
    # must be logged in
    if not session.get("user"):
        # If the request was made via fetch (AJAX), return JSON; otherwise redirect to login
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": False, "message": "Please log in first.", "redirect": url_for("login")}), 401
        return redirect(url_for("login"))

    if request.method == "GET":
        # render the page (create mode)
        return render_template("subscriberCreateArticle.html", article=None)

    # POST (AJAX from the page’s JS)
    action   = (request.form.get("action") or "").strip()   # "draft" or "publish"
    title    = (request.form.get("title") or "").strip()
    category = (request.form.get("category") or "").strip()
    content  = (request.form.get("content") or "").strip()
    image    = request.files.get("image")

    # (optional) Do any temp saving you like here; we’ll just simulate success
    if action == "draft":
        msg = "✅ Your story has been saved as a draft."
    elif action == "publish":
        msg = "🚀 Your story has been uploaded successfully!"
    else:
        return jsonify({"ok": False, "message": "⚠️ Something went wrong. Please try again."}), 400

    # Tell the client to go back to the subscriber home when done showing the confirmation
    return jsonify({"ok": True, "message": msg, "redirect": url_for("subscriberHomepage")})

# --- EDIT SHORTCUT ------------------------------------------------
@app.route("/edit-article/<aid>")
def edit_article(aid):
    if not session.get("user"):
        return redirect(url_for("login"))
    article = _store_find(aid)
    if not article:
        flash("Article not found.", "error")
        return redirect(url_for("my_articles"))
    # reuse the same template with 'article' filled
    return render_template("subscriberCreateArticle.html", article=article)

# --- DELETE -------------------------------------------------------
@app.route("/delete-article/<aid>", methods=["POST"])
def delete_article(aid):
    if not session.get("user"):
        return jsonify({"ok": False, "message": "Unauthorized"}), 401
    articles = _store_get_all()
    keep = [a for a in articles if a["id"] != aid]
    session["my_articles"] = keep
    session.modified = True
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"ok": True, "message": "🗑️ Article deleted.", "redirect": url_for("my_articles")})
    flash("Article deleted.", "success")
    return redirect(url_for("my_articles"))

def _all_builtin_articles():
    # Reuse the same content you already have in subscriberArticle1..4
    return [
        {
            "slug": "article1",
            "title": "Circle Line disruption: Service between Marina Bay and Promenade stations has resumed",
            "image_name": None,  # if you store uploads later
            "image_url": url_for("static", filename="img/SMRT.webp"),
            "category": "Trending",
            "content": ("A train fault on the Circle Line resulted in no train services between Marina Bay and "
                        "Promenade for about 35 minutes on Monday (Sept 1) morning. Rail operator SMRT announced "
                        "the disruption on social media at 8.41am. ..."),
        },
        {
            "slug": "article2",
            "title": "Woman charged over possessing almost 200 etomidate-laced vapes, buying another 50",
            "image_name": None,
            "image_url": url_for("static", filename="img/sel-kpod.jpeg"),
            "category": "Crime",
            "content": ("SINGAPORE – A woman was charged over possessing 195 etomidate-laced vapes, or Kpods, "
                        "and buying another 50 such pods on separate occasions in 2024. ..."),
        },
        {
            "slug": "article3",
            "title": "Jail for money mule who was promised $100 a day to withdraw cash for scammers",
            "image_name": None,
            "image_url": url_for("static", filename="img/scam.jpg"),
            "category": "Crime",
            "content": ("SINGAPORE – A financially strapped man withdrew scam proceeds in cash from ATMs "
                        "to earn $100 a day so that he could buy diapers and milk powder for his newborn child. ..."),
        },
        {
            "slug": "article4",
            "title": "Fire breaks out at Tuas industrial building; no injuries reported",
            "image_name": None,
            "image_url": url_for("static", filename="img/fire.jpeg"),
            "category": "Local",
            "content": ("SINGAPORE – A fire broke out at an industrial building in Tuas on Saturday morning "
                        "(Sept 6). The Singapore Civil Defence Force (SCDF) said it was alerted at 10.25am. ..."),
        },
    ]


# ---------- Bookmarks page ----------
@app.route("/bookmarks")
def bookmarks():
    if not session.get("user"):
        return redirect(url_for("login"))

    pinned = set(session.get("pinned_articles", []))
    all_articles = _all_builtin_articles()

    # filter by pinned
    articles = [a for a in all_articles if a["slug"] in pinned]

    # optional sorting by ?sort=recent|title|category
    sort = request.args.get("sort", "").lower()
    if sort == "title":
        articles.sort(key=lambda x: x["title"].lower())
    elif sort == "category":
        articles.sort(key=lambda x: x.get("category", "").lower())
    # "recent" not meaningful for built-ins; keep as-is or add timestamps later

    return render_template("subscriberBookmarks.html", articles=articles)


# ---------- Author homepage ----------
@app.route("/authorHomepage")
@login_required("Author")
def authorHomepage():
    return render_template("authorHomepage.html")

# ---------- Auth ----------
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
            # NOTE: plaintext password check (not recommended for production)
            if password == user["password"]:
                # Block suspended BEFORE setting session
                if user["usertype"].lower() == "suspended":
                    flash("Your account has been suspended. Please contact support.")
                    return redirect(url_for("login"))

                # Set session
                session["userID"] = user["userID"]
                session["usertype"] = user["usertype"]
                session["user"] = user["name"]

                # Role redirects
                if user["usertype"] == "Admin":
                    return redirect(url_for("adminHomepage"))
                elif user["usertype"] == "Moderator":
                    return redirect(url_for("modHomepage"))
                elif user["usertype"] == "Subscriber":
                    return redirect(url_for("subscriberHomepage"))
                elif user["usertype"] == "Author":
                    return redirect(url_for("authorHomepage"))
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

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password, usertype) VALUES (%s, %s, %s, %s)",
                (name, email, password, "Subscriber")
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
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("home"))

# ---------- Moderator: manage users ----------
@app.route("/manageUsers")
def manage_users():
    if "userID" not in session or session.get("usertype") != "Moderator":
        flash("Access denied.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT userID, name, email, usertype
        FROM users
        WHERE usertype IN ('Subscriber', 'Author', 'Suspended')
    """)
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("manageUsers.html", users=users)

@app.route("/warnUser", methods=["POST"])
def warn_user():
    if "userID" not in session or session.get("usertype") != "Moderator":
        flash("Access denied.")
        return redirect(url_for("login"))

    warned_user_id = request.form.get("userID")

    conn = get_db_connection()
    cursor = conn.cursor()

    warning_message = "You have received a warning from the moderator."
    cursor.execute(
        "INSERT INTO warnings (userID, message) VALUES (%s, %s)",
        (warned_user_id, warning_message)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Warning sent successfully!")
    return redirect(url_for("manage_users"))

@app.route("/toggleSuspend", methods=["POST"])
def toggle_suspend():
    if "userID" not in session or session.get("usertype") != "Moderator":
        flash("Access denied.")
        return redirect(url_for("login"))

    user_id = request.form["userID"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT usertype, previous_usertype FROM users WHERE userID = %s", (user_id,))
    user = cursor.fetchone()

    if user:
        if user["usertype"] == "Suspended":
            restored_type = user["previous_usertype"] if user["previous_usertype"] else "Subscriber"
            cursor.execute("""
                UPDATE users
                SET usertype = %s, previous_usertype = NULL
                WHERE userID = %s
            """, (restored_type, user_id))
            flash(f"User {user_id} has been unsuspended.")
        else:
            cursor.execute("""
                UPDATE users
                SET previous_usertype = usertype, usertype = 'Suspended'
                WHERE userID = %s
            """, (user_id,))
            flash(f"User {user_id} has been suspended.")

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("manage_users"))

# ---------- Forgot password ----------
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("forgot_password"))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            cursor.execute(
                "UPDATE users SET password = %s WHERE email = %s",
                (new_password, email)
            )
            conn.commit()
            flash("Password has been reset. Please login with the new password.")
            cursor.close()
            conn.close()
            return redirect(url_for("login"))
        else:
            flash("Email not found.")
            cursor.close()
            conn.close()
            return redirect(url_for("forgot_password"))
    return render_template("forgot_password.html")

# ---------- Admin views ----------
@app.route("/viewAllUsers")
def view_all_users():
    if "userID" not in session or session.get("usertype") != "Admin":
        flash("Access denied.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT userID, name, email, usertype FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("viewAllUsers.html", users=users)

@app.route("/searchAccount", methods=["GET", "POST"])
def search_account():
    if "userID" not in session or session.get("usertype") != "Admin":
        flash("Access denied.")
        return redirect(url_for("login"))

    users = []
    search_term = ""

    if request.method == "POST":
        search_term = request.form["search_term"]
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT userID, name, email, usertype
            FROM users
            WHERE name LIKE %s OR email LIKE %s
        """, (f"%{search_term}%", f"%{search_term}%"))
        users = cursor.fetchall()
        cursor.close()
        conn.close()

    return render_template("searchAccount.html", users=users, search_term=search_term)

@app.route("/createUser", methods=["GET", "POST"])
def create_user():
    if "userID" not in session or session.get("usertype") != "Admin":
        flash("Access denied.")
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        usertype = request.form["usertype"]

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("create_user"))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password, usertype) VALUES (%s, %s, %s, %s)",
            (name, email, password, usertype)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("User created successfully!")
        return redirect(url_for("view_all_users"))

    return render_template("createUser.html")

@app.route("/updateUser", methods=["GET", "POST"])
def update_user():
    if "userID" not in session or session.get("usertype") != "Admin":
        flash("Access denied.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        user_id = request.form.get("userID")
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        usertype = request.form.get("usertype")

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("update_user"))

        cursor.execute("""
            UPDATE users
            SET name = %s, email = %s, password = %s, usertype = %s
            WHERE userID = %s
        """, (name, email, password, usertype, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        flash("User updated successfully!")
        return redirect(url_for("view_all_users"))

    cursor.execute("SELECT userID, name, email, usertype FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("updateUser.html", users=users)

# ---------- Dev helper ----------
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True)
