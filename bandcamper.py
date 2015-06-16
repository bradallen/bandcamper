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
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, ID3, TALB, TPE1, TPE2, COMM, USLT, TCOM, TCON, TDRC, error


def validate_url(url):
    #TODO: validate url, duh
    return False

def change_song_details(audio_path, title, artist, art_path):
    mp3 = MP3(audio_path, ID3=ID3)
    id3 = ID3(audio_path)

    set_tags(mp3)
    set_album_art(mp3, art_path, 'image/jpg')
    set_title(id3, title)
    set_artist(id3, artist)

    mp3.save()
    id3.save()

    print 'Track: %s' % id3['TIT2'].text[0]
    print 'Artist: %s' % id3['TALB'].text[0]

def set_tags(mp3):
    try:
        mp3.add_tags()
    except error as e:
        print e
        pass

def set_album_art(mp3, art_path, image_type):
    try:
        mp3.tags.add(
            APIC(
                encoding = 3, # 3 is for utf-8
                mime = image_type, # image/jpeg or image/png
                type = 3, # 3 is for the cover image
                desc = u'Cover',
                data = open(art_path).read()
            )
        )
    except error as e:
        print e
        pass

def set_title(id3, title):
    try:
        id3.add(TIT2(encoding = 3, text = title))
    except error as e:
        print e
        pass

def set_artist(id3, artist):
    try:
        id3.add(TALB(encoding = 3, text = artist))
    except error as e:
        print e
        pass


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
        change_song_details('tests/sample.mp3', 'Side A', 'Kappa Chow', 'tests/albumart2.jpg')
else:
    print "Gimmie something to rip bud!"


