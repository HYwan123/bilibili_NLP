    def test(self):
        try:
            self.cursor.execute('SELECT * FROM test')
            rows = self.cursor.fetchall()
            for row in rows:
                print(row)
        except Exception as e:
            print("查询失败:", e)
