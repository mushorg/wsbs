'''
Created on 03.02.2010

@author: Lukas
'''

import re

def search(php_file):
    CHAN = []
    file = open("file/" + php_file).read()
    if re.search("\\r", file):
        file = file.split("\r")
    elif re.search("\\n", file):
        file = file.split("\n")
    for line in file:
        if re.search("=\"#", line):
            chan = line.partition("\"")[2].partition("\"")[0].strip()
            if chan == "#" or chan == "#e0e0e0":
                continue
            elif chan not in CHAN:
                CHAN.append(chan)
            else:
                continue
    return CHAN