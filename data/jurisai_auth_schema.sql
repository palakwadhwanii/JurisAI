CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    full_name TEXT,
                    created_at TEXT NOT NULL
                );
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE user_tokens (
                    token TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
CREATE TABLE search_history (
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
CREATE INDEX idx_history_user_id ON search_history(user_id, created_at DESC);
CREATE INDEX idx_tokens_token ON user_tokens(token);
