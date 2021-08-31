import sqlite3


class DbControl:
    def __init__(self):
        self.sqlite_con = None

    def open_database(self, table_path):
        try:
            self.sqlite_con = sqlite3.connect(f'file:{table_path}?mode=rw', uri=True)
            return True
        except sqlite3.OperationalError:
            self.sqlite_con = sqlite3.connect(table_path)
            cursor = self.sqlite_con.cursor()
            cursor.execute('''CREATE TABLE words (id PRIMARY KEY AUTOINCREMENT, word  STRING  NOT NULL UNIQUE, 
            count INTEGER NOT NULL DEFAULT (0) ); ''')
            cursor.execute('''CREATE UNIQUE INDEX idx_word ON words (word);''')
            cursor.execute('''CREATE TABLE sources (url STRING NOT NULL UNIQUE);''')
            cursor.execute('''CREATE UNIQUE INDEX idx_url ON sources (url);''')
            return True
        except Exception as e:
            print('!!! Open database error', e)
            return False

    def close_database(self):
        self.sqlite_con.close()

    def commit(self):
        self.sqlite_con.commit()

    def is_url_captured(self, url: str):
        cursor = self.sqlite_con.cursor()
        cursor.execute('SELECT * FROM sources WHERE url=?', (url,))
        return len(cursor.fetchall()) > 0

    def upsert_url(self, url: str, site: str):
        cursor = self.sqlite_con.cursor()
        cursor.execute('INSERT INTO sources(url, site) VALUES(?,?) ON CONFLICT(url) DO NOTHING', (url, site))

    def get_all_words(self):
        cursor = self.sqlite_con.cursor()
        cursor.execute('SELECT word, count FROM words')
        return dict(cursor.fetchall())

    def upsert_words(self, word: str, qty: int):
        cursor = self.sqlite_con.cursor()
        cursor.execute('INSERT INTO words(word, count) VALUES(?,?) ON CONFLICT(word) DO UPDATE SET count=?',
                       (word, qty, qty,))

    def get_cursor(self):
        return self.sqlite_con.cursor()
