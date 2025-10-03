from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response, abort, make_response
import os, time
import uuid
from functools import wraps
import webbrowser
import threading
import mysql.connector
from datetime import datetime, timezone
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
def login_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            # If no session → force logout
            if "userID" not in session:
                session.clear()
                return redirect(url_for("login"))

            # If a role is required → check it
            if role and session.get("usertype") != role:
                # Wrong role? Destroy session completely
                session.clear()
                flash("Access denied. Please log in again.", "danger")
                return redirect(url_for("login"))

            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# ---------- Public pages ----------# (TIM)
@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT articleID, title, content, author, published_at, updated_at, image
        FROM articles
        ORDER BY published_at DESC
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
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch user stats
    cursor.execute("SELECT COUNT(*) AS total FROM users")
    total_users = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS new_today FROM users WHERE DATE(created_at) = CURDATE()")
    new_users_today = cursor.fetchone()["new_today"]

    cursor.execute("SELECT COUNT(*) AS suspended FROM users WHERE usertype='Suspended'")
    suspended_users = cursor.fetchone()["suspended"]

    cursor.execute("SELECT COUNT(*) AS active FROM users WHERE usertype!='Suspended'")
    active_users = cursor.fetchone()["active"]

    cursor.close()
    conn.close()

    # Render template directly; @after_request will handle no-cache headers
    return render_template(
        "adminHomepage.html",
        total_users=total_users,
        new_users_today=new_users_today,
        suspended_users=suspended_users,
        active_users=active_users,
    )

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
    action  = request.form.get("action", "publish").lower()
    title   = (request.form.get("title") or "").strip()
    content = (request.form.get("content") or "").strip()
    cat_id  = request.form.get("category_id")
    author  = session.get("user") or "Subscriber"

    if not title or not content or not cat_id:
        return jsonify({"ok": False, "message": "Title, content, and category are required."}), 400

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

    publish = (action == "publish")
    conn = get_db_connection()
    cur = conn.cursor()

    if publish:
        cur.execute("""
            INSERT INTO articles (title, content, author, published_at, updated_at, image, catID, draft)
            VALUES (%s, %s, %s, NOW(), NOW(), %s, %s, FALSE)
        """, (title, content, author, image_rel, cat_id))
    else:
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
@app.route("/subscriber/api/articles", endpoint="subscriber_search_api")
@login_required("Subscriber")
def subscriber_search_api():
    cat   = request.args.get("cat")
    q     = (request.args.get("q") or "").strip()
    limit = int(request.args.get("limit", 10))
    offset= int(request.args.get("offset", 0))

    conn = get_db_connection()
    cur  = conn.cursor(dictionary=True)

    where  = ["a.draft = FALSE"]
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

