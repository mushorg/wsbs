""" Automated PHP file analyzer using the pKaji PHP sandbox
    and web server botnet spy.
 
    All rights by Lukas Rist (glaslos@gmail.com)"""

from os import listdir

import Queue
import threading
import sys
import time

sys.path.append("modules")

import modules.phpsandbox as phpsandbox
import modules.result as result
import modules.bot as bot
import modules.database as database
import modules.parse_xml as parse_xml

print "Web Server Botnet Researcher started..."

file_list = listdir("file/")
#file_list = ("small_bot.txt",)
sum_files = len(file_list)
print "There are %s PHP files in the queue!" % sum_files 
time.sleep(1)

file_queue = Queue.Queue()

xml_parser = parse_xml.ReportParser()
irc_bot = bot.Trojan_Horse()
mysql_database = database.MySQLDB()

mysql_database.create()

class ThreadWesBos(threading.Thread):
    """Class to analyze PHP files using
    the pKaji PHP sandbox and process the results."""
    
    def __init__(self, file_queue):
        threading.Thread.__init__(self)
        self.file_queue = file_queue

    def run(self):
        while True:
            # grabs php file from queue
            php_file = self.file_queue.get()
            # process file
            self.wsb(php_file)
            # signals to queue job is done
            self.file_queue.task_done()
            
    def wsb(self, php_file):
        """Function to handle all actions with the sandbox"""
        # skip the subversion folder
        if php_file == ".svn":
            return
        file = open("file/" + php_file, 'r')
        for line in file.readlines():
            # we only analyze PHP files which opens a socket
            if "fsockopen" in line:
                # send file to pKaji sandbox
                sandbox_report = phpsandbox.to_sandbox(php_file)
                # parse the result
                if sandbox_report:
                    server = xml_parser.handle_report(sandbox_report)
                    if server[0] != "":
                        print server
                        # Connect to the server and get botnet information
                        NAMES = self.spy(server)
                        if len(NAMES) > 0:
                            print "We found %s drones in a botnet!" % len(NAMES)
                        # write all we found into the sqlite database and get the ID
                        HOST, PORT, CHAN, NICK, USER = server
                        mysql_database.insert(HOST, PORT, CHAN, NICK, USER, NAMES, php_file)
                        print "%s files left in queue" % self.file_queue.qsize()
                # file successful processed
                return
            else:
                # we are not interested in this file
                return
    
    def spy(self, server):
        """"Function to handle the irc spies"""
        print "Connecting to %s" % server[0]
        NAMES = irc_bot.connect(server)
        return NAMES

def main():
    """Function spawning the threads, managing the queue and 
    waiting for all threads to finish"""
    # spawn a pool of threads, and pass them the queue instances 
    for i in range(10):
        t = ThreadWesBos(file_queue)
        t.setDaemon(True)
        t.start()
    # populate the file queue with data
    for file in file_list:
        file_queue.put(file)
    # wait on the queue until everything has been processed
    file_queue.join()
    
if __name__ == "__main__":
    main()