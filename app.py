from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
import os, time
import uuid
from functools import wraps
import webbrowser
import threading
import mysql.connector
from datetime import datetime
from werkzeug.utils import secure_filename
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

import nltk

# Path to bundled nltk_data (inside your repo)
nltk_data_dir = os.path.join(os.path.dirname(__file__), "nltk_data")
nltk.data.path.append(nltk_data_dir)
# Test
from nltk.tokenize import sent_tokenize
print(sent_tokenize("Hello world. This is a test."))


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
'''
def get_db_connection():
    return mysql.connector.connect(

        host="shortline.proxy.rlwy.net",
        user="root",
        password="ZavXqAKfvdBvKRUKrjhQZoMYypyHLQes",
        database="railway",
        port=52559
    )
'''
print("Connected to MySQL")
# ---------- Auth wrapper ---------- # (YY)
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

# ---------- Public pages ----------# (TIM)
@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT articleID, title, content, author, published_at, updated_at, image
        FROM articles
        ORDER BY published_at DESC
        LIMIT 4
    """)
    articles = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("index.html", articles=articles)

@app.route("/article/<int:article_id>")
def article(article_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM articles WHERE articleID = %s", (article_id,))
    article = cursor.fetchone()
    cursor.close()
    conn.close()

    #if not article: # i added this part (ZT)
        #return "Article not found", 404
    
    # --- AI Summarizer call ---
    summary_points = []
    try:
        full_text = article.get("content", "").strip()
        summary_points = summarize_to_points(full_text)
    except Exception as e:
        summary_points = [f"AI summarizer not available: {str(e)}"]

    return render_template("article.html", article=article, summary_points=summary_points)

@app.route("/search")
def search():
    query = request.args.get("q", "")
    articles = []
    no_results = False

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if query:
        cursor.execute("""
            SELECT articleID, title, content, author, published_at, updated_at, image
            FROM articles
            WHERE title LIKE %s
            ORDER BY published_at DESC
        """, ("%" + query + "%",))
        articles = cursor.fetchall()

    # If no results, load homepage articles instead
    if not articles:
        no_results = True
        cursor.execute("""
        SELECT a.articleID, a.title, a.content, a.author, a.published_at, a.image, c.name AS category
        FROM articles a
        JOIN categories c ON a.catID = c.categoryID
        ORDER BY a.published_at DESC
        LIMIT 4
    """)
        articles = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("index.html", articles=articles, no_results=no_results, search_query=query)

def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name FROM categories")
    categories = cursor.fetchall()
    conn.close()
    return categories

@app.context_processor
def inject_categories():
    return dict(nav_categories=get_categories())

@app.route("/category/<category_name>")
def category(category_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.articleID, a.title, a.content, a.author, a.published_at, a.image, c.name AS category
        FROM articles a
        JOIN categories c ON a.catID = c.categoryID
        WHERE c.name = %s
        ORDER BY a.published_at DESC
    """, (category_name,))
    articles = cursor.fetchall()

    conn.close()

    # Pass a flag if no articles found
    return render_template("index.html", articles=articles, category_name=category_name, no_articles=(len(articles) == 0))


