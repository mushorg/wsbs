import sqlite3

class MySQLDB():
    
    def __init__(self):
        pass
    
    def create(self):
        db = sqlite3.connect('db/sqlite.db')
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS CnC(id integer primary key, host text, port integer, channel text, nick text, user text, names text, filename text)")
        db.commit()
        db.close()
        
    def check_existence(self, FILENAME):
        db = sqlite3.connect('db/sqlite.db')
        cursor = db.cursor()
        sql1 = "SELECT id FROM CnC WHERE filename = ?"
        cursor.execute(sql1, (FILENAME,))
        if len(cursor.fetchall()) > 0:
            return True
        else:
            return False
        db.commit()
        db.close()
    
    def insert(self, HOST, PORT, CHAN, NICK, USER, NAMES, FILENAME):
        db = sqlite3.connect('db/sqlite.db')
        cursor = db.cursor()
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
        cursor.execute(sql1, (HOST,CHAN))
        found_entries = cursor.fetchall()
        if len(found_entries) > 0:
            print "Already in database"
            if NAMES != "":
                NAMES_new = NAMES.split(",")
                if found_entries[0][1] != "":
                    NAMES_old = found_entries[0][1].split(",")
                    NAMES = NAMES_old
                else:
                    NAMES = []
                    NAMES_old = []
                for name in NAMES_new:
                    if name not in NAMES_old and name != "":
                        NAMES.append(name)
                NAMES_string = ""
                for name in NAMES:
                    NAMES_string += name + ","
                NAMES = NAMES_string
                ID = found_entries[0][0]
                sql2 = "UPDATE CnC SET names = ? WHERE id = ?"
                cursor.execute(sql2, (NAMES,ID))
        else:
            sql3 = "INSERT INTO CnC values(NULL, ?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(sql3, (HOST, PORT, CHAN, NICK, USER, NAMES, FILENAME))
        db.commit()
        db.close()
    
    def show(self):
        db = sqlite3.connect('db/sqlite.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM CnC")
        for row in cursor:
            print row
        db.commit()
        db.close()