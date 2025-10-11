from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response, abort, make_response
import os, io, re, time, uuid, time, zipfile, shutil, secrets
from functools import wraps
import webbrowser
import threading
import mysql.connector
import json
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from rapidfuzz import process, fuzz
import fitz
from pathlib import Path
from docx import Document
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from deep_translator import GoogleTranslator
from utils.profanity_filter import contains_profanity, censor_text
from typing import Optional

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

@app.route("/api/articles", methods=["POST"], endpoint="api_articles_post")
@login_required("Subscriber")
def api_articles_create():
    action  = (request.form.get("action") or "publish").lower()
    title   = (request.form.get("title") or "").strip()
    content = (request.form.get("content") or "").strip()
    cat_id  = request.form.get("category_id")
    author  = session.get("user") or "Subscriber"

    if not title or not content or not cat_id:
        return jsonify({"ok": False, "message": "Title, content, and category are required."}), 400

    # basic profanity gate (keep your own functions if you have them)
    try:
        if contains_profanity(title) or contains_profanity(content):
            return jsonify({"ok": False, "message": "Your article contains blocked words. Please revise and try again."}), 400
    except Exception:
        # if the profanity lib fails, don't hard block publishing
        pass

    image_rel = None
    img_dir_fs = os.path.join(app.root_path, "static", "img")

    # 1) Directly uploaded file has highest priority
    up = request.files.get("image")
    if up and up.filename:
        os.makedirs(img_dir_fs, exist_ok=True)
        safe = secure_filename(up.filename)
        name, ext = os.path.splitext(safe)
        unique = f"{name}_{int(time.time())}{ext}"
        up.save(os.path.join(img_dir_fs, unique))
        image_rel = f"/static/img/{unique}"
    else:
        # 2) Else, cover_url from importer (points to /static/uploads/articles/...)
        cover_url = request.form.get("cover_url")
        if cover_url:
            copied = _copy_static_file(cover_url, img_dir_fs)
            if copied:
                image_rel = copied

    # 3) (Optional) also persist any other extracted images if provided (not used by DB image field)
    #    frontend sends JSON array in 'import_images'; we copy them into static/img for permanence.
    try:
        import_images_json = request.form.get("import_images", "[]")
        import_images = json.loads(import_images_json) if import_images_json else []
        if isinstance(import_images, list):
            for rel in import_images:
                _copy_static_file(rel, img_dir_fs)
    except Exception:
        pass  # non-fatal

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

def _copy_static_file(rel_url: str, dest_dir: str) -> Optional[str]:
    """
    rel_url: like '/static/uploads/articles/<batch>/img/file.png'
    dest_dir: absolute filesystem dir for static/img
    Returns a new web path '/static/img/<unique>' or None.
    """
    if not rel_url or not rel_url.startswith("/static/"):
        return None

    src_path = Path(app.root_path, rel_url.lstrip("/")).resolve()
    if not src_path.exists() or not src_path.is_file():
        return None

    dest_dir_path = Path(dest_dir)
    dest_dir_path.mkdir(parents=True, exist_ok=True)

    stem = src_path.stem
    ext  = src_path.suffix
    unique = f"{stem}_{int(time.time())}{ext}"
    dest_path = dest_dir_path / unique

    shutil.copy2(src_path, dest_path)
    return f"/static/img/{unique}"

# (MW) --------Import document, extract text & images--------
@app.post("/subscriber/api/import-article")
@login_required("Subscriber")
def api_import_article():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify(ok=False, message="No file provided"), 400

    ext = os.path.splitext(file.filename.lower())[1]
    if ext not in {".txt", ".pdf", ".doc", ".docx"}:
        return jsonify(ok=False, message="Unsupported file type"), 400

    raw = file.read()
    if not raw:
        return jsonify(ok=False, message="Empty file"), 400

    base_id = uuid.uuid4().hex[:12]
    base_dir = os.path.join(app.static_folder, "uploads", "articles", base_id)
    img_dir  = os.path.join(base_dir, "img")
    os.makedirs(img_dir, exist_ok=True)

    text = ""
    img_names = []

    try:
        if ext == ".txt":
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("latin-1", errors="ignore")
        elif ext == ".pdf":
            text, img_names = _extract_from_pdf(raw, img_dir, base_id)
        elif ext == ".docx":
            text = _extract_text_docx(raw)
            img_names = _extract_images_docx(raw, img_dir, base_id)
        elif ext == ".doc":
            try:
                docx_bytes = _convert_doc_to_docx(raw)
            except Exception as e:
                return jsonify(ok=False, message=f".doc conversion failed: {e}"), 400
            text = _extract_text_docx(docx_bytes)
            img_names = _extract_images_docx(docx_bytes, img_dir, base_id)
    except Exception as e:
        return jsonify(ok=False, message=f"Import failed: {e}"), 500

    _save_text_file(text, base_dir, base_id)  # optional

    base_url = f"/static/uploads/articles/{base_id}/img"
    img_urls = [f"{base_url}/{name}" for name in img_names]

    return jsonify(ok=True, text=text, images=img_urls)

