"""All rights by Lukas Rist (glaslos@gmail.com)"""

import Queue
import threading
import sys

sys.path.append("modules")

import modules.bot as bot
import modules.database as database

print "Web Server Botnet Researcher started..."

class ThreadWesBos(threading.Thread):
    """Class to analyze PHP files using
    the pKaji PHP sandbox and process the results."""
    
    def __init__(self, file_queue):
        threading.Thread.__init__(self)
        self.file_queue = file_queue
        self.irc_bot = bot.Trojan_Horse()
        self.botnet_db = database.BotnetDB()

    def run(self):
        while True:
            # grabs php file from queue
            php_file = self.file_queue.get()
            # process file
            self.wsb(php_file)
            # signals to queue job is done
            self.file_queue.task_done()
            
    def wsb(self, botnet):
        NAMES = self.spy(botnet)
        if len(NAMES) > 0:
            print "We found %s drones in a botnet!" % len(NAMES)
        # write all we found into the sqlite database and get the ID
        self.mysql_database.insert(botnet)
        print "%s files left in queue" % self.file_queue.qsize()
        return
    
    def spy(self, server):
        """"Function to handle the irc spies"""
        print "Connecting to %s" % server[0]
        NAMES = self.irc_bot.connect(server)
        return NAMES

def main():
    """Function spawning the threads, managing the queue and 
    waiting for all threads to finish"""
    
    file_queue = Queue.Queue()
    
    # spawn a pool of threads, and pass them the queue instances 
    for i in range(10):
        t = ThreadWesBos(file_queue)
        t.setDaemon(True)
        t.start()
    # populate the file queue with data
    credentials_db = database.CredentialsDB()
    botnet_list = credentials_db.get_credentials() 
    for botnet in botnet_list:
        file_queue.put(botnet)
    # wait on the queue until everything has been processed
    file_queue.join()
    
if __name__ == "__main__":
    main()