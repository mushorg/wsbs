import sqlite3

def parse_msg(msg):
    prefix = ''
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


c = sqlite3.connect("../db/botnet_info_msg.db")
cc = c.cursor()

for i in range(1,32):
    cc.execute("SELECT * FROM Botnet_%s" % str(i))
    
    for row in cc.fetchall():
        parsed_msg = parse_msg(row[2].encode('utf-8'))
        if parsed_msg[1] == "311":
            print parsed_msg[2][3]        