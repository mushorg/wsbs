# Automated PHP file analyzer and web server botnet spy. All rights by Lukas Rist (glaslos@gmail.com)

from os import listdir

import Queue
import threading
import sys
import time
import re

sys.path.append("modules")

import phpsandbox
import result
import bot
import database
import chan

print "Web Server Botnet Researcher started..."

file_list = listdir("file/")
print "There are %s files in the queue!" % len(file_list)
time.sleep(1)

queue = Queue.Queue()

irc_bot = bot.Trojan_Horse()
database.create()

class ThreadWSBS(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            #grabs php file from queue
            php_file = self.queue.get()
            #process file
            wsb(php_file)
            #signals to queue job is done
            self.queue.task_done()

def wsb(php_file):
    if php_file == ".svn":
        return
    file = open("file/" + php_file, 'r')
    for line in file.readlines():
        if re.search("fsockopen", line):
            sandbox_report = phpsandbox.to_sandbox(php_file)
            HOST, PORT, CHAN, NICK, USER = result.parse(sandbox_report)
            if HOST != "":
                print HOST, PORT, CHAN, NICK, USER
                if len(CHAN) < 1:
                    print "no channel found, searching..."
                    CHAN = set(chan.search(php_file))
                    print CHAN
                database.insert(HOST, PORT, CHAN, NICK, USER, php_file)
            return
        else:
            return
        
def spy():
    for server in database.select_servers():
        print "Connecting to %s" % server[1]
        irc_bot.connect(server)

def main():
    
    #spawn a pool of threads, and pass them queue instance 
    for i in range(10):
        t = ThreadWSBS(queue)
        t.setDaemon(True)
        t.start()

    #populate queue with data
    for file in file_list:
        queue.put(file)
    
    #wait on the queue until everything has been processed
    queue.join()

if __name__ == "__main__":
    main()