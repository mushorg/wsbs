import socket
import time
import modules.database as database
import datetime

class Trojan_Horse():
    
    def log(self, id, msg):
        print "[irc_client] %s : %s" % (id, msg)
        
    def __init__(self, botnet):
        self.botnet_db = database.BotnetInfoDB()
        try:
            self.irc_host = botnet.irc_addr.split(':')[0]
            self.irc_port = int(botnet.irc_addr.split(':')[1])
        except:
            self.log(botnet.botnet_id, "IRC server address mal-formed: '%s'" % str(botnet.irc_addr))
        self.irc_server_pass = botnet.irc_server_pwd
        self.nick = botnet.irc_nick
        self.user = botnet.irc_user
        self.mode = botnet.irc_mode
        self.chan_list = botnet.irc_channel.split(', ')
        self.botnet = botnet
        self.channel_names = []
        self.retried = False
    
    def send(self, msg):
        #print repr(msg)
        self.s.send(msg)
        
    def send_pass(self):
        self.send("PASS %s\r\n" % self.irc_server_pass)
        
    def connect(self):
        # Create socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect socket
        try:
            self.msg_db = database.MessageDB(self.botnet.botnet_id)
            #self.s.settimeout(20.0)
            self.s.connect((self.irc_host, self.irc_port))
            # Send server password
            if self.irc_server_pass != "":
                self.send_pass()
        except socket.timeout, e:
            self.log(self.botnet.botnet_id, "Connection timeout: %s" % e)
            self.botnet_db.update_status(self.botnet.botnet_id,"server_status","TimeOut")
            if not self.retried:
                self.log(self.botnet.botnet_id, "Reconnecting...")
                self.retried = True
                self.s.connect((self.irc_host, self.irc_port))
        except Exception as e:
            self.botnet_db.update_status(self.botnet.botnet_id,"server_status","Error" + str(e))
            self.log(self.botnet.botnet_id, "Connection error: %s" % str(e))
            return self.channel_names
        else:
            self.botnet_db.update_status(self.botnet.botnet_id,"server_status","Connected")
            self.log(self.botnet.botnet_id, "Connected to IRC server")
            self.read()
    
    def set_nick(self):
        # Set nick
        self.send("NICK %s\r\n" % self.nick)
        
    def set_user(self):
        # Set user
        self.send("USER %s\r\n" % self.user)
        
    def change_nick(self):
        # TODO: change nick to a valid bot nick
        self.nick = "x" + self.nick[1:]
        self.send("self.nick %s\r\n" % self.nick)
        
    def set_mode(self):
        # Set mode
        self.send("MODE %s\r\n" % self.mode)        
        
    
    def get_drones(self):
        channel_names = self.line[6:]
        for name in channel_names:
            if name.startswith("@"):
                name = name.partition("@")[2]
            if name.startswith("&"):
                name = name.partition("&")[2]
            self.send("WHOIS %s\r\n" % name)
    
    def join_channel(self):
        for channel in self.chan_list:
            channel = channel.strip()
            if channel != "" and channel != "#":
                self.send("JOIN %s\r\n" % channel)
        
    def read(self):
        readbuffer = ""
        closed = 0
        retries = 0
        # timerange before timeout
        timerange = 3*24*60*60
        start_time = time.time()
        self.set_nick()
        self.set_user()
        self.set_mode()
        while closed != 1 or retries < 3:
            if time.time() - start_time > timerange:
                self.log(self.botnet_id, "Timeout reached")
                self.s.close()
                self.botnet_db.update_status(self.botnet.botnet_id, "server status" , "disconnected")
                break
            try:
                readbuffer = readbuffer + self.s.recv(1024)
                temp = readbuffer.split("\n")
                readbuffer = temp.pop()
                for line in temp:
                    line = line.rstrip()
                    #self.log(self.botnet.botnet_id, line)
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.msg_db.insert(timestamp, line)
                    self.line = line.split()
                    # The IRC table tennis 
                    if self.line[0] == "PING":
                        self.send("PONG %s\r\n" % self.line[1])
                    # If connected, join the channel
                    if self.line[1] == "001":
                        self.join_channel()
                    # No channel given
                    if self.line[1] == "461" and self.line[3] == "JOIN":
                        self.s.close()
                        self.botnet_db.update_status(self.botnet_db.botnet_id, "server status" , "disconnected")
                        closed = 1
                    # Channel joined
                    if self.line[1] == "366":
                        self.log(self.botnet.botnet_id, "IRC Channel successful joined")
                    # List users in channel and get IPs/domains
                    if self.line[1] == "353":
                        self.get_drones()
                    # Nick already in use
                    if self.line[1] == "433":
                        self.change_nick()
                    # Error while connecting (banned?)
                    if self.line[0] == 'ERROR' and self.line[1] == ':Closing':
                        self.s.close()
                        self.botnet_db.update_status(self.botnet.botnet_id, "server status" , "disconnected")
                        closed = 1
                    # Whois domain
                    if self.line[1] == "311":
                        self.channel_names.append(self.line[5])
                    # development command
                    if self.line[1] == "PRIVMSG" and self.line[3] == ":quit!":
                        self.s.close()
                        self.botnet_db.update_status(self.botnet.botnet_id, "server status" , "disconnected")
                        closed = 1
                    if self.line[1] == "TOPIC":
                        print "Got topic: %s" % str(self.line)
                        self.botnet_db.update_topic(str(self.line), self.botnet.botnet_id)
            except socket.timeout, e:
                self.botnet_db.update_status(self.botnet.botnet_id,"server_status","TimeOut")
                self.log(self.botnet.botnet_id, "Timeout: %s" % e)
                retries += 1
            except socket.error, e:
                self.botnet_db.update_status(self.botnet.botnet_id,"server_status","Error" + str(e))
                self.log(self.botnet.botnet_id, "Error: %s while connecting to the IRC server!" % e[1])
                retries += 1
            except Exception as e:
                self.botnet_db.update_status(self.botnet.botnet_id,"server_status","Error" + str(e))
                self.log(self.botnet.botnet_id, "Unknown error: %s" % str(e))
                retries += 1
        self.msg_db.close_handle()
        
        