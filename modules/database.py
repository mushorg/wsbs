import sqlite3
import types

class MySQLDB():
    
    def __init__(self):
        pass
    
    def create(self):
        self.db = sqlite3.connect('db/sqlite.db')
        self.cursor = self.db.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS CnC(id integer primary key, host text, port integer, channel text, nick text, user text, names text, filename text)")
        self.close_db()
        
    def check_existence(self, FILENAME):
        self.db = sqlite3.connect('db/sqlite.db')
        self.cursor = self.db.cursor()
        sql1 = "SELECT id FROM CnC WHERE filename = ?"
        self.cursor.execute(sql1, (FILENAME,))
        if len(self.cursor.fetchall()) > 0:
            return True
        else:
            return False
        self.close_db()
    
    def insert(self, HOST, PORT, CHAN, NICK, USER, NAMES, FILENAME):
        self.db = sqlite3.connect('db/sqlite.db')
        self.cursor = self.db.cursor()
        CHAN_string = ""
        for channel in CHAN:
            CHAN_string += channel + ","
        CHAN = CHAN_string
        USER = USER.encode('utf-8')
        if len(NAMES) > 1:
            NAMES_string = ""
            for name in NAMES:
                NAMES_string += name + ","
            NAMES = NAMES_string
        else:
            NAMES = ""
        sql1 = "SELECT id, names FROM CnC WHERE host = ? AND channel LIKE ?"
        self.cursor.execute(sql1, (HOST,CHAN))
        if len(self.cursor.fetchall()) > 0:
            print "Already in database"
            if NAMES != "":
                NAMES_old = self.cursor.fetchone()[1].split(",")
                NAMES_new = NAMES.split(",")
                NAMES = NAMES_old
                print "Old names: ", NAMES
                for name in NAMES_new:
                    if name not in NAMES_old:
                        NAMES.append(name)
                NAMES_string = ""
                for name in NAMES:
                    NAMES_string += name + ","
                NAMES = NAMES_string
                print "New names: ", NAMES
                ID = self.cursor.fetchone()[0]
                print "ID = ", ID
                sql2 = "UPDATE CnC SET names = ? WHERE id = ?"
                self.cursor.execute(sql2, (NAMES,ID))
        else:
            sql3 = "INSERT INTO CnC values(NULL, ?, ?, ?, ?, ?, ?, ?)"
            self.cursor.execute(sql3, (HOST, PORT, CHAN, NICK, USER, NAMES, FILENAME))
        self.close_db()
    
    def show(self):
        self.db = sqlite3.connect('db/sqlite.db')
        self.cursor = self.db.cursor()
        self.cursor.execute("SELECT * FROM CnC")
        for row in self.cursor:
            print row
        self.close_db()
        
    def close_db(self):
        self.db.commit()
        self.db.close()
        
mysql_database = MySQLDB()
mysql_database.show()