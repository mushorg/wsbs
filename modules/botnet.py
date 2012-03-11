class Botnet(object):

    def __init__(self, botnet):
        self.botnet_id = None
        self.sandbox_id = botnet['id']
        self.file_name = botnet['file_name']
        self.file_md5 = botnet['file_md5']
        self.first_analysis_date = botnet['first_analysis_date']
        self.last_analysis_date = botnet['last_analysis_date']
        self.irc_addr = botnet['irc_addr']
        self.irc_server_pwd = botnet['irc_server_pwd']
        self.irc_nick = botnet['irc_nick']
        self.irc_user = botnet['irc_user']
        self.irc_mode = botnet['irc_mode']
        self.irc_channel = botnet['irc_channel']
        self.irc_nickserv = botnet['irc_nickserv']
        self.irc_notice = botnet['irc_notice']
        self.irc_privmsg = botnet['irc_privmsg']
