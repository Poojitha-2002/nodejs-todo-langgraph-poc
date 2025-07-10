import sqlite3
from datetime import datetime, timedelta

DB_FILE = "auth_tokens.db"


def init_db():
    """Initialize the SQLite database and create the auth_tokens table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_tokens (
            app TEXT,
            username TEXT,
            token TEXT,
            expires_at TEXT,
            PRIMARY KEY (app, username)
        )
    """
    )
    conn.commit()
    conn.close()


def save_token(app: str, username: str, token: str, ttl_minutes: int = 30):
    """Save or update a token with an expiration time."""
    expires_at = (datetime.now() + timedelta(minutes=ttl_minutes)).isoformat()
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "REPLACE INTO auth_tokens (app, username, token, expires_at) VALUES (?, ?, ?, ?)",
        (app, username, token, expires_at),
    )
    conn.commit()
    conn.close()


def get_token(app: str, username: str) -> str | None:
    """Retrieve a valid token if it exists and is not expired."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT token, expires_at FROM auth_tokens WHERE app = ? AND username = ?",
        (app, username),
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        token, expires_at = row
        if datetime.fromisoformat(expires_at) > datetime.now():
            return token
    return None


def delete_token(app: str, username: str):
    """Delete a stored token, e.g., if it's expired or invalid."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "DELETE FROM auth_tokens WHERE app = ? AND username = ?", (app, username)
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()

    # Simulate storing a token
    save_token("demo_app", "test_user", "xyz123token", ttl_minutes=1)

    # Retrieve token
    token = get_token("demo_app", "test_user")
    print("Retrieved token:", token)

    # Optional: Delete it
    # delete_token("demo_app", "test_user")