def _extract_from_pdf(raw_bytes: bytes, img_dir: str, base_id: str):
    os.makedirs(img_dir, exist_ok=True)
    text_parts = []
    image_names = []

    doc = fitz.open(stream=raw_bytes, filetype="pdf")
    try:
        for page_index in range(len(doc)):
            page = doc[page_index]
            # text
            text_parts.append(page.get_text())

            # images
            for img in page.get_images(full=True):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                try:
                    if pix.alpha:  # remove alpha for consistent PNGs
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    fname = f"p{page_index+1:03d}-{xref}.png"
                    out_path = os.path.join(img_dir, fname)
                    pix.save(out_path)
                    image_names.append(fname)
                finally:
                    pix = None
        full_text = "\n".join(text_parts).strip()
        return full_text, image_names
    finally:
        doc.close()


def _extract_text_docx(raw_bytes: bytes) -> str:
    doc = Document(io.BytesIO(raw_bytes))
    parts = [p.text for p in doc.paragraphs if p.text]
    # also consider tables (optional)
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                if cell.text:
                    parts.append(cell.text)
    text = "\n".join(parts)
    # normalize a bit
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def _extract_images_docx(raw_bytes: bytes, img_dir: str, base_id: str):
    os.makedirs(img_dir, exist_ok=True)
    image_names = []
    with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
        for name in zf.namelist():
            # embedded images live under word/media/
            if name.startswith("word/media/") and not name.endswith("/"):
                data = zf.read(name)
                fname = os.path.basename(name)
                out_path = os.path.join(img_dir, fname)
                with open(out_path, "wb") as f:
                    f.write(data)
                image_names.append(fname)
    return image_names


def _convert_doc_to_docx(raw_bytes: bytes) -> bytes:
    import tempfile, win32com.client as win32
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "in.doc")
        dst = os.path.join(td, "out.docx")
        with open(src, "wb") as f: f.write(raw_bytes)

        word = win32.gencache.EnsureDispatch('Word.Application')
        word.Visible = False
        doc = word.Documents.Open(src)
        try:
            wdFormatXMLDocument = 12
            doc.SaveAs(dst, FileFormat=wdFormatXMLDocument)
        finally:
            doc.Close(False)
            word.Quit()

        with open(dst, "rb") as f:
            return f.read()


def _save_text_file(text: str, base_dir: str, base_id: str):
    os.makedirs(base_dir, exist_ok=True)
    out_path = os.path.join(base_dir, "extracted.txt")
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text or "")
    except Exception:
        # Non-fatal; ignore disk errors here
        pass