# (MW)
# -------View route (full-page article, shows pin state)----------------
@app.route("/subscriber/article/<int:article_id>")
@login_required("Subscriber")
def subscriber_article_view(article_id):
    conn = get_db_connection()
    cur  = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT a.articleID, a.title, a.content, a.author,
               a.published_at, a.updated_at,
               CASE
                 WHEN a.image IS NULL OR a.image = '' THEN NULL
                 WHEN a.image LIKE 'http%' THEN a.image
                 WHEN a.image LIKE '/static/%' THEN a.image
                 WHEN a.image LIKE '../static/%' THEN REPLACE(a.image, '../static', '/static')
                 ELSE CONCAT('/static/img/', a.image)
               END AS image,
               c.name AS category
        FROM articles a
        LEFT JOIN categories c ON a.catID = c.categoryID
        WHERE a.articleID = %s
          AND a.draft = FALSE
        LIMIT 1
    """, (article_id,))
    article = cur.fetchone()
    if not article:
        cur.close(); conn.close()
        abort(404)

    # pin state...
    cur.execute("SELECT 1 FROM subscriber_pins WHERE userID=%s AND articleID=%s LIMIT 1",
                (session["userID"], article_id))
    is_pinned = cur.fetchone() is not None

    cur.close(); conn.close()
    return render_template("subscriberArticleView.html", article=article, is_pinned=is_pinned)

@app.route("/subscriber/api/pin", methods=["POST"])
@login_required("Subscriber")
def subscriber_toggle_pin():
    data = request.get_json(silent=True) or {}
    article_id = data.get("articleID")

    if not article_id:
        return jsonify(ok=False, message="articleID is required"), 400

    conn = get_db_connection()
    cur  = conn.cursor()

    # Check current state
    cur.execute("""
        SELECT id FROM subscriber_pins
        WHERE userID=%s AND articleID=%s
        LIMIT 1
    """, (session["userID"], article_id))
    row = cur.fetchone()

    if row:
        cur.execute("DELETE FROM subscriber_pins WHERE id=%s", (row[0],))
        conn.commit()
        cur.close(); conn.close()
        return jsonify(ok=True, state="unpinned", message="Article unpinned")
    else:
        try:
            cur.execute("""
                INSERT INTO subscriber_pins (userID, articleID)
                VALUES (%s, %s)
            """, (session["userID"], article_id))
            conn.commit()
            cur.close(); conn.close()
            return jsonify(ok=True, state="pinned", message="Article pinned")
        except Exception as e:
            conn.rollback()
            cur.close(); conn.close()
            return jsonify(ok=False, message="Unable to pin"), 500

# --- My Articles: page ---
@app.route("/subscriber/my-articles")
@login_required("Subscriber")
def subscriber_my_articles():
    return render_template("subscriberMyArticles.html")

# --- My Articles: JSON API ---
@app.route("/subscriber/api/my-articles")
@login_required("Subscriber")
def subscriber_api_my_articles():
    status = (request.args.get("status") or "all").lower()
    limit  = int(request.args.get("limit", 20))
    offset = int(request.args.get("offset", 0))

    conn = get_db_connection()
    cur  = conn.cursor(dictionary=True)

    where  = ["a.author = %s"]                      
    params = [session.get("user")]                   

    if status == "published":
        where.append("a.draft = FALSE")
    elif status == "drafts":
        where.append("a.draft = TRUE")

    cur.execute(f"""
        SELECT a.articleID, a.title, a.content, a.draft,
               a.published_at, a.updated_at,
               CASE
                 WHEN a.image IS NULL OR a.image = '' THEN NULL
                 WHEN a.image LIKE 'http%' THEN a.image
                 WHEN a.image LIKE '/static/%' THEN a.image
                 WHEN a.image LIKE '../static/%' THEN REPLACE(a.image, '../static', '/static')
                 ELSE CONCAT('/static/img/', a.image)
               END AS image,
               c.name AS category
        FROM articles a
        LEFT JOIN categories c ON a.catID = c.categoryID
        WHERE {" AND ".join(where)}
        ORDER BY COALESCE(a.published_at, a.updated_at) DESC
        LIMIT %s OFFSET %s
    """, (*params, limit, offset))

    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

# View: load edit page 
@app.route("/subscriber/edit-article/<int:article_id>")
@login_required("Subscriber")
def subscriber_edit_article(article_id):
    conn = get_db_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT a.articleID, a.title, a.content, a.catID, a.image, a.draft,
               a.published_at, a.updated_at
        FROM articles a
        WHERE a.articleID = %s AND a.author = %s
        LIMIT 1
    """, (article_id, session.get("user")))
    article = cur.fetchone()
    cur.close(); conn.close()
    if not article:
        return ("Forbidden", 403)
    return render_template("subscriberEditArticles.html", article=article)

