# Copyright (C) 2011  Lukas Rist
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import Queue
import threading
import datetime

import modules.bot as bot
import modules.database as database


class WesBos(threading.Thread):

    def __init__(self, botnet_queue):
        threading.Thread.__init__(self)
        self.botnet_queue = botnet_queue

    def run(self):
        while self.botnet_queue.qsize() > 0:
            botnet_size = 0
            # grabs php file from queue
            botnet = self.botnet_queue.get()
            # process file
            irc_bot = bot.Trojan_Horse(botnet)
            botnet_size = irc_bot.connect()
            if len(botnet_size) > 0:
                print "We found %s drones in a botnet!" % len(botnet_size)
            # signals to queue job is done
            self.botnet_queue.task_done()


def main():
    botnet_queue = Queue.Queue()

    # populate the file queue with data
    sandbox_db = database.SandboxDB()
    sandbox_list = sandbox_db.get_credentials()
    sandbox_db.close()
    botnet_db = database.BotnetInfoDB()
    for botnet in sandbox_list:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        duplicate_botnet_id = botnet_db.select_by_features(botnet.irc_addr,
                                                           botnet.irc_channel)
        if not duplicate_botnet_id:
            botnet_db.insert(botnet.irc_addr,
                             botnet.irc_server_pwd,
                             botnet.irc_nick,
                             botnet.irc_user,
                             botnet.irc_mode,
                             botnet.irc_channel,
                             botnet.sandbox_id,
                             timestamp
                             )
        else:
            botnet_db.update_time(botnet.analysis_date, duplicate_botnet_id[0])
    botnet_list = botnet_db.select_all()

    # spawn a pool of threads, and pass them the queue instances
    # Count the unique C&C plus channel, then initialize the thread
    for botnet in botnet_list:
        botnet_queue.put(botnet)
    for i in range(len(botnet_list)):
        t = WesBos(botnet_queue)
        t.setDaemon(True)
        t.start()
    botnet_db.close_handle()
    # wait on the queue until everything has been processed
    botnet_queue.join()

if __name__ == "__main__":
    main()
