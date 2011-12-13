import sqlite3
import re

class BotTrack():
    def __init__(self):
        self.conn = sqlite3.connect('../db/botip.db')
        self.create_BotIP()
        self.create_privmsg()

    def create_BotIP(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""CREATE TABLE IF NOT EXISTS Bot_IP_Track (id INTEGER PRIMARY KEY, 
            timestamp TEXT, botnet_id INTERGER, botspy TEXT, nickname TEXT, username TEXT, hostname TEXT, 
            realname TEXT, geoip_addr TEXT, geoip_name)""")
            self.conn.commit()
        except sqlite3.OperationalError, e:
            print "Creating database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Creating database Error:", e
        finally:
            cursor.close()
            
    def create_privmsg(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""CREATE TABLE IF NOT EXISTS Bot_PRIVMSG (id INTEGER PRIMARY KEY, 
            timestamp TEXT, botnet_id INTERGER, channel TEXT, msgtype TEXT, info TEXT)""")
            self.conn.commit()
        except sqlite3.OperationalError, e:
            print "Creating database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Creating database Error:", e
        finally:
            cursor.close()
            
    def insert_privmsg(self, timestamp, botnet_id, channel, msgtype, info):
        cursor = self.conn.cursor()
        try:
            # If C&C server and port exists, insert into db
            cursor.execute("INSERT INTO Bot_PRIVMSG VALUES(?, ?, ?, ?, ?, ?)", (None, timestamp, botnet_id, channel, msgtype, info))
        except sqlite3.OperationalError, e:
            print "Insert into database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Insert into database Error:", e
        finally:
            self.conn.commit()
            cursor.close()
            
    def insert_BotIP(self, timestamp, botnet_id, botspy, nickname, username, hostname, realname, geoip_addr, geoip_name):
        cursor = self.conn.cursor()
        try:
            # If C&C server and port exists, insert into db
            cursor.execute("INSERT INTO Bot_IP_Track VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (None, timestamp, botnet_id, botspy, nickname, username, hostname, realname, geoip_addr, geoip_name))
        except sqlite3.OperationalError, e:
            print "Insert into database Error:", e
        except sqlite3.ProgrammingError, e:
            print "Insert into database Error:", e
        finally:
            self.conn.commit()
            cursor.close()


class BotnetAnalysis():
    def __init__(self):
        self.dbname = "botnet_info_msg.db"
        self.cc = sqlite3.connect(self.dbname).cursor()

    def parse_msg(self, msg):
        prefix = ''
        trailing = []
        try:
            if msg[0] == ':' :
                prefix, msg = msg[1:].split(' ', 1)
            
            if msg.find(' :') != -1:
                msg, trailing = msg.split(' :', 1)
                args = msg.split()
                args.append(trailing)
            else:
                args = msg.split()
            
            command = args.pop(0)
            return prefix, command, args    
    
        except IndexError as e:
            return 0
        
    def PRIVMSG_dork(self, msg):
        for item in msg:
            m = re.search(r'((ftp)|(http)|(https)).*$', item)
            if m:
                channel = msg[0]
                command = str(msg[1].split(":")[:1]).replace("[", "").replace("]", "").replace("\'", "")
                dork_url = m.group(0)
                return channel, command, dork_url
    
    def Botnet_Server_Type(self, msg):
        '''IRC Response Code = 004 --> Get IRCServer Name and  ServeVersion'''
        server_version = msg[2]
        return server_version
    
                  
            
                  
        
        
        
            #if parsed_msg[1] == "311":
                #print type(parsed_msg[1])
             #   print "IP:", parsed_msg      
