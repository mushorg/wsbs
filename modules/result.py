'''
Created on 29.01.2010

@author: Lukas
'''

def parse(report):
    
    CnC_IP = ""
    CnC_PORT = ""
    CnC_CHANNEL = []
    CnC_NICK = ""
    CnC_USER = ""
    
    #print report
    for line in report:
        #if "<fsockopen>" in line:
        if "host=" in line:
            CnC_IP = line.partition("host=")[2].partition(",")[0]
            CnC_PORT = line.rpartition("port=")[2].partition(",")[0]
        #if "<fwrite>" in line and "JOIN" in line:
        if "JOIN" in line:
            CnC_CHANNEL.append("#" + line.partition("#")[2].partition("\n")[0].strip())
        if "NICK" in line:
            CnC_NICK = line.partition("NICK")[2].partition("\n")[0].strip()
        if "USER" in line:
            if ":Parse error:" in line or ":Fatal error:" in line:
                CnC_USER = line.partition("USER")[2].rpartition(":")[0].strip() + " :" + CnC_NICK
            else:
                CnC_USER = line.partition("USER")[2].partition("\"")[0].strip()
    return CnC_IP, CnC_PORT, CnC_CHANNEL, CnC_NICK, CnC_USER