# (MW) ------AI: suggest title, clean up text, pick category------
@app.post("/subscriber/api/ai-suggest")
@login_required("Subscriber")
def api_ai_suggest():
    # Read JSON
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify(ok=False, message="Invalid JSON"), 400

    text = (data.get("text") or "").strip()
    if not text:
        return jsonify(ok=False, message="No text provided"), 400

    # Fetch categories via MySQL
    conn = get_db_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT categoryID, name FROM categories ORDER BY name")
    categories = cur.fetchall()
    cur.close(); conn.close()
    if not categories:
        return jsonify(ok=False, message="No categories configured"), 500

    # Heuristic title & cleanup
    def simple_title(t: str) -> str:
        for line in t.splitlines():
            s = line.strip()
            if len(s) >= 8:
                return s[:90].rstrip(" .!?:;")
        t = t.strip()
        return (t[:80] + "…") if len(t) > 80 else (t or "Untitled")

    def basic_cleanup(t: str) -> str:
        t = re.sub(r"[ \t]+", " ", t or "")
        t = re.sub(r"\n{3,}", "\n\n", t)
        return t.strip()

    title = simple_title(text)
    corrected = basic_cleanup(text)

    # Pick category by fuzzy match across full text
    choices = [c["name"] for c in categories]
    STOP = set("""
    a an the and or of for to in on with as at by from this that those these is are was were be been being
    it its they them their we our you your i me my he she his her which who whom whose will would should could
    """.split())

    words = re.findall(r"[A-Za-z]{3,}", corrected.lower())
    words = [w for w in words if w not in STOP and len(w) >= 4]

    from collections import Counter
    top_terms = [w for w, _n in Counter(words).most_common(30)] or ["general"]
    query = " ".join(top_terms)

    match = process.extractOne(query, choices, scorer=fuzz.WRatio)
    if match:
        cat_name, score, idx = match
        cat_id = categories[idx]["categoryID"]
    else:
        cat_id  = categories[0]["categoryID"]
        cat_name= categories[0]["name"]

    return jsonify(
        ok=True,
        title=title,
        corrected_text=corrected,
        category_id=cat_id,
        category_name=cat_name
    )

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
@login_required("Subscriber")
def subscriber_api_comments():
    from flask import jsonify, request, session

    article_id = int(request.args.get("article_id", 0))
    uid = session.get("userID")  # <- use the correct session key

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # 1) Load comments for this article (include parent fields)
    cur.execute("""
        SELECT
            c.commentID,
            c.comment_text,
            c.likes,
            c.dislikes,
            c.created_at,
            c.userID,
            c.is_reply,
            c.reply_to_comment_id,
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
        in_clause = ",".join(comment_ids)
        cur.execute(f"""
            SELECT commentID, reaction
            FROM comment_reactions
            WHERE userID = %s AND commentID IN ({in_clause})
        """, (uid,))
        for r in cur.fetchall():
            my_reaction_map[r["commentID"]] = r["reaction"]

    cur.close()
    conn.close()

    # Helper to ISO-date
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
            "author": r["author"] or "Anonymous",
            "mine": bool(r["mine"]),
            "my_reaction": my_reaction_map.get(r["commentID"]),  # "like" | "dislike" | None
            "is_reply": bool(r.get("is_reply")),
            "parent_id": r.get("reply_to_comment_id")  # null or int
        })

    return jsonify(out)


@app.post("/subscriber/api/comments")
@login_required("Subscriber")
def subscriber_api_comment_create():
    from flask import request, jsonify, session
    uid = session.get("userID")
    article_id = request.form.get("articleID")
    text = request.form.get("text", "").strip()
    parent_id = request.form.get("parent_id")

    if not text:
        return jsonify({"ok": False, "error": "Empty comment."}), 400

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # ✅ Ensure 1-level replies only (reply to top-level)
    top_parent_id = None
    if parent_id:
        try:
            pid = int(parent_id)
            cur.execute("SELECT reply_to_comment_id FROM comments WHERE commentID=%s", (pid,))
            row = cur.fetchone()
            if row:
                # if the parent already has a parent, use that (force top-level)
                top_parent_id = row["reply_to_comment_id"] or pid
            else:
                top_parent_id = pid
        except Exception:
            top_parent_id = None

    cur.close()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO comments (articleID, userID, comment_text, is_reply, reply_to_comment_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (article_id, uid, text, bool(top_parent_id), top_parent_id))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"ok": True})


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

@app.route("/subscriber/report_article", methods=["POST"])
def report_article():
    data = request.get_json()
    article_id = data.get("articleID")
    reason = data.get("reason")
    details = data.get("details", "")
    
    reporter_id = session.get("userID")
    if not reporter_id:
        return jsonify({"message": "User not logged in."}), 401

    if not article_id or not reason:
        return jsonify({"message": "Article ID and reason are required."}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 🟩 Step 1: Check if this user already reported this article
        cursor.execute(
            """
            SELECT 1 FROM article_reports
            WHERE article_id = %s AND reporter_id = %s
            """,
            (article_id, reporter_id)
        )
        existing = cursor.fetchone()
        if existing:
            return jsonify({"message": "You have already reported this article."}), 400

        # 🟩 Step 2: Insert new report
        cursor.execute(
            """
            INSERT INTO article_reports (article_id, reporter_id, reason, details)
            VALUES (%s, %s, %s, %s)
            """,
            (article_id, reporter_id, reason, details)
        )
        conn.commit()
        return jsonify({"message": "Report submitted successfully."})

    except mysql.connector.Error as err:
        print("Database error:", err)
        return jsonify({"message": "An error occurred while submitting your report."}), 500
    finally:
        cursor.close()
        conn.close()


# (MW) --------------Profile page----------------
def save_profile_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    safe = secure_filename(file_storage.filename)
    name, ext = os.path.splitext(safe)
    if ext.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        raise ValueError("Unsupported image type")
    unique = f"{name}_{int(time.time())}{ext}"
    dest_dir = Path(app.root_path) / "static" / "profilePictures"
    dest_dir.mkdir(parents=True, exist_ok=True)
    file_storage.save(dest_dir / unique)
    return f"/static/profilePictures/{unique}"

@app.route("/profile")
@login_required("Subscriber")
def profile():
    uid = session["userID"]

    conn = get_db_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT userID, name, email, usertype, image, bio
        FROM users
        WHERE userID=%s
        LIMIT 1
    """, (uid,))
    u = cur.fetchone()
    cur.close(); conn.close()

    if not u:
        flash("User not found.", "error")
        return redirect(url_for("subscriberHomepage"))

    # Normalize stored image paths so the browser can render them
    img = (u.get("image") or "")
    if img.startswith("../static/"):
        u["image"] = img.replace("../static", "/static")
    elif img.startswith("./static/"):
        u["image"] = img.replace("./static", "/static")

    # Optional: also pass a 'profile' dict since the template may use either
    profile = {
        "display_name": u["name"],
        "email": u["email"],
        "usertype": u["usertype"],
        "bio": u.get("bio"),
        "avatar_url": u.get("image"),
    }

    # Your template expects 'pinned' and 'articles' too; pass empty lists for now
    return render_template(
        "subscriberProfile.html",
        user=u,
        profile=profile,
        pinned=[],
        articles=[]
    )

