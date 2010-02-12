'''
Created on 31.01.2010

@author: Lukas
'''

import socket
import time

import database

class Trojan_Horse():
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def connect(self, server):
        ID = server[0]
        HOST = server[1]
        PORT = server[2]
        PASS = ""
        CHAN = server[3]
        NICK = server[4]
        IDENT = server[5]
        
        # Create socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect socket
        try:
            s.connect((HOST, PORT))
            s.settimeout(5.0)
        except socket.error, e:
            print "Error: %s while connecting to the IRC server!" % e
            return
        # Send server password
        if PASS != "":
            s.send("PASS %s\r\n" % PASS)
        # Set nick
        s.send("NICK %s\r\n" % NICK)
        # Set user
        s.send("USER %s\r\n" % IDENT)
        
        NAMES = []
        readbuffer = ""
        closed = 0
        timerange = 1*60
        start_time = time.time()
        while closed != 1:
            if time.time() - start_time > timerange:
                print "timeout reached"
                s.close()
                break
            try:
                readbuffer = readbuffer + s.recv(1024)
                temp = readbuffer.split("\n")
                readbuffer = temp.pop()
                for line in temp:
                    line=line.rstrip()
                    line=line.split()
                    print line
                    # The IRC table tennis 
                    if(line[0]=="PING"):
                        s.send("PONG %s\r\n" % line[1])
                        print "PONG send"
                    # If connected, join the channel
                    if line[1] == "001":
                        try:
                            for channel in CHAN.split(","):
                                if channel != "":
                                    s.send("JOIN %s\r\n" % channel)
                                    print "joining %s" % channel
                        except:
                            print "Error while trying to join a IRC Channel"
                    # No channel given
                    if line[1] == "461" and line[3] == "JOIN":
                        s.close()
                        closed = 1
                    # Channel joined
                    if line[1] == "366":
                        print "IRC Channel successful joined."
                    # List of users in channel
                    if line[1] == "353":
                        names = line[6:]
                        for name in names:
                            if name.startswith("@"):
                                name = name.partition("@")[2]
                            s.send("WHOIS %s\r\n" % name)
                    # Nick already in use
                    if line[1] == "433":
                        NICK = "x" + NICK[1:]
                        s.send("NICK %s\r\n" % NICK)
                    # Error while connecting (banned?)
                    if line[0] == 'ERROR' and line[1] == ':Closing':
                        s.close()
                        closed = 1
                    # Whois domain
                    if line[1] == "311":
                        NAMES.append(line[5])
                    # devlopment command
                    if line[1] == "PRIVMSG" and line[3] == ":quit!":
                        s.close()
                        closed = 1
                    if input[1] == "TOPIC":
                        print "got topic"
            except socket.error, e:
                print "Error: %s while connecting to the IRC server!" % e
                return     
        database.insert_names(ID, NAMES)