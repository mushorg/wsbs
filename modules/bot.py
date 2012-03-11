import socket
import time
import modules.database as database
import datetime


class Trojan_Horse():

    def log(self, msg):
        print "[irc_client] %s : %s" % (self.botnet.botnet_id, msg)

    def __init__(self, botnet):
        self.botnet = botnet
        self.mal_formed = False
        self.botnet_db = database.BotnetInfoDB()
        try:
            if "udp://" in botnet.irc_addr:
                    botnet.irc_addr = botnet.irc_addr.partition("udp://")[2]
            self.irc_host = botnet.irc_addr.split(':')[0]
            self.irc_port = int(botnet.irc_addr.split(':')[1])
        except Exception as e:
            self.log("IRC server address mal-formed: '%s' error: %s" %
                     (botnet.irc_addr, str(e)))
            self.mal_formed = True
        self.irc_server_pass = botnet.irc_server_pwd
        self.nick = botnet.irc_nick
        self.user = botnet.irc_user
        self.mode = botnet.irc_mode
        if isinstance(botnet.irc_channel, (str, unicode)):
            self.chan_list = botnet.irc_channel.split(', ')
        else:
            self.chan_list = botnet.irc_channel
        self.channel_names = []
        self.log(" ".join([self.irc_host, str(self.irc_port),
                           self.nick, self.user]))
        self.retried = False

    def send(self, msg):
        #print repr(msg)
        self.s.send(msg)

    def send_pass(self):
        self.send("PASS %s\r\n" % self.irc_server_pass)

    def set_nick(self):
        # Set nick
        self.send("NICK %s\r\n" % self.nick)

    def set_user(self):
        # Set user
        print repr(self.user)
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
        timerange = 3 * 24 * 60 * 60
        start_time = time.time()
        self.set_user()
        self.set_nick()
        self.set_mode()
        while closed != 1 or retries < 3:
            if time.time() - start_time > timerange:
                self.log("Timeout reached")
                self.s.close()
                self.botnet_db.update_status(self.botnet.botnet_id,
                                             "server_status", "disconnected")
                break
            try:
                readbuffer = readbuffer + self.s.recv(1024)
                temp = readbuffer.split("\n")
                readbuffer = temp.pop()
                for line in temp:
                    line = line.rstrip()
                    self.log(line)
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
                        self.botnet_db.update_status(self.botnet_id,
                                        "server_status", "disconnected")
                        closed = 1
                        break
                    # Channel joined
                    if self.line[1] == "366":
                        self.log(
                                 "IRC Channel successful joined")
                    # List users in channel and get IPs/domains
                    if self.line[1] == "353":
                        self.get_drones()
                    # Nick already in use
                    if self.line[1] == "433":
                        self.change_nick()
                    # Error while connecting (banned?)
                    if self.line[0] == 'ERROR' and self.line[1] == ':Closing':
                        try:
                            self.s.close()
                        except:
                            print "close failed"
                        self.botnet_db.update_status(self.botnet.botnet_id,
                                            "server_status", "disconnected")
                        closed = 1
                        break
                    if self.line[1] == "311":
                        self.channel_names.append(self.line[5])
                    if self.line[1] == "TOPIC":
                        self.log("Got topic: %s" % str(self.line))
                        self.botnet_db.update_topic(str(self.line),
                                                    self.botnet.botnet_id)
                    if self.line[1] == "431":
                        self.log("NICK: No nickname given, disconnecting")
                        closed = 1
                        break
                    if self.line[1] == "461":
                        self.log("USER: Not enough parameters, disconnecting")
                        closed = 1
                        break
            except socket.timeout, e:
                self.botnet_db.update_status(self.botnet.botnet_id,
                                             "server_status", "timeout")
                self.log("Timeout: %s" % e)
                retries += 1
            except socket.error, e:
                self.botnet_db.update_status(self.botnet.botnet_id,
                                        "server_status", "error %s" % str(e))
                self.log(
                        "Error: %s while reading from IRC server!" % e[1])
                print self.irc_host, self.irc_port
                retries += 1
            except Exception as e:
                self.botnet_db.update_status(self.botnet.botnet_id,
                                        "server_status", "error %s" % str(e))
                self.log(
                                        "Unknown read error: %s" % str(e))
                retries += 1
        self.msg_db.close_handle()

    def connect(self):
        max_reconnects = 4
        re_connects = 0
        connected = False
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.msg_db = database.MessageDB(self.botnet.botnet_id)
        while not connected and re_connects <= max_reconnects:
            try:
                #self.s.settimeout(20.0)
                self.s.connect((self.irc_host, self.irc_port))
            except socket.timeout, e:
                self.botnet_db.update_status(self.botnet.botnet_id,
                                             "server_status", "timeout")
                self.log("Connection timeout: %s" % e)
                re_connects += 1
                time.sleep(2)
            except Exception as e:
                self.botnet_db.update_status(self.botnet.botnet_id,
                                        "server_status", "error %s" % str(e))
                self.log("Connection error: %s" % str(e))
                re_connects += 1
                time.sleep(2)
            else:
                self.botnet_db.update_status(self.botnet.botnet_id,
                                             "server_status", "connected")
                self.log("Connected to IRC server")
                connected = True
        if connected:
            if self.irc_server_pass != "":
                self.send_pass()
            self.read()
        else:
            self.log("Unable to connect, finishing job...")
            return None