# ---------- Role homepages ---------- # (YY)
@app.route("/adminHomepage")
@login_required("Admin")
def adminHomepage():
    if "userID" not in session or session.get("usertype") != "Admin":
        flash("Access denied.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Total users
    cursor.execute("SELECT COUNT(*) AS total FROM users")
    total_users = cursor.fetchone()['total']

    # New users today
    cursor.execute("SELECT COUNT(*) AS new_today FROM users WHERE DATE(created_at) = CURDATE()")
    new_users_today = cursor.fetchone()['new_today']

    # Suspended users (usertype = 'Suspended')
    cursor.execute("SELECT COUNT(*) AS suspended FROM users WHERE usertype='Suspended'")
    suspended_users = cursor.fetchone()['suspended']

    # Active users (everyone except Suspended)
    cursor.execute("SELECT COUNT(*) AS active FROM users WHERE usertype!='Suspended'")
    active_users = cursor.fetchone()['active']

    cursor.close()
    conn.close()

    return render_template("adminHomepage.html",
                           total_users=total_users,
                           new_users_today=new_users_today,
                           suspended_users=suspended_users,
                           active_users=active_users)

# (YY)
@app.route("/modHomepage") 
@login_required("Moderator")
def modHomepage():
    return render_template("modHomepage.html")

# (YY)
@app.route("/subscriberHomepage")
@login_required("Subscriber")
def subscriberHomepage():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    # (existing warnings query)
    cur.execute("SELECT message, created_at FROM warnings WHERE userID=%s", (session["userID"],))
    warnings = cur.fetchall()
    # Pull categories dynamically
    cur.execute("SELECT categoryID, name FROM categories ORDER BY categoryID ASC")
    categories = cur.fetchall()
    cur.close(); conn.close()
    # active tab via query param (?cat=Technology), default 'Trending'
    active_category = request.args.get("cat", "Trending")
    return render_template(
        "subscriberHomepage.html",
        warnings=warnings,
        categories=categories,
        active_category=active_category
    )

# (MW)
# API: articles feed for subscriberHomepage
@app.route("/api/articles")
@login_required("Subscriber")
def api_articles():
    cat = request.args.get("cat") 
    q     = (request.args.get("q") or "").strip()
    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    params = []
    where  = ["a.draft = FALSE"]  # <-- exclude drafts

    join   = "LEFT JOIN categories c ON a.catID = c.categoryID"
    if cat:
        where.append("c.name = %s")
        params.append(cat)

    if q:
        where.append("(a.title LIKE %s OR a.content LIKE %s)")
        like = f"%{q}%"
        params.extend([like, like])

    sql = f"""
        SELECT a.articleID, a.title, a.content, a.author,
               a.published_at, a.updated_at, a.image, c.name AS category
        FROM articles a
        {join}
        WHERE {" AND ".join(where)}
        ORDER BY COALESCE(a.published_at, a.updated_at) DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])

    cur.execute(sql, tuple(params))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

@app.route("/subscriber/create-article")
@login_required("Subscriber")
def subscriberCreateArticle():
    return render_template("subscriberCreateArticle.html")

@app.route("/api/categories")
@login_required("Subscriber")
def api_categories():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT categoryID, name FROM categories ORDER BY categoryID ASC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

@app.route("/api/articles", methods=["POST"])
@login_required("Subscriber")
def api_articles_create():
    action  = request.form.get("action", "publish").lower()  # "publish" or "draft"
    title   = (request.form.get("title") or "").strip()
    content = (request.form.get("content") or "").strip()
    cat_id  = request.form.get("category_id")  # categoryID (int)
    author  = session.get("user") or "Subscriber"

    if not title or not content or not cat_id:
        return jsonify({"ok": False, "message": "Title, content, and category are required."}), 400

    # save image (optional)
    image_rel = None
    file = request.files.get("image")
    if file and file.filename:
        img_dir = os.path.join(app.root_path, "static", "img")
        os.makedirs(img_dir, exist_ok=True)
        safe = secure_filename(file.filename)
        name, ext = os.path.splitext(safe)
        unique = f"{name}_{int(time.time())}{ext}"
        file.save(os.path.join(img_dir, unique))
        image_rel = f"/static/img/{unique}"

    # insert
    publish = (action == "publish")
    conn = get_db_connection()
    cur = conn.cursor()

    if publish:
        # publish now: draft = FALSE, set published_at/updated_at
        cur.execute("""
            INSERT INTO articles (title, content, author, published_at, updated_at, image, catID, draft)
            VALUES (%s, %s, %s, NOW(), NOW(), %s, %s, FALSE)
        """, (title, content, author, image_rel, cat_id))
    else:
        # draft: draft = TRUE; leave published_at NULL, set updated_at
        cur.execute("""
            INSERT INTO articles (title, content, author, published_at, updated_at, image, catID, draft)
            VALUES (%s, %s, %s, NULL, NOW(), %s, %s, TRUE)
        """, (title, content, author, image_rel, cat_id))

    conn.commit()
    cur.close(); conn.close()

    return jsonify({
        "ok": True,
        "message": "Article uploaded." if publish else "Draft saved.",
        "redirect": url_for("subscriberHomepage")
    })

# (MW)
# imports (if missing)
from flask import jsonify, request

@app.route("/subscriber/api/articles", endpoint="subscriber_search_api")
@login_required("Subscriber")
def subscriber_search_api():
    cat   = request.args.get("cat")
    q     = (request.args.get("q") or "").strip()
    limit = int(request.args.get("limit", 10))
    offset= int(request.args.get("offset", 0))

    conn = get_db_connection()
    cur  = conn.cursor(dictionary=True)

    where  = ["a.draft = FALSE"]   # hide drafts
    params = []

    if cat:
        where.append("c.name = %s")
        params.append(cat)

    if q:
        like = f"%{q}%"
        where.append("(a.title LIKE %s OR a.content LIKE %s)")
        params.extend([like, like])

    sql = f"""
        SELECT a.articleID, a.title, a.content, a.author,
               a.published_at, a.updated_at, a.image, c.name AS category
        FROM articles a
        LEFT JOIN categories c ON a.catID = c.categoryID
        WHERE {' AND '.join(where)}
        ORDER BY COALESCE(a.published_at, a.updated_at) DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    cur.execute(sql, tuple(params))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)


