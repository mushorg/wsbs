import sqlite3

from datetime import datetime


class SandboxBotnet(object):
    sandbox_id = None
    file_name = ''
    file_md5 = ''
    irc_addr = ''
    irc_server_pwd = ''
    irc_nick = ''
    irc_user = ''
    irc_mode = ''
    irc_channel = ''
    irc_nickserv = ''
    irc_topic = ''
    irc_notice = []
    irc_privmsg = []
    first_analysis = ''
    last_analysis = ''


class Botnet(SandboxBotnet):
    botnet_id = None
    server_status = None
    channel_status = None
    bot_status = None


class SandboxDB(object):

    def __init__(self):
        self.db = sqlite3.connect('db/sandbox.db')

    def get_credentials(self):
        botnet_list = []
        cursor = self.db.cursor()
        list_in_sandbox = cursor.execute("SELECT * FROM botnets").fetchall()
        print "Found %s botnet in sandbox.db" % len(list_in_sandbox)
        for res in list_in_sandbox:
            botnet = SandboxBotnet()
            botnet.sandbox_id, botnet.file_md5, botnet.file_name, botnet.irc_addr = res[0:4]
            botnet.irc_server_pwd, botnet.irc_nick, botnet.irc_user = res[4:7]
            botnet.irc_mode, botnet.irc_channel, botnet.irc_nickserv = res[7:10]
            botnet.irc_notice, botnet.irc_privmsg, botnet.first_analysis = res[10:13]
            botnet.last_analysis = res[13]
            botnet_list.append(botnet)
        return botnet_list

    def close(self):
        self.db.close()


class BotnetInfoDB():

    def __init__(self):
        self.create()

    def connect(self):
        try:
            self.conn = sqlite3.connect('db/botnet_info.db')
        except sqlite3.OperationalError, e:
            print "Database connection error:", e
        except sqlite3.ProgrammingError, e:
            print "Database connection error:", e

    def create(self):
        conn = sqlite3.connect('db/botnet_info.db')
        cursor = conn.cursor()
        try:
            cursor.execute("""CREATE TABLE IF NOT EXISTS botnet_info (
                            id INTEGER PRIMARY KEY,
                            addr TEXT,
                            server_pass TEXT,
                            nick TEXT,
                            user TEXT,
                            mode TEXT,
                            channel TEXT,
                            sandboxid INTEGER,
                            lasttime TEXT,
                            topic TEXT,
                            server_status TEXT,
                            channel_status TEXT,
                            bot_status TEXT,
                            server_type TEXT)""")
        except sqlite3.OperationalError, e:
            print "Creating database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Creating database Error:", e
        else:
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def insert(self, botnet):
        cursor = self.conn.cursor()
        botnet_id = None
        try:
            # If C&C server and port exists, insert into db
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if botnet.irc_addr:
                cursor.execute("""INSERT INTO botnet_info VALUES(?, ?, ?, ?, ?,
                                    ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                               (None, botnet.irc_addr, botnet.irc_server_pwd,
                                botnet.irc_nick, botnet.irc_user,
                                ', '.join(botnet.irc_mode),
                                ', '.join(botnet.irc_channel),
                                botnet.sandbox_id, timestamp, None, None,
                                None, None, None))
        except sqlite3.OperationalError, e:
            print "Insert into database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Insert into database Error:", e
        else:
            botnet_id = cursor.lastrowid
            self.conn.commit()
        finally:
            cursor.close()
        return botnet_id

    def select_all(self):
        conn = sqlite3.connect('db/botnet_info.db')
        cursor = conn.cursor()
        botnet_list = []
        try:
            data = cursor.execute("SELECT * FROM botnet_info").fetchall()
            for res in data:
                botnet = Botnet()
                botnet.botnet_id = res[0]
                botnet.irc_addr = res[1]
                botnet.irc_server_pwd = res[2]
                botnet.irc_nick = res[3]
                botnet.irc_user = res[4]
                botnet.irc_mode = res[5]
                botnet.irc_channel = res[6]
                botnet.irc_topic = res[7]
                botnet.server_status = res[8]
                botnet.channel_status = res[9]
                botnet.bot_status = res[10]
                botnet_list.append(botnet)
        except sqlite3.OperationalError, e:
            print "Select from database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Select from database Error:", e
        finally:
            cursor.close()
            conn.close()
        return botnet_list

    def select_by_features(self, addr, channel):
        conn = sqlite3.connect('db/botnet_info.db')
        cursor = conn.cursor()
        data = None
        try:
            data = cursor.execute("SELECT id FROM botnet_info WHERE addr == ? AND channel == ?",
                                  (addr, channel)).fetchone()
        except sqlite3.OperationalError, e:
            print "Select from database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Select from database Error:", e
        finally:
            cursor.close()
            conn.close()
        return data

    def update_time(self, timestamp, botnetID):
        conn = sqlite3.connect('db/botnet_info.db')
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE botnet_info SET lasttime = '%s' WHERE id == '%s'""" % (timestamp, str(botnetID)))
        except sqlite3.OperationalError, e:
            print "Update Time To database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Update Time To database Error:", e
        finally:
            conn.commit()
            cursor.close()
            conn.close()

    def update_connection(self):
        pass

    def update_status(self, botnetID, target, status):
        conn = sqlite3.connect('db/botnet_info.db')
        cursor = conn.cursor()
        try:
            sql_query = """UPDATE botnet_info SET %s = ? WHERE id == ?""" % target
            cursor.execute(sql_query, (status, str(botnetID)))
        except sqlite3.OperationalError, e:
            print "Update %s To database Error:" % status, e
        except sqlite3.ProgrammingError, e:
            print "Update %s To database Error:" % status, e
        finally:
            conn.commit()
            cursor.close()
            conn.close()

    def update_topic(self, line, botnetID):
        conn = sqlite3.connect('db/botnet_info.db')
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE botnet_info SET topic = ? WHERE id == ? """,
                           (line, str(botnetID)))
        except sqlite3.OperationalError, e:
            print "Update Topic To database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Update Topic To database Error:", e
        finally:
            conn.commit()
            cursor.close()
            conn.close()

    def update_servertype(self, botnetID, servertype):
        conn = sqlite3.connect('db/botnet_info.db')
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE botnet_info SET server_type = ? WHERE id == ? """,
                           (servertype, str(botnetID)))
        except sqlite3.OperationalError, e:
            print "Update Topic To database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Update Topic To database Error:", e
        finally:
            conn.commit()
            cursor.close()
            conn.close()

    def close(self):
        self.conn.close()


class MessageDB():

    def __init__(self, botnetID):
        self.conn = sqlite3.connect('db/botnets/Botnet_%s.db' % str(botnetID))
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, timestamp TEXT, rawmsg TEXT)")
            self.conn.commit()
        except sqlite3.OperationalError, e:
            print "creating table error", e
        except sqlite3.ProgrammingError, e:
            print "creating table error", e
        finally:
            cursor.close()

    def insert(self, time, msg):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO messages VALUES(?, ?, ?)", (None, time, msg))
            self.conn.commit()
        except sqlite3.OperationalError, e:
            print "insert table error", e
        except sqlite3.ProgrammingError, e:
            print "insert table error", e
        finally:
            cursor.close()

    def show_all(self):
        cursor = self.conn.cursor()
        data = None
        try:
            data = cursor.execute("SELECT * FROM messages").fetchall()
        except sqlite3.OperationalError, e:
            print "select data from db Error", e
        except sqlite3.ProgrammingError, e:
            print "select data from db Error", e
        finally:
            cursor.close()
        return data

    def close_handle(self):
        self.conn.close()
