# Automated PHP file analyzer and web server botnet spy. All rights by Lukas Rist (glaslos@gmail.com)

import sys
sys.path.append("modules")

import phpsandbox
import result
import bot
import database
import chan

from os import listdir

def wsbs():
    print "Web Server Botnet Researcher started..."
    
    irc_bot = bot.Trojan_Horse()
    database.create()
    
    file_list = listdir("file/")
    #file_list = ["03ca9d71a172c71984f09b8c2f382412",]
    for php_file in file_list:
        report = phpsandbox.to_sandbox(php_file)
        HOST, PORT, CHAN, NICK, USER = result.parse(report)
        if HOST != "":
            print HOST, PORT, CHAN, NICK, USER
            if len(CHAN) < 1:
                print "no channel found, searching..."
                CHAN = set(chan.search(php_file))
                print CHAN
            database.insert(HOST, PORT, CHAN, NICK, USER)
    for server in database.select_servers():
        print "Connecting to %s" % server[1]
        irc_bot.connect(server)

if __name__ == "__main__":
    wsbs()