import sqlite3
import datetime


class StateDB:
    def __init__(self, path: str):
        self.path = path
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self._init_schema()

    def _init_schema(self):
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS change_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT, action TEXT, payload TEXT
            )"""
        )
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS user_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT, cluster_id TEXT, decision TEXT, details TEXT
            )"""
        )
        self.conn.commit()

    @staticmethod
    def _now() -> str:
        return datetime.datetime.utcnow().isoformat(timespec="seconds")

    def log_action(self, action: str, payload: str):
        self.conn.execute(
            "INSERT INTO change_history (ts, action, payload) VALUES (?,?,?)",
            (self._now(), action, payload),
        )
        self.conn.commit()

    def log_user_decision(self, cluster_id: str, decision: str, details: str):
        self.conn.execute(
            "INSERT INTO user_actions (ts, cluster_id, decision, details) VALUES (?,?,?,?)",
            (self._now(), cluster_id, decision, details),
        )
        self.conn.commit()

    def get_history(self, limit: int = 200):
        cur = self.conn.execute(
            "SELECT ts, action, payload FROM change_history ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return [{"ts": r[0], "action": r[1], "payload": r[2]} for r in cur.fetchall()]

    def get_user_actions(self, limit: int = 200):
        cur = self.conn.execute(
            "SELECT ts, cluster_id, decision, details FROM user_actions ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return [
            {"ts": r[0], "cluster_id": r[1], "decision": r[2], "details": r[3]}
            for r in cur.fetchall()
        ]