 #!/usr/bin/env python
import urllib
import urllib2
import json
import re
import os.path
import readline, glob
# import subprocess
import sys


def validate_url(url):
    #TODO: validate url, duh
    return True

def rip_it_up(album_url):
    response = urllib2.urlopen(album_url)
    if(response.getcode() == 200):
        garbage = response.read()
        #TODO: doesn't work, too many backtracks might have to grab values individually
        the_stuff = re.match(garbage, "/(?=var\sTralbumData\s\=\s\{)(.|\s)*(?=\}\;)/")
        if the_stuff:
            print the_stuff
        else:
            return False
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