@app.route("/profile/update", methods=["POST"])
@login_required("Subscriber")
def profile_update():
    uid = session["userID"]
    next_url = request.form.get("next") or request.referrer or url_for("subscriberHomepage")

    name = (request.form.get("name") or "").strip()
    bio  = (request.form.get("bio")  or "").strip()
    avatar_file = request.files.get("avatar")

    # --- fetch current user values for change detection ---
    conn = get_db_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT name, bio, image FROM users WHERE userID=%s LIMIT 1", (uid,))
    row = cur.fetchone()
    cur.close()

    current_name = (row.get("name") or "").strip() if row else ""
    current_bio  = (row.get("bio") or "").strip() if row else ""
    # NOTE: we only treat avatar as changed if a file is uploaded

    no_text_change = (name == current_name and bio == current_bio)
    no_avatar_upload = not (avatar_file and avatar_file.filename)

    if no_text_change and no_avatar_upload:
        # nothing to do → show "No changes" toast on profile for 2s, then return to last page
        return redirect(url_for("profile", nochange=1, next=next_url))

    # --- if we reach here, at least one field changed ---
    new_img = None
    if avatar_file and avatar_file.filename:
        new_img = save_profile_image(avatar_file)

    try:
        cur = conn.cursor()
        if new_img:
            cur.execute("UPDATE users SET name=%s, bio=%s, image=%s WHERE userID=%s",
                        (name, bio, new_img, uid))
        else:
            cur.execute("UPDATE users SET name=%s, bio=%s WHERE userID=%s",
                        (name, bio, uid))
        conn.commit()
    except Exception as e:
        conn.rollback()
        err = str(e)
        return redirect(url_for("profile", error=1, msg=err, next=next_url))
    finally:
        cur.close(); conn.close()

    # success → show toast on profile for 2s, then return to last page
    return redirect(url_for("profile", updated=1, next=next_url))


