 #!/usr/bin/env python
import urllib
import urllib2
import json
import re
import os.path
import readline, glob
# import subprocess
import sys
import pprint


def validate_url(url):
    #TODO: validate url, duh
    return True

def rip_it_up(album_url):

    response = urllib2.urlopen(album_url)
    if(response.getcode() == 200):
        garbage = response.read()

        print "here it is"
        regex = re.compile("var\sTralbumData\s\=\s\{")

        for m in regex.finditer(garbage):
            start = m.start()

        i = start
        end = None
        while not end:
            if garbage[i] is ";" and garbage[i-1] is "}":
                end = i
            i += 1

        good_stuff = garbage[start:end]
    else:
        return False
    #download this shizz
    return True

if len(sys.argv) > 1:
    album_url = sys.argv[1]
    if validate_url(album_url):
        print "Now ripping " + album_url #TODO: grab album title from json
        if(rip_it_up(album_url)):
            print "Aw yiz"
        else:
            print "Ah, that's a real ding there"
    else:
        print "What this is?"
else:
    print "Gimmie something to rip bud!"

