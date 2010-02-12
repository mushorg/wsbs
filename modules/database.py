'''
Created on 29.01.2010

@author: Lukas
'''

import sqlite3

def create():
    db = sqlite3.connect('db/sqlite.db')
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS CnC(id integer primary key, host text, port integer, channel text, nick text, user text, names text)")
    db.commit()
    db.close()

def insert(HOST, PORT, CHAN, NICK, USER):
    NAMES = ""
    CHAN_string = ""
    for channel in CHAN:
        CHAN_string += channel + ","
    CHAN = CHAN_string
    print "insert: " + CHAN 
    db = sqlite3.connect('db/sqlite.db')
    cursor = db.cursor()
    sql1 = "SELECT id FROM CnC WHERE host = ? AND channel LIKE ?"
    cursor.execute(sql1, (HOST,CHAN))
    if len(cursor.fetchall()) > 0:
        print "Already in database"
    else:
        sql2 = "INSERT INTO CnC values(NULL, ?, ?, ?, ?, ?, ?)"
        cursor.execute(sql2, (HOST, PORT, CHAN, NICK, USER, NAMES))
    db.commit()
    db.close()
    
def select_servers():
    CnC_SERVERS = []
    db = sqlite3.connect('db/sqlite.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM CnC")
    for server in cursor:
        CnC_SERVERS.append(server)
    db.close()
    return CnC_SERVERS

def insert_names(ID, new_names):
    NAMES = ""
    db = sqlite3.connect('db/sqlite.db')
    cursor = db.cursor()
    sql1 = "SELECT names FROM CnC WHERE id = ?"
    cursor.execute(sql1, (ID,))
    db_names = cursor.fetchall()[0][0]
    if  db_names == "":
        for name in new_names:
            NAMES += name + "," 
    else:
        NAMES = db_names
        splitted_db_names = db_names.split(",")
        for name in new_names:
            if name not in splitted_db_names:
                NAMES += name + ","
    sql2 = "UPDATE CnC SET names = ? WHERE id = ?"
    cursor.execute(sql2, (NAMES,ID,))
    db.commit()
    db.close()
    show()


def show():
    db = sqlite3.connect('../db/sqlite.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM CnC")
    for row in cursor:
        print row
    db.commit()
    db.close()

show()