# API: update article 
@app.route("/subscriber/api/article/<int:article_id>", methods=["POST"])
@login_required("Subscriber")
def subscriber_update_article(article_id):
    action      = (request.form.get("action") or "").lower()   # 'draft' | 'publish'
    title       = (request.form.get("title") or "").strip()
    content     = (request.form.get("content") or "").strip()
    category_id = request.form.get("category_id")
    image_file  = request.files.get("image")

    if not title or not content or not category_id:
        return jsonify(ok=False, message="Title, content and category are required."), 400

    draft_flag = (action != "publish")

    conn = get_db_connection()
    cur  = conn.cursor(dictionary=True)

    cur.execute("SELECT author FROM articles WHERE articleID=%s LIMIT 1", (article_id,))
    row = cur.fetchone()
    if not row or row["author"] != session.get("user"):
        cur.close(); conn.close()
        return jsonify(ok=False, message="Forbidden"), 403

    image_name = None
    if image_file and image_file.filename:
        image_name = image_file.filename
        image_path = os.path.join(app.static_folder, "img", image_name)
        image_file.save(image_path)

    # Build UPDATE
    fields = ["title=%s", "content=%s", "catID=%s", "draft=%s", "updated_at=NOW()"]
    params = [title, content, category_id, draft_flag]

    if not draft_flag:
        fields.append("published_at=NOW()")

    if image_name:
        fields.append("image=%s")
        params.append(image_name)

    params.append(article_id)

    cur.execute(f"UPDATE articles SET {', '.join(fields)} WHERE articleID=%s", params)
    conn.commit()
    cur.close(); conn.close()

    return jsonify(ok=True, message="Saved.", redirect=url_for("subscriber_my_articles"))

# Bookmarks page
@app.route("/subscriber/bookmarks")
@login_required("Subscriber")
def subscriber_bookmarks():
    return render_template("subscriberBookmarks.html")

