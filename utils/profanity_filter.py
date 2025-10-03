import re
import mysql.connector

def load_blocked_words():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="nrs"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM blocked_words")
    words = [row[0] for row in cursor.fetchall()]
    conn.close()
    return words

def contains_profanity(text: str) -> bool:
    blocked_words = load_blocked_words()
    if not blocked_words:
        return False
    pattern = r"\b(" + "|".join(re.escape(word) for word in blocked_words) + r")\b"
    return bool(re.search(pattern, text, flags=re.IGNORECASE))

def censor_text(text: str) -> str:
    blocked_words = load_blocked_words()
    if not blocked_words:
        return text
    pattern = r"\b(" + "|".join(re.escape(word) for word in blocked_words) + r")\b"
    return re.sub(pattern, "***", text, flags=re.IGNORECASE)
