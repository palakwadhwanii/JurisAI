import sqlite3
import hashlib
import secrets
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = Path(BASE_DIR) / "data" / "jurisai_auth.db"

class AuthService:
    """
    Lightweight, embedded SQLite authentication and case history service.
    Features:
    - User registration and login with PBKDF2-HMAC-SHA256 password hashing
    - Cryptographically secure session tokens
    - User-linked search and legal analysis history storage with full case restoration
    """
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    full_name TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS user_tokens (
                    token TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    analysis_id TEXT,
                    query_text TEXT NOT NULL,
                    case_type TEXT,
                    outcome TEXT,
                    summary TEXT,
                    analysis_data_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_history_user_id ON search_history(user_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_tokens_token ON user_tokens(token);
            """)

    @staticmethod
    def _hash_password(password: str, salt: bytes = None) -> tuple[str, str]:
        if salt is None:
            salt = secrets.token_bytes(16)
        pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return pwd_hash.hex(), salt.hex()

    def register_user(self, username: str, email: str, password: str, full_name: Optional[str] = None) -> Dict[str, Any]:
        username = username.strip()
        email = email.strip().lower()
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        if "@" not in email or "." not in email:
            raise ValueError("Invalid email address format.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")

        pwd_hash, salt_hex = self._hash_password(password)
        now_iso = datetime.now(timezone.utc).isoformat()

        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO users (username, email, password_hash, salt, full_name, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (username, email, pwd_hash, salt_hex, full_name or username, now_iso)
                )
                user_id = cursor.lastrowid
        except sqlite3.IntegrityError as e:
            err_msg = str(e).lower()
            if "username" in err_msg:
                raise ValueError(f"Username '{username}' is already taken.")
            elif "email" in err_msg:
                raise ValueError(f"Email '{email}' is already registered.")
            raise ValueError("A user with these credentials already exists.")

        token = self.create_session_token(user_id)
        return {
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "full_name": full_name or username,
                "created_at": now_iso
            },
            "token": token
        }

    def authenticate_user(self, username_or_email: str, password: str) -> Dict[str, Any]:
        identifier = username_or_email.strip()
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT id, username, email, password_hash, salt, full_name, created_at
                FROM users
                WHERE username = ? OR email = ?
                """,
                (identifier, identifier.lower())
            ).fetchone()

        if not row:
            raise ValueError("Invalid username/email or password.")

        stored_hash = row["password_hash"]
        salt_bytes = bytes.fromhex(row["salt"])
        computed_hash, _ = self._hash_password(password, salt=salt_bytes)

        if not secrets.compare_digest(stored_hash, computed_hash):
            raise ValueError("Invalid username/email or password.")

        token = self.create_session_token(row["id"])
        return {
            "user": {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
                "full_name": row["full_name"],
                "created_at": row["created_at"]
            },
            "token": token
        }

    def create_session_token(self, user_id: int, days_valid: int = 30) -> str:
        token = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        expires_at = (now + timedelta(days=days_valid)).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO user_tokens (token, user_id, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (token, user_id, now.isoformat(), expires_at)
            )
        return token

    def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        if not token:
            return None
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT u.id, u.username, u.email, u.full_name, u.created_at
                FROM user_tokens t
                JOIN users u ON t.user_id = u.id
                WHERE t.token = ? AND t.expires_at > ?
                """,
                (token, now_iso)
            ).fetchone()

        if row:
            return {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
                "full_name": row["full_name"],
                "created_at": row["created_at"]
            }
        return None

    def revoke_token(self, token: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM user_tokens WHERE token = ?", (token,))
            return cursor.rowcount > 0

    def save_history(
        self,
        user_id: int,
        query_text: str,
        case_type: Optional[str] = None,
        outcome: Optional[str] = None,
        summary: Optional[str] = None,
        analysis_id: Optional[str] = None,
        analysis_data_json: Optional[str] = None
    ) -> int:
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO search_history (
                    user_id, analysis_id, query_text, case_type, outcome, summary, analysis_data_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    analysis_id,
                    query_text,
                    case_type or "Legal Case Analysis",
                    outcome or "PASS",
                    summary or query_text[:160],
                    analysis_data_json,
                    now_iso
                )
            )
            return cursor.lastrowid

    def get_user_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, analysis_id, query_text, case_type, outcome, summary, created_at
                FROM search_history
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit)
            ).fetchall()

        return [
            {
                "id": r["id"],
                "analysis_id": r["analysis_id"],
                "query_text": r["query_text"],
                "case_type": r["case_type"],
                "outcome": r["outcome"],
                "summary": r["summary"],
                "created_at": r["created_at"]
            }
            for r in rows
        ]

    def get_history_item(self, user_id: int, history_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT id, analysis_id, query_text, case_type, outcome, summary, analysis_data_json, created_at
                FROM search_history
                WHERE id = ? AND user_id = ?
                """,
                (history_id, user_id)
            ).fetchone()

        if not row:
            return None

        import json
        data = None
        if row["analysis_data_json"]:
            try:
                data = json.loads(row["analysis_data_json"])
            except Exception:
                pass

        return {
            "id": row["id"],
            "analysis_id": row["analysis_id"],
            "query_text": row["query_text"],
            "case_type": row["case_type"],
            "outcome": row["outcome"],
            "summary": row["summary"],
            "analysis_data": data,
            "created_at": row["created_at"]
        }

    def delete_history_item(self, user_id: int, history_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM search_history WHERE id = ? AND user_id = ?",
                (history_id, user_id)
            )
            return cursor.rowcount > 0

    def clear_user_history(self, user_id: int) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM search_history WHERE user_id = ?", (user_id,))
            return cursor.rowcount

# Singleton service instance
_auth_service = None

def get_auth_service() -> AuthService:
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service