# Bookmarks data for the logged-in user
@app.route("/subscriber/api/bookmarks")
@login_required("Subscriber")
def subscriber_api_bookmarks():
    uid = session.get("userID")
    if uid is None:
        return jsonify(ok=False, message="Not logged in"), 401

    conn = get_db_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT a.articleID, a.title, a.content, a.author,
               a.published_at, a.updated_at,
               CASE
                 WHEN a.image IS NULL OR a.image = '' THEN NULL
                 WHEN a.image LIKE 'http%%' THEN a.image
                 WHEN a.image LIKE '/static/%%' THEN a.image
                 WHEN a.image LIKE '../static/%%' THEN REPLACE(a.image, '../static', '/static')
                 ELSE CONCAT('/static/img/', a.image)
               END AS image,
               c.name AS category,
               sp.pinned_at
        FROM subscriber_pins sp
        JOIN articles a        ON a.articleID = sp.articleID
        LEFT JOIN categories c ON a.catID = c.categoryID
        WHERE sp.userID = %s
          AND (a.draft IS NULL OR a.draft = FALSE)
        ORDER BY sp.pinned_at DESC
    """, (uid,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(rows)

# --- (MW) Subscriber comment functions ------
def _timeago(ts):
    # naive, good-enough "x min ago"
    if not ts:
        return ""
    if isinstance(ts, str):
        try:
            ts = datetime.fromisoformat(ts.replace("Z",""))
        except Exception:
            return ""
    now = datetime.now(timezone.utc)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    delta = int((now - ts).total_seconds())
    if delta < 60:  return "just now"
    if delta < 3600: return f"{delta//60}m ago"
    if delta < 86400: return f"{delta//3600}h ago"
    return f"{delta//86400}d ago"

@app.get("/subscriber/api/comments")
@login_required()
def subscriber_api_comments():
    from flask import jsonify, request, session

    article_id = int(request.args.get("article_id", 0))
    uid = session.get("userID")  # <- use the correct session key

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # 1) Load comments for this article
    cur.execute("""
        SELECT
            c.commentID,
            c.comment_text,
            c.likes,
            c.dislikes,
            c.created_at,
            c.userID,
            u.name AS author,
            (c.userID = %s) AS mine
        FROM comments c
        JOIN users u ON u.userID = c.userID
        WHERE c.articleID = %s
        ORDER BY c.created_at DESC
    """, (uid, article_id))
    rows = cur.fetchall()

    # 2) Load my reaction (like/dislike) for these comments, if any
    my_reaction_map = {}
    if rows:
        comment_ids = [str(r["commentID"]) for r in rows]
        # Build a safe IN (...) list; since these come from DB rows, it’s fine to join
        in_clause = ",".join(comment_ids)

        cur.execute(f"""
            SELECT commentID, reaction
            FROM comment_reactions
            WHERE userID = %s AND commentID IN ({in_clause})
        """, (uid,))
        for r in cur.fetchall():
            # if both existed somehow, last write wins; normally there’s a UNIQUE(userID, commentID)
            my_reaction_map[r["commentID"]] = r["reaction"]

    cur.close()
    conn.close()

    # 3) Shape API payload
    def to_iso(dt):
        try:
            return dt.isoformat()
        except Exception:
            return None

    out = []
    for r in rows:
        out.append({
            "commentID": r["commentID"],
            "text": r["comment_text"],
            "likes": int(r["likes"] or 0),
            "dislikes": int(r["dislikes"] or 0),
            "created_at": to_iso(r["created_at"]),
            "time_ago": "",  # optional: compute on server or format on client
            "author": r["author"] or "Anonymous",
            "mine": bool(r["mine"]),
            "my_reaction": my_reaction_map.get(r["commentID"])  # "like" | "dislike" | None
        })

    return jsonify(out)


@app.post("/subscriber/api/comments")
@login_required("Subscriber")
def subscriber_api_comment_create():
    uid = session.get("userID")
    article_id = request.form.get("articleID", type=int)
    text = (request.form.get("text") or "").strip()
    parent_id = request.form.get("parent_id", type=int)

    if not article_id or not text:
        return jsonify(ok=False, message="articleID and text required"), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO comments (articleID, userID, comment_text, is_reply, reply_to_comment_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (article_id, uid, text, 1 if parent_id else 0, parent_id))
    conn.commit()
    new_id = cur.lastrowid
    cur.close(); conn.close()
    return jsonify(ok=True, commentID=new_id)

@app.put("/subscriber/api/comments/<int:comment_id>")
@login_required("Subscriber")
def subscriber_api_comment_update(comment_id):
    uid = session.get("userID")
    text = (request.json.get("text") or "").strip()
    if not text:
        return jsonify(ok=False, message="text required"), 400

    conn = get_db_connection()
    cur = conn.cursor()
    # ensure ownership
    cur.execute("SELECT userID FROM comments WHERE commentID=%s", (comment_id,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close(); return jsonify(ok=False, message="Not found"), 404
    if row[0] != uid:
        cur.close(); conn.close(); return jsonify(ok=False, message="Forbidden"), 403

    cur.execute("UPDATE comments SET comment_text=%s WHERE commentID=%s", (text, comment_id))
    conn.commit()
    cur.close(); conn.close()
    return jsonify(ok=True)

@app.delete("/subscriber/api/comments/<int:comment_id>")
@login_required("Subscriber")
def subscriber_api_comment_delete(comment_id):
    uid = session.get("userID")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT userID FROM comments WHERE commentID=%s", (comment_id,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close(); return jsonify(ok=False, message="Not found"), 404
    if row[0] != uid:
        cur.close(); conn.close(); return jsonify(ok=False, message="Forbidden"), 403
    cur.execute("DELETE FROM comments WHERE commentID=%s", (comment_id,))
    conn.commit()
    cur.close(); conn.close()
    return jsonify(ok=True)

@app.post("/subscriber/api/comments/<int:comment_id>/react")
@login_required("Subscriber")
def subscriber_api_comment_react(comment_id):
    uid = session.get("userID")
    action = (request.json.get("action") or "").lower()  # "like"|"dislike"|"clear"

    if action not in ("like", "dislike", "clear"):
        return jsonify(ok=False, message="Invalid action"), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # read current
    cur.execute("""SELECT reaction FROM comment_reactions WHERE commentID=%s AND userID=%s""",
                (comment_id, uid))
    row = cur.fetchone()
    prev = row[0] if row else None

    # counters first (get current counts)
    cur.execute("SELECT likes, dislikes FROM comments WHERE commentID=%s", (comment_id,))
    cd = cur.fetchone()
    if not cd:
        cur.close(); conn.close()
        return jsonify(ok=False, message="Comment not found"), 404
    likes, dislikes = cd

    # apply transitions
    if action == "clear":
        if prev == "like":
            likes = max(0, likes - 1)
        elif prev == "dislike":
            dislikes = max(0, dislikes - 1)
        if prev:
            cur.execute("DELETE FROM comment_reactions WHERE commentID=%s AND userID=%s",
                        (comment_id, uid))
    else:
        if prev == action:
            # toggle off same action
            if action == "like":   likes = max(0, likes - 1)
            else:                  dislikes = max(0, dislikes - 1)
            cur.execute("DELETE FROM comment_reactions WHERE commentID=%s AND userID=%s",
                        (comment_id, uid))
            action = "clear"
        else:
            # switch or create
            if prev == "like":
                likes = max(0, likes - 1)
            elif prev == "dislike":
                dislikes = max(0, dislikes - 1)
            if action == "like":
                likes += 1
            else:
                dislikes += 1
            cur.execute("""
                INSERT INTO comment_reactions (commentID, userID, reaction)
                VALUES (%s,%s,%s)
                ON DUPLICATE KEY UPDATE reaction=VALUES(reaction), updated_at=CURRENT_TIMESTAMP
            """, (comment_id, uid, action))

    # persist counters
    cur.execute("UPDATE comments SET likes=%s, dislikes=%s WHERE commentID=%s",
                (likes, dislikes, comment_id))
    conn.commit()
    cur.close(); conn.close()

    return jsonify(ok=True, likes=likes, dislikes=dislikes, state=None if action=="clear" else action)

# (YY)
# ---------- Auth ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    remembered_email = request.cookies.get("remembered_email")  # Get cookie if exists

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        remember = request.form.get("remember")  # Checkbox returns "on" if checked, None if not

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            if password == user["password"]:
                # Block suspended BEFORE setting session
                if user["usertype"].lower() == "suspended":
                    flash("Your account has been suspended. Please contact support.")
                    return redirect(url_for("login"))

                # Set session
                session["userID"] = user["userID"]
                session["usertype"] = user["usertype"]
                session["user"] = user["name"]

                role_redirects = {
                    "Admin": "adminHomepage",
                    "Moderator": "modHomepage",
                    "Subscriber": "subscriberHomepage",
                    "Author": "authorHomepage"
                }

                redirect_route = role_redirects.get(user["usertype"])
                resp = redirect(url_for(redirect_route) if redirect_route else url_for("login"))

                # Handle "Remember Me"
                if remember:
                    # Save email in a cookie for 30 days
                    resp.set_cookie("remembered_email", email, max_age=30*24*60*60)
                else:
                    # Remove cookie if unchecked
                    resp.delete_cookie("remembered_email")

                if not redirect_route:
                    flash("Invalid user type.")
                return resp

            else:
                flash("Incorrect password.")
                return redirect(url_for("login"))
        else:
            flash("User not found.")
            return redirect(url_for("login"))

    return render_template("login.html", remembered_email=remembered_email)

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
    resp = redirect(url_for("login"))
    resp.delete_cookie("session")  # kill session cookie
    flash("You have been logged out successfully.")
    return resp

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response

# ---------- Moderator: manage users ----------
@app.route("/manageUsers")
@login_required("Moderator")
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
@login_required("Moderator")
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
@login_required("Moderator")
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
@login_required("Admin")
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
@login_required("Admin")
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
@login_required("Admin")
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
        return redirect(url_for("create_user"))

    return render_template("createUser.html")

@app.route("/updateUser", methods=["GET", "POST"])
@login_required("Admin")
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
@login_required("Admin")
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
@login_required("Admin")
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
@login_required("Admin")
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
@login_required("Admin")
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
@login_required("Moderator")
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
@login_required("Moderator")
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
@login_required("Moderator")
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
@login_required("Moderator")
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
@login_required("Moderator")
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
@login_required("Moderator")
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
@login_required("Moderator")
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
@login_required("Moderator")
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
