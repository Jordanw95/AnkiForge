import sqlite3
from google.cloud import translate_v2 as translate
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/jordanwaters/Desktop/Python/Anki/KindleToAnki/KindleToAnki/My First Project-631ac9d558c9.json"



class Datastore : 

    def __init__(self): 
        self.conn = sqlite3.connect('/Users/jordanwaters/Desktop/TerminalScripts/BrowserWords1')
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS newwords (english TEXT, spanish TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS backup (english TEXT, spanish TEXT)")
        self.conn.commit()
    
    def add_entry(self, english, spanish) : 
        self.cur.execute("INSERT INTO newwords VALUES (?, ?)", (english, spanish))
        self.conn.commit()
    
    def view_all(self):
        self.cur.execute('''SELECT count(name) FROM sqlite_master WHERE type ='table' AND name ='newwords' ''')
        if self.cur.fetchone()[0] : 
            self.cur.execute("SELECT * FROM newwords")
            rows = self.cur.fetchall()
            print(rows)
            return rows
        else :
            return []

    def view_all_backup(self) : 
        self.cur.execute("SELECT * FROM backup")
        rows = self.cur.fetchall()
        return rows

    def delete_table(self) : 
        self.cur.execute("INSERT INTO backup SELECT * FROM newwords")
        self.cur.execute("DROP TABLE newwords")
        self.conn.commit()

    def __del__ (self) : 
        self.conn.commit()
        self.conn.close()


class Translation : 

    def __init__(self) : 
        self.translate_client = translate.Client()

    def detect (self, text) : 
        lang = self.translate_client.detect_language(text)
        return lang['language']

    def translate(self, text) :
        lang = self.detect(text) 
        if lang == 'es' :
            dest_lang = "en"
        else :
            dest_lang = 'es'
        translation = self.translate_client.translate(text, target_language = f"{dest_lang}")
        if lang == 'es': 
            return [translation['input'], translation['translatedText']]
        else : 
            return [translation['translatedText'], translation['input']]



class Controller1 : 

    def __init__(self, text) : 
        self.text = self.clean_text(text)
        self.T = Translation()
        self.translations = self.T.translate(self.text)
        self.D = Datastore()
        self.D.add_entry(self.translations[0], self.translations[1])
        self.D.view_all()

    def clean_text(self, text):
        # Not sure if this works, should remove problems with pasted text from internet
        text = text.replace('\n', '')
        text = text.replace('\t', '')
        text = "".join([x for x in text if x not in [",","«","»",":"]])
        return text