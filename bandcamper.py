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
from mutagen.id3 import ID3, APIC, TIT2, ID3, TALB, TPE1, TPE2, TRCK, TCON, TDRC, error

class tcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def validate_url(url):
    try:
        urllib2.urlopen(url)
        return True
    except:
        return False

def change_song_details(audio_path, title, artist, art_path, album_name, track_number, year, genre):
    mp3 = MP3(audio_path, ID3=ID3)
    set_tags(mp3)
    set_album_art(mp3, art_path, 'image/jpg')
    mp3.save()

    id3 = ID3(audio_path)
    set_album_name(id3, album_name)
    set_title(id3, title)
    set_artist(id3, artist)
    set_track_number(id3, track_number)
    set_year(id3, year)
    set_genre(id3, genre)
    id3.save()

    print 'Track: %s' % id3['TIT2'].text[0]
    print 'Artist: %s' % id3['TPE2'].text[0]
    print 'Album: %s' % id3['TALB'].text[0]
    print 'Year: %s' % id3['TDRC'].text[0]
    print 'Number: %s' % id3['TRCK'].text[0]

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

def set_album_name(id3, album_name):
    try:
        id3.add(TALB(encoding = 3, text = album_name))
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
        id3.add(TPE2(encoding = 3, text = artist))
    except error as e:
        print e
        pass

def set_track_number(id3, track_number):
    try:
        id3.add(TRCK(encoding = 3, text = track_number))
    except error as e:
        print e
        pass

def set_year(id3, year):
    try:
        id3.add(TDRC(encoding = 3, text = year))
    except error as e:
        print e
        pass

def set_genre(id3, genre):
    try:
        id3.add(TCON(encoding = 3, text = genre))
    except error as e:
        print e
        pass

def download_file(url, path, title):
    if not os.path.exists(os.path.expanduser(path)):
        os.makedirs(os.path.expanduser(path))

    file_name = title + ".mp3"
    download_url = urllib2.urlopen(url)
    file = open(os.path.expanduser(path + file_name), "wb")
    meta = download_url.info()
    file_size = int(meta.getheaders("Content-Length")[0])

    print "\nDownloading: %s Bytes: %s" % (tcolors.BOLD + file_name + tcolors.END, file_size)

    file_size_dl = 0
    block_sz = 8192

    while True:
        buffer = download_url.read(block_sz)

        if not buffer:
            break

        file_size_dl += len(buffer)
        file.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)

        print status,

    file.close()

def download_album(album_json):
    for t in album_json['trackinfo']:
        download_file(t['file']['mp3-128'], "~/Downloads/bandcamper-test/", t['title'])

    return True

def find_album_json(garbage):
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
        album_json = json.loads(good_stuff)
    else:
        album_json = None

    return album_json


def rip_it_up(album_url):
    response = urllib2.urlopen(album_url)

    if(response.getcode() == 200):
        garbage = response.read()
        album_json = find_album_json(garbage)
        if album_json:
            success = download_album(album_json)
    else:
        success = False

    return success

if len(sys.argv) > 1:
    album_url = sys.argv[1]

    if validate_url(album_url):
        print "\nNow ripping " + tcolors.BLUE + album_url  + tcolors.END #TODO: grab album title from json
        if(rip_it_up(album_url)):
            print tcolors.GREEN + "\n\nDownload Complete" + tcolors.END
        else:
            print tcolors.RED + "\n\nAh, that's a real ding there" + tcolors.END
    else:
        print "What this is?"
        # change_song_details('tests/sample.mp3', 'Side A', 'Kappa Chow', 'tests/albumart.jpg', 'Summer Tour Tape', '1', '2015', 'sackville')
else:
    print "Gimmie something to rip bud!"


