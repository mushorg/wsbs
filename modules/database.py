import sqlite3

class SandboxBotnet(object):
    sandbox_id = None
    file_name = ''
    file_md5 = ''
    analysis_date = ''
    irc_addr = ''
    irc_server_pwd = ''
    irc_nick = ''
    irc_user = ''
    irc_mode = ''
    irc_channel = ''
    irc_nickserv = ''
    irc_notice = []
    irc_privmsg = []
    
class Botnet(SandboxBotnet):
    botnet_id = None

class SandboxDB(object):
    
    def __init__(self):
        self.db = sqlite3.connect('db/sandbox.db')
    
    def get_credentials(self):
        botnet_list = []
        cursor = self.db.cursor()
        cursor.execute("""SELECT * FROM botnets""")
        for res in cursor.fetchall():
            botnet = SandboxBotnet()
            botnet.sandbox_id, botnet.analysis_date, botnet.file_md5, botnet.file_name = res[0:4]
            botnet.irc_addr, botnet.irc_server_pwd, botnet.irc_nick = res[4:7]
            botnet.irc_user, botnet.irc_mode, botnet.irc_channel = res[7:10]
            botnet.irc_nickserv, botnet.irc_notice, botnet.irc_privmsg = res[10:]
            botnet_list.append(botnet)
        return botnet_list
    
    def close(self):
        self.db.close()

class BotnetInfoDB():

    def __init__(self):
        self.conn = sqlite3.connect('db/botnet_info_msg.db', check_same_thread = False)
        self.create()

    def create(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""CREATE TABLE IF NOT EXISTS botnet_info (id INTEGER PRIMARY KEY, 
            addr TEXT, server_pass TEXT, nick TEXT, user TEXT, channel TEXT, sandboxid TEXT, lasttime TEXT, topic TEXT)""")
            self.conn.commit()
        except sqlite3.OperationalError, e:
            print "Creating database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Creating database Error:", e
        finally:
            cursor.close()

    def insert(self, addr, server_pass, nick, user, channel, sandboxid, time):
        cursor = self.conn.cursor()
        try:
            if addr: #if C&C server and port exists, insert into db
                cursor.execute("INSERT INTO botnet_info VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (None, addr, server_pass, nick, user, channel, sandboxid, time, "None"))
        except sqlite3.OperationalError, e:
            print "Insert into database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Insert into database Error:", e
        finally:
            self.conn.commit()
            cursor.close()

    def select_all(self):
        cursor = self.conn.cursor()
        botnet_list = []
        try:
            data = cursor.execute("SELECT * FROM botnet_info").fetchall()
            for res in data:
                print res
                botnet = Botnet()
                botnet.botnet_id = res[0]
                botnet.irc_addr = res[1]
                botnet.irc_server_pwd = res[2]
                botnet.irc_nick = res[3]
                botnet.irc_user = res[4]
                botnet.irc_channel = res[5]
                botnet_list.append(botnet)
        except sqlite3.OperationalError, e:
            print "Select from database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Select from database Error:", e
        finally:
            cursor.close()
        return botnet_list

    def select_by_features(self, addr, channel):
        cursor = self.conn.cursor()
        data = None
        try:
            data = cursor.execute("SELECT id FROM botnet_info WHERE addr == ? AND channel == ?", (addr, channel) ).fetchone()
        except sqlite3.OperationalError, e:
            print "Select from database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Select from database Error:", e
        finally:
            cursor.close()
        return data

    def update_time(self, timestamp, botnetID):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""UPDATE botnet_info SET lasttime = '%s' WHERE id == '%s'""" % (timestamp, str(botnetID)))
            self.conn.commit()
        except sqlite3.OperationalError, e:
            print "Update Time To database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Update Time To database Error:", e
        finally:
            cursor.close()

    def update_connection(self):
        pass

    def update_status(self):
        pass

    def update_topic(self, line, botnetID):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""UPDATE botnet_info SET topic='%s' WHERE id == '%s' """ %(line, str(botnetID)))
        except sqlite3.OperationalError, e:
            print "Update Topic To database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Update Topic To database Error:", e
        finally:
            cursor.close() 

    def close_handle(self):
        self.conn.close()

class MessageDB():

    def __init__(self):
        self.conn = sqlite3.connect('db/botnet_info_msg.db', check_same_thread = False)
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
        finally:
            cursor.close()

    def insert(self, botnetID, time, msg): # The botnetID should be int
        cursor = self.conn.cursor()
        tablename = self.prefix + str(botnetID)
        sql = "INSERT INTO %s VALUES(?, ?, ?)" % tablename
        try:
            cursor.execute(sql, (None, time, msg))
            self.conn.commit()
        except sqlite3.OperationalError, e:
            print "insert table error", e
        except sqlite3.ProgrammingError, e:
            print "insert table error", e
        finally:
            cursor.close()

    def showall(self, botnetID): # The botnetID should be int
        cursor = self.conn.cursor()
        tablename = self.prefix + str(botnetID)
        data = None
        sql = "SELECT * FROM %s" % tablename
        try:
            data = cursor.execute(sql).fetchall()
        except sqlite3.OperationalError, e:
            print "select data from db Error", e
        except sqlite3.ProgrammingError, e:
            print "select data from db Error", e
        finally:
            cursor.close()
        return data

    def close_handle(self):
        self.conn.close()

