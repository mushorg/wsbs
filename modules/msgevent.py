import msg
import database

import GeoIP


for i in range(1, 35): 
    msg_event = msg.BotnetAnalysis()
    botnet_info_db = database.BotnetInfoDB()
    botTrack = msg.BotTrack()

    msg_event.cc.execute("SELECT * FROM Botnet_%s" % str(i))
    for row in msg_event.cc.fetchall():
        if not row[2] == "":
            parsed_msg = msg_event.parse_msg(row[2].encode('utf-8'))

            if parsed_msg[1] == "004":
                itype = msg_event.Botnet_Server_Type(parsed_msg[2])
                botnet_info_db.update_servertype(str(i), itype)

            if parsed_msg[1] == "PRIVMSG":
                dork_info = msg_event.PRIVMSG_dork(parsed_msg[2])
                if dork_info:
                    botTrack.insert_privmsg(row[1], i, dork_info[0],
                                            dork_info[1], dork_info[2])

            if parsed_msg[1] == "311":
                gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
                botTrack.insert_BotIP(row[1], i, parsed_msg[2][0],
                                      parsed_msg[2][1], parsed_msg[2][2],
                                      parsed_msg[2][3], parsed_msg[2][5],
                                      gi.country_code_by_addr(parsed_msg[2][3]),
                                      gi.country_code_by_name(parsed_msg[2][3]))
