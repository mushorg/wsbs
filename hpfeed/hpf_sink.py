import sys

if __name__ == '__main__':
    import hpfeeds
else:
    import hpfeed.hpfeeds as hpfeeds


class HPFeedsSink(object):

    def __init__(self):
        self.host = 'hpfeeds.honeycloud.net'
        self.port = 10000
        self.channels = ['glastopf.sandbox', ]
        self.ident = ''
        self.secret = ''

    def log(self, msg):
        print '[feedcli] {0}'.format(msg)

    def run(self):
        try:
            hpc = hpfeeds.new(self.host, self.port, self.ident, self.secret)
        except hpfeeds.FeedException, e:
            print >>sys.stderr, 'feed exception:', e
            return 1

        print >>sys.stderr, 'connected to', hpc.brokername

        def on_message(identifier, channel, payload):
            print "message",
            print identifier, channel, payload

        def on_error(payload):
            print ' -> errormessage from server: {0}'.format(payload)
            hpc.stop()

        hpc.subscribe(self.channels)
        try:
            hpc.run(on_message, on_error)
        except hpfeeds.FeedException, e:
            print >>sys.stderr, 'feed exception:', e
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
