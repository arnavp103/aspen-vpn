import sqlite3

class DBManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def execute(self, query, params):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch(self, query, params):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def __del__(self):
        self.conn.close()