# (YY)
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
            # Instead of returning text, render template with error
            return render_template("register.html", error="This email is already registered. Please use a different email.")
        finally:
            cursor.close()
            conn.close()
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("index"))

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

    cursor.execute("SELECT name, usertype, previous_usertype FROM users WHERE userID = %s", (user_id,))
    user = cursor.fetchone()

    if user:
        if user["usertype"] == "Suspended":
            restored_type = user["previous_usertype"] if user["previous_usertype"] else "Subscriber"
            cursor.execute("""
                UPDATE users
                SET usertype = %s, previous_usertype = NULL
                WHERE userID = %s
            """, (restored_type, user_id))
            flash(f"{user['name']} has been unsuspended.")
        else:
            cursor.execute("""
                UPDATE users
                SET previous_usertype = usertype, usertype = 'Suspended'
                WHERE userID = %s
            """, (user_id,))
            flash(f"{user['name']} has been suspended.")

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
        email = request.form["email"]

        # Check if user exists and is a Subscriber
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            flash("User not found.")
        elif user["usertype"] != "Subscriber":
            flash("Only Subscribers can be updated to Author.")
        else:
            # Change Subscriber → Author
            cursor.execute(
                "UPDATE users SET usertype = 'Author' WHERE email = %s",
                (email,),
            )
            conn.commit()
            flash("User successfully updated to Author.")

    cursor.close()
    conn.close()

    return render_template("updateUser.html")


