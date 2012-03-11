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
import sys
import time

from ConfigParser import ConfigParser
from functools import partial

import modules.bot as bot
import modules.database as database
import hpfeed.hpf_sink as hpfeeds


class WesBos(threading.Thread):

    def __init__(self, botnet_queue):
        self.botnet_queue = botnet_queue
        threading.Thread.__init__(self)

    def run(self):
        botnet = self.botnet_queue.get()
        irc_bot = bot.Trojan_Horse(botnet)
        if not irc_bot.mal_formed:
            irc_bot.connect()
        self.botnet_queue.task_done()


class MonitorManager(object):

    def __init__(self):
        self.conf = ConfigParser()
        self.conf.read("wsbs.cfg")

    def db_import(self):
        sandbox_db = database.SandboxDB()
        sandbox_list = sandbox_db.get_credentials()
        sandbox_db.close()
        botnet_db = database.BotnetInfoDB()
        botnet_db.connect()
        for botnet in sandbox_list:
            if not isinstance(botnet.irc_channel, (str, unicode)):
                channel = ', '.join(botnet.irc_channel)
            duplicate_botnet_id = botnet_db.select_by_features(botnet.irc_addr,
                                                               channel)
            if not duplicate_botnet_id:
                botnet_db.insert(botnet)
            else:
                botnet_db.update_time(self.last_analysis_date,
                                      duplicate_botnet_id[0])
        botnet_db.close()

    def populate_queue(self):
        self.botnet_queue = Queue.Queue()
        botnet_db = database.BotnetInfoDB()
        botnet_list = botnet_db.select_all()
        for botnet in botnet_list:
            self.botnet_queue.put(botnet)

    def run(self, import_from_db=False):
        if import_from_db:
            self.db_import()
        self.populate_queue()
        hpfeeds_enabled = self.conf.get("hpfeed", "enabled").strip() in ['true', 'True', 'enable', 'yes']
        if hpfeeds_enabled:
            hs = hpfeeds.HPFeedsSink(self.conf)
            hpfeeds_thread = threading.Thread(target=partial(hs.run,
                                                self.botnet_queue))
            hpfeeds_thread.setDaemon(True)
            hpfeeds_thread.start()
        while True:
            if  not hpfeeds_enabled and self.botnet_queue.qsize() == 0:
                break
            nodes = int(self.conf.get("monitor_manager", "max_nodes"))
            queue_size = self.botnet_queue.qsize()
            if nodes == 0 or queue_size < (nodes -
                                           (threading.active_count() - 2)):
                nodes = queue_size
            else:
                nodes = nodes - (threading.active_count() - 2)
            for i in range(nodes):
                t = WesBos(self.botnet_queue)
                t.setDaemon(True)
                t.start()
            print "Botnets left in queue:", queue_size
            time.sleep(10)
        self.botnet_queue.join()

if __name__ == "__main__":
    monitor_manager = MonitorManager()
    try:
        sys.exit(monitor_manager.run())
    except KeyboardInterrupt:
        sys.exit(0)
