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

def find_the_stuff(garbage):
    regex = re.compile("trackinfo\s\:\s\[")

    for m in regex.finditer(garbage):
        start = m.start()
    if start:
        i = start
        end = None
        while not end:
            if garbage[i] is "," and garbage[i-1] is "]":
                end = i
            i += 1

        track_trash = garbage[start:end]
        less_trash = re.sub(regex, '{\"trackinfo\":[', track_trash)
        good_stuff = re.sub("\}\]", '}]}', less_trash)
    else:
        good_stuff = None

    return good_stuff


def rip_it_up(album_url):

    response = urllib2.urlopen(album_url)
    if(response.getcode() == 200):
        garbage = response.read()
        good_stuff = find_the_stuff(garbage)
        if good_stuff:
            print "sup"
            json_stuff = json.loads(good_stuff)
            pprint.pprint(json_stuff)

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


