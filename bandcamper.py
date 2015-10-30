 #!/usr/bin/env python
import urllib
import urllib2
import json
import re
import os.path
import readline, glob
import string
import sys
import pprint
import shutil
from urlparse import urlparse
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, ID3, TALB, TPE1, TPE2, TRCK, TCON, TDRC, error
import unicodedata

class BC(object):
    def __init__(self):
        self._type = 'album'
        self._artwork = ''
        self._artist = ''
        self._album = ''

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def artwork(self):
        return self._artwork

    @artwork.setter
    def artwork(self, value):
        self._artwork = value

    @property
    def artist(self):
        return self._artist

    @artist.setter
    def artist(self, value):
        self._artist = value.decode('utf-8')

    @property
    def album(self):
        return self._album

    @album.setter
    def album(self, value):
        self._album = value.decode('utf-8')

class tcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def validate_url(url):
    url = urlparse(url)

    if url.scheme != 'https' and url.scheme !='http':
        print 'The url needs to start with http or https'
        return False

    domain = string.split(url.netloc, '.')

    if (domain[0] == 'www' and domain[0] != 'bandcamp') and (domain[0] != 'bandcamp'):
        print 'This doesn\'t look like a bandcamp url'
        return False

    domain = string.split(url.path, '/')

    if domain[1] != 'album' and domain[1] != 'track':
        print 'You must provide an album or track'
        return False
    else:
        if domain[1] == 'track':
            BC.type = 'track'

    try:
        urllib2.urlopen(url.geturl())
        return True
    except:
        return False

def download_path():
    return '~/Downloads/'

def change_song_details(audio_path, title, album_art, track_num):
    mp3 = MP3(audio_path, ID3=ID3)
    set_tags(mp3)
    set_album_art(mp3, album_art, 'image/jpg')
    mp3.save()

    id3 = ID3(audio_path)
    set_album_name(id3, BC.album)
    set_title(id3, title)
    set_artist(id3, BC.artist)
    set_track_number(id3, str(track_num))

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

def validateURL(url):
    if url[:5] == 'http:' or url[:6] == 'https:':
        return url
    else:
        if url[:2] == '//':
            return 'https:' + url
        else:
            print '\nShoot, the url we found wasn\'t valid'
            return False

def download_file(url, path, filename, album_json, title, track_num):
    make_directory(path)
    download_url = urllib2.urlopen(url)
    file_and_path = os.path.expanduser(path + filename)
    file = open(file_and_path, 'wb')
    meta = download_url.info()
    file_size = int(meta.getheaders('Content-Length')[0])

    print '\nDownloading: %s Size: %s' % (tcolors.BOLD + filename + tcolors.END, tcolors.BOLD + str(round(file_size / float(1000000), 2)) + "MB" + tcolors.END)

    file_size_dl = 0
    block_sz = 4096

    while True:
        buffer = download_url.read(block_sz)

        if not buffer:
            if track_num:
                change_song_details(file_and_path, title, album_json['album_art'], track_num)
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
    if BC.type == 'album':
        directory = download_path() + re.sub('/', '', BC.album) + '/'
    else:
        directory = download_path() + re.sub('/', '', BC.artist) + '/'

    aURL = validateURL(album_json['artistinfo'][0]['album_art'])

    if aURL:
        download_file(aURL, directory, 'cover.jpg', album_json['artistinfo'][0], '', 0)

    for t in album_json['trackinfo']:
        tURL = validateURL(t['file']['mp3-128'])

        if tURL:
            download_file(tURL, directory, create_file_name(t['track_num'], t['title'].decode('utf-8')), album_json['artistinfo'][0], t['title'].decode('utf-8'), t['track_num'])

    if(check_argvs('-i')):
        copytree(os.path.expanduser(directory), os.path.expanduser('~/Music/iTunes/iTunes Media/Automatically Add to iTunes.localized/' + album_json['artistinfo'][0]['album']))

    return True

def create_file_name(track_number, title):
    return re.sub('/', '', ('0' if track_number < 10 else '') + str(track_number) + ' ' + title + '.mp3')

def find_album_json(garbage):
    album_json = None

    if BC.type == 'track':
        track_regex = re.compile('trackinfo:\s\[')
    else:
        track_regex = re.compile('trackinfo\s\:\s\[')

    artist_name = sanitise_variable(re.compile('artist:\s\"'), garbage)
    album_art_url = sanitise_variable(re.compile('artFullsizeUrl:\s\"'), garbage)
    track_json = re.sub('\}\]', '}]}', re.sub(track_regex, ',\"trackinfo\":[', find_json(garbage, track_regex, ',', ']')))

    try:
        album_name = sanitise_variable(re.compile('album_title:\s\"'), garbage)
    except error as e:
        album_name = ''

    try:
        BC.artist = artist_name
        BC.album = album_name
        BC.artwork = album_art_url
        print artist_name
        print album_name
    except error as e:
        print e

    if artist_name and track_json:
        extra_json = '{ "artistinfo": [{ "artist":"%s", "album":"%s", "album_art":"%s" }]' % (artist_name, album_name, album_art_url)
        garb = re.sub('\\\\', '', filter(lambda x: x in string.printable, extra_json) + filter(lambda x: x in string.printable, track_json))
        album_json = json.loads(garb.decode('utf8'))



        if BC.type == 'album':
            print '\nDownloading: ' + tcolors.BLUE + album_name  + tcolors.END
        else:
            print '\nDownloading: ' + tcolors.BLUE + artist_name  + tcolors.END

    return album_json

def sanitise_variable(regex, garbage):
    return re.sub('"', '', re.sub(regex, '', find_json(garbage, regex, ',', '"'))).decode('utf-8')

def find_json(garbage, regex, nail, coffin):
    start = None

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
        return ''

def rip_it_up(album_url):
    response = urllib2.urlopen(album_url)

    if(response.getcode() == 200):
        garbage = response.read()
        album_json = find_album_json(garbage)
        if album_json:
            success = download_album(album_json)
        else:
            success = False
    else:
        success = False

    return success

def check_argvs(needle):
    for args in sys.argv:
        if args == needle:
            return True

    return False

def get_album_url():
    for args in sys.argv:
        if 'bandcamp.com' in args:
            return args

    return False

def copytree(src, dst, symlinks = False, ignore = None):
    make_directory(dst)

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

    shutil.rmtree(src)

if len(sys.argv) > 1:
    album_url = get_album_url()

    if validate_url(album_url):
        if(rip_it_up(album_url)):
            print '\n\nDownloading: ' + tcolors.GREEN + 'Completed' + tcolors.END
        else:
            print tcolors.RED + '\n\nAh, that\'s a real ding there' + tcolors.END
    else:
        print 'What this is?'
else:
    print 'Gimmie something to rip bud!'


