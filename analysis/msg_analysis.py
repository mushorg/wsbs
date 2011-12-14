import sqlite3

d = 0

def parse_msg(msg):
    prefix = ""
    trailing = []
    if msg[0] == ':':    
        prefix, msg = msg[1:].split(' ', 1)
    if msg.find(' :') != -1:
        msg, trailing = msg.split(' :', 1)
        args = msg.split()
        args.append(trailing)
    else:
        args = msg.split()
    command = args.pop(0)
    return prefix, command, args

def parse_bot(row):
    
    global d
    parsed_msg1 = parse_msg(row[1].encode('utf-8')) #Time
    parsed_msg = parse_msg(row[2].encode('utf-8'))  #whole message
        #print parsed_parsed_msg1  ,"**",parsed_msg
    
    if parsed_msg[1] == "004":
        print "Date:",parsed_msg1[1],"\n our nickname=",parsed_msg[2][0] ,"\n servername =", parsed_msg[2][1] ,"\n version =", parsed_msg[2][2] ,"\n available user modes =",parsed_msg[2][3],"\n available channel modes =",parsed_msg[2][4],"\n"
            #<servername> <version> <available user modes> <available channel modes>"
    if parsed_msg[1] == "311":
        print "Time:",parsed_msg1[2],"\n A bot joins \n nickname:" ,parsed_msg[2][1],"\n username:" ,parsed_msg[2][2] ,"\n hostname:" ,parsed_msg[2][3],"\n realname:" ,parsed_msg[2][5],"\n"
        d = d+1    
    return d  



c = sqlite3.connect("../db/botnet_info_msg.db")
cc = c.cursor()


for i in range(1,32):
    count = 0 
    cc.execute("SELECT * FROM Botnet_%s" % str(i)) 
    
    global d
    d = 0
    print "\nBotnet_%s" % str(i),": "
    
    for row in cc.fetchall():       
        b = parse_bot(row)
        count = count + 1
    
    if count == 0:
        print "No activity \n"
    else:
        print "total:", str(b),"bots joined \n" 
       
       
          