@app.route("/manageUserStatus", methods=["GET", "POST"])
def manage_user_status():
    if "userID" not in session or session.get("usertype") != "Admin":
        flash("Access denied.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        user_id = request.form.get("userID")
        action = request.form.get("action")

        # Get current user info
        cursor.execute("SELECT usertype, previous_usertype FROM users WHERE userID = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            flash("User not found.")
        else:
            if action == "suspend":
                if user["usertype"] == "Admin":
                    flash("You cannot suspend an Admin account.")
                elif user["usertype"] != "Suspended":
                    cursor.execute(
                        "UPDATE users SET previous_usertype = usertype, usertype = 'Suspended' WHERE userID = %s",
                        (user_id,)
                    )
                    flash("User suspended successfully.")

            elif action == "reactivate":
                if user["usertype"] == "Suspended" and user["previous_usertype"]:
                    cursor.execute(
                        "UPDATE users SET usertype = previous_usertype, previous_usertype = NULL WHERE userID = %s",
                        (user_id,)
                    )
                    flash("User reactivated successfully.")
                else:
                    flash("No previous role found. Cannot reactivate.")

            elif action == "delete":
                if user["usertype"] == "Admin":
                    flash("You cannot delete an Admin account.")
                else:
                    cursor.execute("DELETE FROM users WHERE userID = %s", (user_id,))
                    flash("User deleted successfully.")

        conn.commit()

    # Fetch all users
    cursor.execute("SELECT userID, name, email, usertype, previous_usertype FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("manageUserStatus.html", users=users)

@app.route("/newUsers")
def report_new_users():
    if "userID" not in session or session.get("usertype") != "Admin":
        flash("Access denied.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Example: users created in the last 7 days
    cursor.execute("""
        SELECT userID, name, email, usertype, created_at
        FROM users
        WHERE created_at >= NOW() - INTERVAL 7 DAY
        ORDER BY created_at DESC
    """)
    new_users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("newUsers.html", users=new_users)

@app.route("/articleSubmissions")
def report_article_submissions():
    if "userID" not in session or session.get("usertype") != "Admin":
        flash("Access denied.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Example: fetch articles submitted in the last 7 days
    cursor.execute("""
        SELECT articleID, title, author, created_at
        FROM articles
        WHERE created_at >= NOW() - INTERVAL 7 DAY
        ORDER BY created_at DESC
    """)
    articles = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("articleSubmissions.html", articles=articles)

@app.route("/loginActivity")
def login_activity():
    if "userID" not in session or session.get("usertype") != "Admin":
        flash("Access denied.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch last 100 login activities (most recent first)
    cursor.execute("""
        SELECT activityID, userID, email, login_time, ip_address
        FROM login_activity
        ORDER BY login_time DESC
        LIMIT 100
    """)
    activities = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("loginActivity.html", activities=activities)

@app.route("/flaggedArticles")
def flagged_articles():
    if "userID" not in session or session.get("usertype") != "Moderator":
        flash("Access denied.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all flagged articles
    cursor.execute("""
        SELECT articleID, title, author, created_at, flagged_reason, flagged_at
        FROM articles
        WHERE is_flagged = TRUE
        ORDER BY flagged_at DESC
    """)
    articles = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("flaggedArticles.html", articles=articles)
# (YY)
@app.route("/flaggedComments")
def flagged_comments():
    if "userID" not in session or session.get("usertype") != "Moderator":
        flash("Access denied.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all flagged comments
    cursor.execute("""
        SELECT commentID, content, author, articleID, created_at, flagged_reason, flagged_at
        FROM comments
        WHERE is_flagged = TRUE
        ORDER BY flagged_at DESC
    """)
    comments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("flaggedComments.html", comments=comments)
# (YY)
@app.route("/pendingArticles", methods=["GET", "POST"])
def pending_articles():
    if "userID" not in session or session.get("usertype") != "Moderator":
        flash("Access denied.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        article_id = request.form.get("articleID")
        action = request.form.get("action")
        if action == "approve":
            cursor.execute("UPDATE articles SET status='Approved' WHERE articleID=%s", (article_id,))
            flash("Article approved successfully.")
        elif action == "reject":
            cursor.execute("UPDATE articles SET status='Rejected' WHERE articleID=%s", (article_id,))
            flash("Article rejected successfully.")
        conn.commit()

    cursor.execute("SELECT articleID, title, author, created_at FROM articles WHERE status='Pending'")
    articles = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("pendingArticles.html", articles=articles)
# (YY)
@app.route("/manageCategories", methods=["GET"])
def manage_categories():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("manageCategories.html", categories=categories)
# (YY)
@app.route("/manageCategories/create", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        name = request.form.get("categoryName").strip()
        description = request.form.get("categoryDescription").strip()

        if not name:
            flash("Category name cannot be empty.", "error")
            return redirect(url_for("add_category"))

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if category already exists
        cursor.execute("SELECT * FROM categories WHERE name = %s", (name,))
        existing = cursor.fetchone()
        if existing:
            flash("Category already exists.", "error")
            cursor.close()
            conn.close()
            return redirect(url_for("add_category"))

        # Insert new category with description
        cursor.execute(
            "INSERT INTO categories (name, description) VALUES (%s, %s)",
            (name, description)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Category added successfully.", "success")
        return redirect(url_for("manage_categories"))

    # GET request
    return render_template("createCategory.html")
# (YY)
@app.route("/manageCategories/update", methods=["GET", "POST"])
def update_category():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        categoryID = request.form.get("categoryID")
        name = request.form.get("categoryName").strip()
        description = request.form.get("categoryDescription").strip()

        if not name:
            flash("Category name cannot be empty.", "error")
            return redirect(url_for("update_category"))

        cursor.execute(
            "UPDATE categories SET name=%s, description=%s WHERE categoryID=%s",
            (name, description, categoryID)
        )
        conn.commit()
        flash("Category updated successfully.", "success")
        return redirect(url_for("manage_categories"))

    # GET request: load all categories to select which to update
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("updateCategory.html", categories=categories)

# (YY)
@app.route("/manageCategories/delete", methods=["GET"])
def delete_category_page():
    search = request.args.get("search", "")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if search:
        cursor.execute("SELECT * FROM categories WHERE name LIKE %s ORDER BY name ASC", ('%' + search + '%',))
    else:
        cursor.execute("SELECT * FROM categories ORDER BY name ASC")

    categories = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("deleteCategory.html", categories=categories)

# Handle actual deletion (YY)
@app.route("/manageCategories/delete/<int:categoryID>", methods=["POST"])
def delete_category(categoryID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE categoryID=%s", (categoryID,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Category deleted successfully.", "success")
    return redirect(url_for("delete_category_page"))


# ---------- AI Summarizer -------
# to summarize text and convert to bullet points
def summarize_to_points(text, sentences_count=5):
    if not text.strip():
        return ["No summary available"]

    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences_count)
    return [str(s) for s in summary]



# endpoint: to receive article text and return bullet-point summary
@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    text = data.get("text", "")

    try:
        bullet_points = summarize_to_points(text)
        return jsonify({"summary": bullet_points})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Dev helper ----------
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True)