# (YY)
# ---------- Auth ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    remembered_email = request.cookies.get("remembered_email")  # Get cookie if exists

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        remember = request.form.get("remember")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            # Replace this if you store plain text passwords (not recommended)
            # if password == user["password"]:
            if password == user["password"]:  # or use check_password_hash(user["password"], password)
                # Check if suspended
                if user["usertype"].lower() == "suspended":
                    flash("Your account has been suspended. Please contact support.")
                    return redirect(url_for("login"))

                # ✅ Mark user as logged in and update last active time
                cursor.execute("""
                    UPDATE users
                    SET is_logged_in = TRUE, last_active = NOW()
                    WHERE userID = %s
                """, (user["userID"],))

                # ✅ Record login activity (optional but useful)
                cursor.execute("""
                    INSERT INTO login_activity (userID, email, login_time, ip_address)
                    VALUES (%s, %s, NOW(), %s)
                """, (user["userID"], user["email"], request.remote_addr))

                conn.commit()

                # ✅ Set session data
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
                resp = make_response(redirect(url_for(redirect_route) if redirect_route else url_for("login")))

                # ✅ Handle "Remember Me" cookie
                if remember:
                    resp.set_cookie("remembered_email", email, max_age=30 * 24 * 60 * 60)
                else:
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

    # On GET, render login page with remembered email if any
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
    # Update database to mark user inactive before clearing session
    if "userID" in session:
        user_id = session["userID"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET is_logged_in = FALSE, last_active = NOW()
            WHERE userID = %s
        """, (user_id,))
        conn.commit()
        cursor.close()
        conn.close()

    # Destroy session and clear cookie
    session.clear()
    resp = redirect(url_for("login"))
    resp.delete_cookie("session")  # remove Flask session cookie
    flash("You have been logged out successfully.")
    return resp

@app.before_request
def update_last_active():
    if "userID" in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET last_active = NOW()
            WHERE userID = %s
        """, (session["userID"],))
        conn.commit()
        cursor.close()
        conn.close()

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

@app.route("/articleSubmission")
@login_required("Admin")
def article_submission():
    # Ensure only Admins can access
    if "userID" not in session or session.get("usertype") != "Admin":
        flash("Access denied.")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch only articles created by valid users (exclude system/orphan articles)
    cursor.execute("""
    SELECT 
        a.articleID,
        a.title,
        a.content,
        a.author,
        a.published_at,
        a.updated_at,
        a.image,
        a.catID,
        a.draft
    FROM articles a
    INNER JOIN users u ON a.author = u.name
    WHERE u.usertype IN ('Author', 'Subscriber')
    ORDER BY a.published_at DESC
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

    cursor.execute("""
        SELECT 
            userID, 
            email,
            is_logged_in,
            last_active
        FROM users
        ORDER BY last_active DESC
    """)
    users = cursor.fetchall()

    # Calculate "x hours ago"
    now = datetime.now()
    for user in users:
        if user["last_active"]:
            diff = now - user["last_active"]
            seconds = diff.total_seconds()
            if seconds < 60:
                user["last_seen"] = "Just Now"
            elif seconds < 3600:
                user["last_seen"] = f"{int(seconds // 60)} min ago"
            elif seconds < 86400:
                user["last_seen"] = f"{int(seconds // 3600)} hrs ago"
            else:
                user["last_seen"] = f"{int(seconds // 86400)} days ago"
        else:
            user["last_seen"] = "N/A"

    cursor.close()
    conn.close()

    return render_template("loginActivity.html", users=users)

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

# ---------- Multilingual SUpport ----------
translated = GoogleTranslator(source="auto", target="de").translate
@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    title = data.get("title", "")
    content = data.get("content", "")
    summary = data.get("summary", [])
    target_lang = data.get("target_lang", "en")

    if target_lang == "en":
        return jsonify({
            "title": title,
            "content": content,
            "summary": summary
        })

    try:
        translate_title = GoogleTranslator(source="auto", target=target_lang).translate(title) if title else ""
        translated_content = GoogleTranslator(source="auto", target=target_lang).translate(content)
        
        # traslate in single api call
        if summary:
            full_summary = "\n".join(summary)
            translated_full_summary = GoogleTranslator(source="auto", target=target_lang).translate(full_summary)
            translated_summary = translated_full_summary.split("\n")
        else:
            translated_summary = []

        return jsonify({
            "title": translate_title,
            "content": translated_content,
            "summary": translated_summary
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Dev helper ----------
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True)
