import sys
import json

from datetime import datetime

if __name__ == '__main__':
    import hpfeeds
else:
    import hpfeed.hpfeeds as hpfeeds
    import modules.botnet as botnet
    from modules import database


class HPFeedsSink(object):

    def __init__(self, conf):
        self.host = conf.get("hpfeed", "host")
        self.port = conf.getint("hpfeed", "port")
        self.channels = conf.get("hpfeed", "chan").split(",")
        self.ident = conf.get("hpfeed", "ident")
        self.secret = conf.get("hpfeed", "secret")

    def botnet_to_db(self, botnet):
        self.botnet_id = None
        botnet_db = database.BotnetInfoDB()
        if len(botnet.irc_channel) > 0:
            channel = ', '.join(botnet.irc_channel)
        else:
            channel = ""
        duplicate_botnet_id = botnet_db.select_by_features(botnet.irc_addr,
                                                           channel)
        if not duplicate_botnet_id:
            botnet_db.connect()
            self.botnet_id = botnet_db.insert(botnet)
            botnet_db.close()
        else:
            botnet_db.update_time(botnet.last_analysis_date,
                                  duplicate_botnet_id[0])

    def log(self, msg):
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print '[hpf sink {0}] {1}'.format(time_stamp, msg)

    def run(self, botnet_queue):
        self.botnet_queue = botnet_queue
        try:
            hpc = hpfeeds.new(self.host, self.port, self.ident, self.secret)
        except hpfeeds.FeedException, e:
            self.log('Feed exception: %s' % e)
            return 1

        self.log('Connected to: %s' % hpc.brokername)

        def on_message(identifier, channel, payload):
            analysis_report = json.loads(str(payload))
            print analysis_report
            self.log("New sandbox report for file: %s" %
                     analysis_report['file_md5'])
            if __name__ == "__main__":
                print analysis_report['irc_addr'], analysis_report['irc_nick']
            else:
                analysis_report = botnet.Botnet(analysis_report)
                self.botnet_to_db(analysis_report)
                analysis_report.botnet_id = self.botnet_id
                self.botnet_queue.put(analysis_report)

        def on_error(payload):
            self.log('Error message from server: {0}'.format(payload))
            hpc.stop()

        hpc.subscribe(self.channels)
        try:
            hpc.run(on_message, on_error)
        except hpfeeds.FeedException, e:
            self.log('Feed exception: %s' % e)
        except KeyboardInterrupt:
            pass
        finally:
            hpc.close()
        return 0

if __name__ == '__main__':
    hs = HPFeedsSink()
    try:
        sys.exit(hs.run())
    except KeyboardInterrupt:
        sys.exit(0)
