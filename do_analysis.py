import modules.database as database
import analysis.msg as msg
import GeoIP
import os


blist = os.listdir("db/botnets/")
for item in blist:
    dbname = "db/botnets/" + item
    botnet_id = item.split("Botnet_")[1].split(".db")[0]

    msg_botnet = msg.BotnetAnalysis()
    msg_track = msg.BotTrackDB()
    bot_info_db = database.BotnetInfoDB()

    rowall = msg_botnet.db_select(dbname)
    gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
    for row in rowall:
        if not row[2] == "":
            timestamp = row[1]
            parsed_msg = msg_botnet.parse_msg(row[2].encode('utf-8'))
            if parsed_msg[1] == "004":
                itype = msg_botnet.Botnet_Server_Type(parsed_msg[2])
                bot_info_db.update_servertype(botnet_id, itype)
            if parsed_msg[1] == "PRIVMSG":
                dork_info = msg_botnet.PRIVMSG_dork(parsed_msg[2])
                if dork_info:
                    msg_track.insert_privmsg(timestamp, botnet_id,
                            dork_info[0], dork_info[1], dork_info[2])
            if parsed_msg[1] == "311":
                geoip = gi.country_code_by_addr(parsed_msg[2][3])
                geoname = gi.country_code_by_name(parsed_msg[2][3])
                msg_track.insert_BotIP(timestamp, botnet_id, parsed_msg[2],
                                            geoip, geoname)
