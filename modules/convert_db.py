import sqlite3


class convert_botnet_info_db(object):
    """
    This script is for converting wsbs database to add three columns
    with server_status, channel_status, and bot_status
    """
    def __init__(self):
        self.conn = sqlite3.connect("../db/botnet_info.db")
        self.convert_it()

    def convert_it(self):
        cursor = self.conn.cursor()
        schema = cursor.execute("""SELECT * FROM sqlite_master
                    WHERE type='table' AND name='botnet_info'""").fetchone()
        try:
            if not 'server_status' in schema[4]:
                print "Adding server_status"
                cursor.execute("""ALTER TABLE botnet_info
                                    ADD COLUMN server_status TEXT""")
            if not 'channel_status' in schema[4]:
                print "Adding channel_status"
                cursor.execute("""ALTER TABLE botnet_info
                                    ADD COLUMN channel_status TEXT""")
            if not 'bot_status' in schema[4]:
                print "Adding bot_status"
                cursor.execute("""ALTER TABLE botnet_info
                                    ADD COLUMN bot_status TEXT""")
            if not 'server_type' in schema[4]:
                print "Adding server_type"
                cursor.execute("""ALTER TABLE botnet_info
                                    ADD COLUMN server_type TEXT""")
        except Exception as e:
            print e
        self.conn.commit()
        cursor.close()
        self.conn.close()

cdb = convert_botnet_info_db()
