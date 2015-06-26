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

move_to_itunes = False

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

def download_path():
    if move_to_itunes == True:
        return '~/Music/iTunes/iTunes Music/Automatically Add to iTunes/'
    else:
        return '~/Downloads/'

def change_song_details(audio_path, title, artist_info, track_num):
    mp3 = MP3(audio_path, ID3=ID3)
    set_tags(mp3)
    set_album_art(mp3, artist_info['album_art'], 'image/jpg')
    mp3.save()

    id3 = ID3(audio_path)
    set_album_name(id3, artist_info['album'])
    set_title(id3, title)
    set_artist(id3, artist_info['artist'])
    set_track_number(id3, str(track_num))
    # set_year(id3, artist_info['year'])
    # set_genre(id3, artist_info['genre'])
    id3.save()

def set_tags(mp3):
    try:
        mp3.add_tags()
    except error as e:
        # print e
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

def make_directory(path):
    if not os.path.exists(os.path.expanduser(path)):
        try:
            os.makedirs(os.path.expanduser(path))
        except error as e:
            print e
            pass

def download_file(url, path, filename, album_json, title, track_num):
    make_directory(path)
    download_url = urllib2.urlopen(url)
    file_and_path = os.path.expanduser(path + filename)
    file = open(file_and_path, 'wb')
    meta = download_url.info()
    file_size = int(meta.getheaders('Content-Length')[0])

    print '\nDownloading: %s Size: %s' % (tcolors.BOLD + filename + tcolors.END, tcolors.BOLD + str(round(file_size / float(1000000), 2)) + "MB" + tcolors.END)

    file_size_dl = 0
    block_sz = 8192

    while True:
        buffer = download_url.read(block_sz)

        if not buffer:
            if track_num:
                change_song_details(file_and_path, title, album_json, track_num)
            else:
                album_json['album_art'] = file_and_path
            break

        file_size_dl += len(buffer)
        file.write(buffer)
        status = r'%10d  [%3.2f%%]' % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)

        print status,

    file.close()

def download_album(album_json):
    directory = download_path() + re.sub('/', '', album_json['artistinfo'][0]['album']) + '/'

    download_file(album_json['artistinfo'][0]['album_art'], directory, 'cover.jpg', album_json['artistinfo'][0], '', 0)

    for t in album_json['trackinfo']:
        download_file(t['file']['mp3-128'], directory, create_file_name(t['track_num'], t['title']), album_json['artistinfo'][0], t['title'], t['track_num'])

    return True

def create_file_name(track_number, title):
    return re.sub('/', '', ('0' if track_number < 10 else '') + str(track_number) + ' ' + title + '.mp3')

def find_album_json(garbage):
    album_json = None
    track_regex = re.compile('trackinfo\s\:\s\[')

    artist_name = sanitise_variable(re.compile('artist:\s\"'), garbage)
    album_name = sanitise_variable(re.compile('album_title:\s\"'), garbage)
    album_art_url = sanitise_variable(re.compile('artFullsizeUrl:\s\"'), garbage)
    track_json = re.sub('\}\]', '}]}', re.sub(track_regex, ',\"trackinfo\":[', find_json(garbage, track_regex, ',', ']')))

    if artist_name and album_name and track_json:
        extra_json = '{ "artistinfo": [{ "artist":"%s", "album":"%s", "album_art":"%s" }]' % (artist_name, album_name, album_art_url)
        album_json = json.loads(re.sub('\\\\', '', extra_json + track_json))

        print '\nDownloading: ' + tcolors.BLUE + album_name  + tcolors.END

    return album_json

def sanitise_variable(regex, garbage):
    return re.sub('"', '', re.sub(regex, '', find_json(garbage, regex, ',', '"')))

def find_json(garbage, regex, nail, coffin):
    for m in regex.finditer(garbage):
        start = m.start()

    if start:
        i = start
        end = None
        while not end:
            if garbage[i] is nail and garbage[i-1] is coffin:
                end = i
            i += 1

        return garbage[start:end]
    else:
        return None

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

def check_argvs():
    for args in sys.argv:
        if args == '-i':
            move_to_itunes = True
            sys.argv[1] = sys.argv[2]

if len(sys.argv) > 1:
    check_argvs()

    album_url = sys.argv[1]

    if validate_url(album_url):
        if(rip_it_up(album_url)):
            print '\n\nDownloading: ' + tcolors.GREEN + 'Completed' + tcolors.END
        else:
            print tcolors.RED + '\n\nAh, that\'s a real ding there' + tcolors.END
    else:
        print 'What this is?'
else:
    print 'Gimmie something to rip bud!'


