import sqlite3

class Botnet(object):
    
    def __init__(self):
        self.sandbox_id = None
        self.file_name = ''
        self.file_md5 = ''
        self.analysis_date = ''
        self.irc_addr = ''
        self.irc_server_pwd = ''
        self.irc_nick = ''
        self.irc_user = ''
        self.irc_mode = ''
        self.irc_channel = ''
        self.irc_nickserv = ''
        self.irc_notice = []
        self.irc_privmsg = []

class SandboxDB(object):
    
    def __init__(self):
        self.db = sqlite3.connect('db/sandbox.db')
    
    def get_credentials(self):
        botnet_list = []
        cursor = self.db.cursor()
        cursor.execute("""SELECT * FROM botnets""")
        for res in cursor.fetchall():
            botnet = Botnet()
            botnet.sandbox_id, botnet.analysis_date, botnet.file_md5, botnet.file_name = res[0:4]
            botnet.irc_addr, botnet.irc_server_pwd, botnet.irc_nick = res[4:7]
            botnet.irc_user, botnet.irc_mode, botnet.irc_channel = res[7:10]
            botnet.irc_nickserv, botnet.irc_notice, botnet.irc_privmsg = res[10:]
            botnet_list.append(botnet)
        return botnet_list
    
    def close(self):
        self.db.close()

class MessageDB():

    def __init__(self):
        self.conn = sqlite3.connect('db/botnet_info_msg.db')
        self.prefix = u"Botnet_"

    def createtable(self, botnetID): # The botnetID should be int
        tablename = self.prefix + str(botnetID)
        cursor = self.conn.cursor()
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS %s (id INTEGER PRIMARY KEY, timestamp TEXT, rawmsg TEXT)" % tablename)
            self.conn.commit()
        except sqlite3.OperationalError, e:
            print "creating table error", e
        except sqlite3.ProgrammingError, e:
            print "creating table error", e
        cursor.close()

    def insert(self, botnetID, time, msg): # The botnetID should be int
        cursor = self.conn.cursor()
        tablename = self.prefix + str(botnetID)
        sql = "INSERT INTO %s VALUES(?, ?, ?)" % tablename
        try:
            cursor.execute(sql, (None, time, msg))
            self.conn.commit()
        except sqlite3.OperationalError, e:
            print "creating table error", e
        except sqlite3.ProgrammingError, e:
            print "creating table error", e
        cursor.close()

    def showall(self, botnetID): # The botnetID should be int
        cursor = self.conn.cursor()
        tablename = self.prefix + str(botnetID)
        sql = "SELECT * FROM %s" % tablename
        reply = []
        try:
            data = cursor.execute(sql).fetchall()
            cursor.close()
            return data
        except sqlite3.OperationalError, e:
            print "Selecting data from db Error", e
        except sqlite3.ProgrammingError, e:
            print "Selecting data from db Error", e

    def closehandle(self):
        self.conn.commit()
        self.conn.close()

class BotnetInfoDB():

    def __init__(self):
        self.conn = sqlite3.connect('db/botnet_info_msg.db')
        self.create()

    def create(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS botnet_info (id INTEGER PRIMARY KEY, serverinfo TEXT, channel TEXT, sandboxid TEXT, lasttime TEXT)")
            self.conn.commit()
        except sqlite3.OperationalError, e:
            print "Creating database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Creating database Error:", e
        cursor.close()

    def insert(self, serverinfo, channel, sandboxid, time):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO botnet_info VALUES(?, ?, ?, ?, ?)", (None, serverinfo, channel, sandboxid, time))
        except sqlite3.OperationalError, e:
            print "Insert into database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Insert into database Error:", e
        self.conn.commit()
        cursor.close()

    def selectbyid(self, sandboxid):
        cursor = self.conn.cursor()
        try:
            reply = cursor.execute("SELECT * FROM botnet_info WHERE sandboxid == ? ORDER BY id", (sandboxid,)).fetchone()
            cursor.close()
            return reply
        except sqlite3.OperationalError, e:
            print "Select from database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Select from database Error:", e

    def closehandle(self):
        self.conn.commit()
        self.conn.close()

