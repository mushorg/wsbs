# Automated PHP file analyzer and web server botnet spy. All rights by Lukas Rist (glaslos@gmail.com)

import sys
sys.path.append("modules")

import phpsandbox
import result
import bot
import database
import chan

from os import listdir

import Queue
import threading

print "Web Server Botnet Researcher started..."

file_list = listdir("file/")
queue = Queue.Queue()

irc_bot = bot.Trojan_Horse()
database.create()

class ThreadWSBS(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            #grabs host from queue
            php_file = self.queue.get()

            wsb(php_file)

            #signals to queue job is done
            self.queue.task_done()

def main():
    
    #spawn a pool of threads, and pass them queue instance 
    for i in range(5):
        t = ThreadWSBS(queue)
        t.setDaemon(True)
        t.start()

    #populate queue with data
    for file in file_list:
        queue.put(file)
    
    #wait on the queue until everything has been processed
    queue.join()

def wsb(php_file):
    
    report = phpsandbox.to_sandbox(php_file)
    HOST, PORT, CHAN, NICK, USER = result.parse(report)
    if HOST != "":
        if len(CHAN) < 1:
            print "no channel found, searching..."
            CHAN = set(chan.search(php_file))
            print CHAN
        database.insert(HOST, PORT, CHAN, NICK, USER)
        
def spy():
    for server in database.select_servers():
        print "Connecting to %s" % server[1]
        irc_bot.connect(server)

if __name__ == "__main__":
    main()