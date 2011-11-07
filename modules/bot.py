import socket
import time

class Trojan_Horse():
 
    def __init__(self):
        pass
    
    def connect(self, server):
        HOST = server[0]
        PORT = server[1]
        PASS = ""
        self.CHAN = server[2]
        NICK = server[3]
        IDENT = server[4]
        NAMES = []
        readbuffer = ""
        closed = 0
        # timerange before timeout
        timerange = 1*60
        start_time = time.time()
        # Create socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect socket
        try:
            self.s.connect((HOST, PORT))
            self.s.settimeout(5.0)
            # Send server password
            if PASS != "":
                self.s.send("PASS %s\r\n" % PASS)
            # Set nick
            self.s.send("NICK %s\r\n" % NICK)
            # Set user
            self.s.send("USER %s\r\n" % IDENT)
        except socket.timeout, e:
            print "Timeout: %s" % e
            return NAMES
        except socket.error, e:
            print "Error: %s while connecting to the IRC server!" % e[1]
            return NAMES
        except e:
            print "unknown error: %s" % e
            return NAMES
        while closed != 1:
            if time.time() - start_time > timerange:
                print "timeout reached"
                self.s.close()
                break
            try:
                readbuffer = readbuffer + self.s.recv(1024)
                temp = readbuffer.split("\n")
                readbuffer = temp.pop()
                for line in temp:
                    line = line.rstrip()
                    self.line = line.split()
                    # The IRC table tennis 
                    if(self.line[0]=="PING"):
                        self.s.send("PONG %s\r\n" % self.line[1])
                    # If connected, join the channel
                    if self.line[1] == "001":
                        self.join_channel()
                    # No channel given
                    if self.line[1] == "461" and self.line[3] == "JOIN":
                        self.s.close()
                        closed = 1
                    # Channel joined
                    if self.line[1] == "366":
                        print "IRC Channel successful joined."
                    # List users in channel and get IPs/domains
                    if self.line[1] == "353":
                        self.get_drones()
                    # Nick already in use
                    if self.line[1] == "433":
                        NICK = "x" + NICK[1:]
                        self.s.send("NICK %s\r\n" % NICK)
                    # Error while connecting (banned?)
                    if self.line[0] == 'ERROR' and self.line[1] == ':Closing':
                        self.s.close()
                        closed = 1
                    # Whois domain
                    if self.line[1] == "311":
                        NAMES.append(self.line[5])
                    # development command
                    if self.line[1] == "PRIVMSG" and self.line[3] == ":quit!":
                        self.s.close()
                        closed = 1
                    if self.line[1] == "TOPIC":
                        print "Got topic: %s" % str(self.line)
            except socket.timeout, e:
                print "Timeout: %s" % e
                return NAMES
            except socket.error, e:
                print "Error: %s while connecting to the IRC server!" % e[1]
                return NAMES
            except:
                print "Unknown error"
                return NAMES
        return NAMES
    
    def get_drones(self):
        names = self.line[6:]
        for name in names:
            if name.startswith("@"):
                name = name.partition("@")[2]
            if name.startswith("&"):
                name = name.partition("&")[2]
            self.s.send("WHOIS %s\r\n" % name)
    
    def join_channel(self):
        for channel in self.CHAN:
            if channel != "" and channel != "#":
                self.s.send("JOIN %s\r\n" % channel)