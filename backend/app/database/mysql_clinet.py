import mysql.connector
import logging


logger = logging.getLogger(__name__)

class MysqlClient():
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    

    def __init__(self):
        self.conn = mysql.connector.connect(
            host = '127.0.0.1',
            user = 'wan',
            password = 'Qqwe123123',
            database = 'bilibili_NLP',
        )
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def close(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()


    def test(self):
        self.cursor.execute('SELECT * FROM test')
        rows = self.cursor.fetchall()
        print(1)
        for row in rows:
            print(row)




