# -*- coding:utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib2
import contextlib
import re
import json
import hashlib
import uuid
import random
import time

__version__ = '0.0.4'
__all__ = ['Client']

CLIENTS = {'htmlshark' : '20101222.59',
           'jsqueue' : '20101222.59'}

REFERER = 'http://grooveshark.com/JSQueue.swf?20110405.03'
HEADER_USER_AGENT = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10'}
ALBUM_COVER_URL = 'http://beta.grooveshark.com/static/amazonart/'

POPULAR_TYPE_DAILY = 'daily'
POPULAR_TYPE_MONTHLY = 'monthly'

SEARCH_TYPE_SONGS = 'Songs'
SEARCH_TYPE_ARTISTS = 'Artists'
SEARCH_TYPE_ALBUMS = 'Albums'
SEARCH_TYPE_PLAYLISTS = 'Playlists'
SEARCH_TYPE_USERS = 'Users'

RADIO_RAP = 3
RADIO_R_AND_B = 4
RADIO_ROCK = 12
RADIO_ALTERNATIVE = 13
RADIO_METAL = 17
RADIO_HIP_HOP = 29
RADIO_JAZZ = 43
RADIO_POP = 56
RADIO_ELECTRONICA = 67
RADIO_TRANCE = 69
RADIO_AMBIENT = 75
RADIO_COUNTRY = 80
RADIO_BLUEGRASS = 96
RADIO_OLDIES = 102
RADIO_PUNK = 111
RADIO_FOLK = 122
RADIO_INDIE = 136
RADIO_REGGAE = 160
RADIO_EXPERIMENTAL = 191
RADIO_BLUES = 230
RADIO_LATIN = 528
RADIO_CLASSICAL = 750
RADIO_CLASSIC_ROCK = 3529

REFRESH_TOKEN = 240

class Picture(object):
    '''
    Could be an album cover or a user picture.
    Do not use this class directly.
        
    :param url: image url
    '''
    def __init__(self, url):
        self._url = url
        self._data = None
        self._type = self._url.split('.').pop()
    
    @property
    def type(self):
        '''
        image type for example png or jpg
        '''
        return self._type
    
    @property
    def data(self):
        '''
        raw image data
        '''
        if self._data is None:
            request = urllib2.Request(self._url, headers=HEADER_USER_AGENT)
            with contextlib.closing(urllib2.urlopen(request)) as response:
                self._data = response.read()
        return self._data

class Stream(object):
    '''
    Get song's raw data.
    Do not use this class directly.
        
    :param ip: streaming server adress
    :param key: streaming key required to get the stream
    '''
    def __init__(self, ip, key):
        self._ip = ip
        self._key = key
        request = urllib2.Request('http://%s/stream.php' % (self._ip), data='streamKey=%s' % (self._key),
                                  headers=HEADER_USER_AGENT)
        self._data = urllib2.urlopen(request)
        self._size = int(self.data.info().getheader('Content-Length'))
       
    @property
    def data(self):
        '''
        A file-like object containing song's raw data.
        '''
        return self._data
    
    @property
    def size(self):
        '''
        Size of the song's raw data in bytes.
        '''
        return self._size

class Album(object):
    '''
    Represents an album.
    Do not use this class directly.
        
    :param id: internal album id
    :param name: name
    :param artist_id: artist's id to generate an :py:class:`Artist` object
    :param artist_name: artist's name to generate an :py:class:`Artist` object
    :param cover_url: album's cover to generate an :class:`Album` object
    :param connection: underlying :class:`Connection` object
    '''
    def __init__(self, id, name, artist_id, artist_name, cover_url, connection):
        self._connection = connection
        self._id = id
        self._name = name
        self._artist_id = artist_id
        self._artist_name = artist_name
        self._cover_url = cover_url
        self._songs = None
        self._cover = None
        self._artist = None

    def __str__(self):
        return '%s - %s' % (self.name, self.artist.name)
    
    @property
    def id(self):
        '''
        internal album id
        '''
        return self._id
    
    @property
    def name(self):
        '''
        album's name
        '''
        return self._name
    
    @property
    def artist(self):
        '''
        :class:`Artist` object of album's artist
        '''
        if not self._artist:
            self._artist = Artist(self._artist_id, self._artist_name, self._connection)
        return self._artist
    
    @property
    def cover(self):
        '''
        album cover as :class:`Picture` object
        '''
        if self._cover_url:
            if not self._cover:
                self._cover = Picture(self._cover_url)
            return self._cover
    
    @property
    def songs(self):
        '''
        generator generates album's songs as :class:`Song` objects
        '''
        if self._songs is None:
            self._songs = [Song.from_response(song, self._connection) for song in \
                           self._connection.request('albumGetSongs', {'albumID' : self.id, 'isVerified' : True, 'offset' : 0},
                                                    self._connection.header('albumGetSongs'))[1]['songs']]
        return iter(self._songs)

class Artist(object):
    '''
    Represents an artist.
    Do not use this class directly.
        
    :param id: internal artist id
    :param name: name
    :param connection: underlying :class:`Connection` object
    '''
    def __init__(self, id, name, connection):
        self._connection = connection
        self._id = id
        self._name = name
        self._similar = None
        self._songs = None
        
    def __str__(self):
        return self.name

    @property
    def id(self):
        '''
        internal artist id
        '''
        return self._id
    
    @property
    def name(self):
        '''
        artist's name
        '''
        return self._name

    @property
    def similar(self):
        '''
        generator generates similar artists as :class:`Artist` objects
        '''
        if self._similar is None:
            self._similar = [Artist(artist['ArtistID'], artist['Name'], self._connection) for artist in \
                             self._connection.request('artistGetSimilarArtists', {'artistID' : self.id},
                                                      self._connection.header('artistGetSimilarArtists'))[1]['SimilarArtists']]
        return iter(self._similar)
    
    @property
    def songs(self):
        '''
        generator generates artist's songs as :class:`Song` objects
        '''
        if self._songs is None:
            self._songs = [Song.from_response(song, self._connection) for song in \
                           self._connection.request('artistGetSongs', {'artistID' : self.id, 'isVerified' : True, 'offset' : 0},
                                                    self._connection.header('artistGetSongs'))[1]['songs']]
        return iter(self._songs)
             
class Song(object):
    '''
    Represents a song.
    Do not use this class directly.
        
    :param id: internal song id
    :param name: name
    :param artist_id: artist's id to generate an :py:class:`Artist` object
    :param artist_name: artist's name to generate an :py:class:`Artist` object
    :param album_id: album's id to generate an :class:`Album` object
    :param album_name: album's name to generate an :class:`Album` object
    :param cover_url: album's cover to generate an :class:`Album` object
    :param track: track number
    :param duration: estimate song duration
    :param popularity: populaity
    :param connection: underlying :class:`Connection` object
    '''
    def __init__(self, id, name, artist_id, artist_name, album_id, album_name, cover_url, track, duration, popularity, connection):
        self._connection = connection
        self._id = id
        self._name = name
        self._artist_id = artist_id
        self._artist_name = artist_name
        self._album_id = album_id
        self._album_name = album_name
        self._album_id = album_id
        self._album_name = album_name
        self._cover_url = cover_url
        self._track = track
        self._duration = duration
        self._popularity = popularity
        self._artist = None
        self._album = None
        
    def __str__(self):
        return '%s - %s - %s' % (self.name, self.artist.name, self.album.name)
    
    @classmethod
    def from_response(cls, song, connection):
        return cls(song['SongID'], song['Name'], song['ArtistID'], song['ArtistName'], song['AlbumID'], song['AlbumName'],
                   song['CoverArtFilename'], song['TrackNum'], song['EstimateDuration'], song['Popularity'], connection)
    
    @property
    def id(self):
        '''
        internal song id
        '''
        return self._id
    
    @property
    def name(self):
        '''
        name
        '''
        return self._name
    
    @property
    def artist(self):
        '''
        artist as :class:`Artist` object
        '''
        if not self._artist:
            self._artist = Artist(self._artist_id, self._artist_name, self._connection)
        return self._artist
    
    @property
    def album(self):
        '''
        album as :class:`Album` object
        '''
        if not self._album:
            self._album = Album(self._album_id, self._album_name, self._artist_id, self._artist_name, self._cover_url, self._connection)
        return self._album
    
    @property
    def track(self):
        '''
        track number
        '''
        return self._track
    
    @property
    def duration(self):
        '''
        estimate song duration
        '''
        return self._duration
    
    @property
    def popularity(self):
        '''
        populaity
        '''
        return self._popularity
    
    @property
    def stream(self):
        '''
        :class:`Stream` object for playing
        '''
        stream_info = self._connection.request('getStreamKeyFromSongIDEx', {'songID' : self.id, 'country' : self._connection.country,
                                                                            'prefetch' : False, 'mobile' : False},
                                               self._connection.header('getStreamKeyFromSongIDEx', 'jsqueue'))[1]
        return Stream(stream_info['ip'], stream_info['streamKey'])

class User(object):
    '''
    Represents a user.
    Do not use this class directly.
        
    :param id: internal user id
    :param username: username
    :param picture: picture as :class:`Picture` object
    :param city: city
    :param sex: sex
    :param country: country
    :param connection: underlying :class:`Connection` object
    :param complete: ``True`` if some user information is missing 
    '''
    def __init__(self, id, username, picture_url, city, sex, country, connection, complete=False):
        self._connection = connection
        self._id = id
        self._name = username
        self._picture_url = picture_url
        self._city = city
        self._sex = sex
        self._country = country
        self._complete = complete
        self._picture = None
    
    def __str__(self):
        return self.name
    
    def _complete_information(self):
        '''
        Use getUserByID method to fetch user information if it is not complete
        '''
        user = self._connection.request('getUserByID', {'userID' : self.id},
                                        self._connection.header('getUserByID'))[1]['User']
        self._picture = Picture('http://beta.grooveshark.com/static/userimages/%s' % (user['Picture']))
        self._city = user['City']
        self._country = user['Country']
        self._sex = user['Sex']
        self._complete = False

    @property
    def id(self):
        '''
        internal user id
        '''
        return self._id
    
    @property
    def name(self):
        '''
        name
        '''
        return self._name

    @property
    def picture(self):
        '''
        picture as :class:`Picture` object
        '''
        if self._complete:
            self._complete_information()
        if not self._picture and self._picture_url:
            self._picture = Picture(self._picture_url)
        return self._picture
    
    @property
    def city(self):
        '''
        city
        '''
        if self._complete:
            self._complete_information()
        return self._city
    
    @property
    def country(self):
        '''
        country
        '''
        if self._complete:
            self._complete_information()
        return self._country
    
    @property
    def sex(self):
        '''
        sex
        '''
        if self._complete:
            self._complete_information()
        return self._sex

class Playlist(object):
    '''
    Represents a playlist.
    Do not use this class directly.
        
    :param id: internal playlist id
    :param name: name    
    :param user_id: user's id who owns the playlist 
    :param user_name: user's name who owns the playlist 
    :param variety: variety
    :param num_artists: number of artists
    :param num_songs: number of songs
    :param about: about
    :param rank: song's rank
    :param score: song's score
    :param connection: underlying :class:`Connection` object
    '''
    def __init__(self, id, name, user_id, user_name, variety, num_artists, num_songs, about, rank, score, connection):
        self._connection = connection
        self._id = id
        self._name = name
        self._user_id = user_id
        self._user_name = user_name
        self._variety = variety
        self._num_artists = num_artists
        self._num_songs = num_songs
        self._about = about
        self._rank = rank
        self._score = score
        self._songs = None
        self._user = None
    
    def __str__(self):
        return '%s - %s' % (self.name, self.user.name)

    @property
    def id(self):
        '''
        internal playlist id
        '''
        return self._id
    
    @property
    def name(self):
        '''
        name
        '''
        return self._name
    
    @property
    def variety(self):
        '''
        variety of songs
        '''
        return self._variety
    
    @property
    def num_artists(self):
        '''
        number of artists
        '''
        return self._num_artists
    
    @property
    def num_songs(self):
        '''
        number of songs
        '''
        return self._num_songs
    
    @property
    def about(self):
        '''
        about
        '''
        return self._about

    @property
    def rank(self):
        '''
        playlist's rank
        '''
        return self._rank
    
    @property
    def score(self):
        '''
        playlist's score
        '''
        return self._score

    @property
    def user(self):
        '''
        user owns the playlist as :class:`User` object
        '''
        if not self._user:
            self._user = User(self._user_id, self._user_name, None, None, None, None, self._connection, True)
        return self._user
    
    @property
    def songs(self):
        '''
        generator generates playlist's :class:`Song` objects
        '''
        if self._songs is None:
            self._songs = [Song.from_response(song, self._connection) for song in \
                           self._connection.request('playlistGetSongs', {'playlistID' : self.id},
                                                    self._connection.header('playlistGetSongs'))[1]['Songs']]
        return iter(self._songs)

class Radio(object):
    '''
    Listen to songs by specifc genre.
    Do not use this class directly.
    
    :param artists: list of artist ids
    :param radio: the genre (see :class:`Client`'s :meth:`radio` method)
    :param connection: the underlying :class:`Connection` object
    '''
    def __init__(self, artists, radio, connection):
        self._artists = [artist['ArtistID'] for artist in artists]
        self._radio = radio
        self._connection = connection
        self._recent_artists = []
        self._songs_already_seen = []
    
    @property
    def song(self):
        '''
        :class:`Song` object of next song to play
        '''
        song = self._connection.request('autoplayGetSong', {'weightModifierRange' : [-9,9],
                                                            'seedArtists' : dict([(artist, 'p') for artist in self._artists]),
                                                            'tagID' : self._radio, 'recentArtists' : self._recent_artists, 
                                                            'songQueueID' : self._connection.queue_id, 'secondaryArtistWeightModifier' : 0.75,
                                                            'country' : self._connection.country, 'seedArtistWeightRange' : [110,130],
                                                            'songIDsAlreadySeen' : self._songs_already_seen, 'maxDuration' : 1500,
                                                            'minDuration' : 60, 'frowns' : []},
                                        self._connection.header('autoplayGetSong', 'jsqueue'))[1]
        return Song(song['SongID'], song['SongName'], song['ArtistID'], song['ArtistName'], song['AlbumID'], song['AlbumName'],
                    song['CoverArtUrl'], None, song['EstimateDuration'], None, self._connection)

class Connection(object):
    '''
    Lowlevel api communication.
    
    :param session: stored session information as returned by :meth:`init_session` method.
    :param token: stored token information as returned by :meth:`init_token` method.   
    :param queue_id: stored queue id as returned by :meth:`init_queue` method.
    '''
    def __init__(self, session=None, token=None, queue_id=None):
        self._user = str(uuid.uuid4()).upper()
        if session:
            self._session = session['id']
            self._secret = session['secret']
            self.country = session['country']
            self._user = session['user']
        if token:
            self._token = token['token']
            self._token_time = token['time']
        if queue_id:
            self.queue_id = queue_id
    
    def _random_hex(self):
        '''
        Returns a random hex string
        '''
        hex_set = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
        return ''.join([random.choice(hex_set) for i in range(6)])
    
    def _request_token(self, method):
        '''
        Calculate request token.
        A new one is required for each request.
        '''
        if time.time() - self._token_time > REFRESH_TOKEN:
            self.init_token()
        random_value = self._random_hex()
        return random_value + hashlib.sha1(method + ':' + self._token + ':quitStealinMahShit:' + random_value).hexdigest()
    
    def _json_request_header(self):
        '''
        Return HTTP-headers for json-requests
        '''
        return {'Cookie' : 'PHPSESSID=' + self._session, 'Content-Type' : 'application/json',
                'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10',
                'Content-Type' : 'application/json',
                'Referer' : REFERER}    
    
    def _get_session(self):
        '''
        Request session id and country, calculate communication secret
        '''
        request = urllib2.Request('http://grooveshark.com', headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10'})
        with contextlib.closing(urllib2.urlopen(request)) as response:
            self._session = re.search('PHPSESSID=([a-z0-9]*)', response.info().getheader('Set-Cookie')).group(1)
            self._secret = hashlib.md5(self._session).hexdigest()
            config = json.loads(re.search(r'\<script type="text/javascript"\>window\.gsConfig = (\{.*\});\<\/script\>', response.read()).group(1))
            self.country = config['country']
    
    def _get_token(self):
        '''
        Request communication token
        '''
        self._token = self.request('getCommunicationToken', {'secretKey' : self._secret},
                                   {'uuid' :self._user,
                                    'session' : self._session,
                                    'clientRevision' : CLIENTS['htmlshark'],
                                    'country' : self.country,
                                    'privacy' : 0,
                                    'client' : 'htmlshark'})[1]
        self._token_time = time.time()
        
    def _get_queue_id(self):
        '''
        Request queue id
        '''
        self.queue_id = self.request('initiateQueue', None, self.header('initiateQueue', 'jsqueue'))[1] 
       
    def init_session(self):
        '''
        Fetch Grooveshark's session id, country and calculate communication secret
        '''
        self._get_session()
        return {'id' : self._session, 'secret' : self._secret, 'country' : self.country, 'user' : self._user}
    
    def init_token(self):
        '''
        Fetch Grooveshark's communication token requied for every request
        '''
        self._get_token()
        return {'token' : self._token, 'time' : self._token_time}
    
    def init_queue(self):
        '''
        Fetch Grooveshark's queue id
        '''
        self._get_queue_id()
        return self.queue_id
        
    def header(self, method, client = 'htmlshark'):
        '''
        Returns a header for Grooveshark's API json-requests
        '''
        return {'token' : self._request_token(method),
                'privacy' : 0,
                'uuid' : self._user,
                'clientRevision' : CLIENTS[client],
                'session' : self._session,
                'client' : client,
                'Country' : self.country}
    
    def request(self, method, parameters, header):
        '''
        Make a json-request to Grooveshark's API
        '''
        data = json.dumps({'parameters' : parameters,
                           'method' : method,
                           'header' : header})
        request = urllib2.Request('https://grooveshark.com/more.php?%s' % (method), data = data,
                                  headers = self._json_request_header())
        with contextlib.closing(urllib2.urlopen(request)) as response:
            return response.info(), json.loads(response.read())['result']

class Client(object):
    '''
    A client for Grooveshark's API which supports:
        
    * radio (songs by genre)
    * search for songs, artists, albums, playlists and users
    * popular songs
    
    :param session: stored session information as returned by :meth:`init_session` method.
    :param token: stored token information as returned by :meth:`init_token` method.   
    :param queue_id: stored queue id as returned by :meth:`init_queue` method.
    '''
    def __init__(self, session=None, token=None, queue_id=None):
        self._connection = Connection(session, token, queue_id)

    def init(self):
        '''
        Fetch Grooveshark's session, communication token and queue id.
        
        :rtype: tuple: (:meth:`init_session()`, :meth:`init_token()`, :meth:`init_queue()`)        
        '''
        return (self._connection.init_session(), self._connection.init_token(), self._connection.init_queue())
    
    def init_session(self):
        '''
        Fetch Grooveshark's session.
        
        :rtype: dictionary: {'id' : session id, 'secret' : session secret, 'country' : session country, 'user' : user id}
        
        You can store the returned dictionary and use it again over the *session* argument of the :class:`Client` class. 
        '''
        return self._connection.init_session()
    
    def init_token(self):
        '''
        Fetch Grooveshark's communication token.
        Make sure to call :meth:`init_session()` first.
        
        :rtype: dictionary: {'token' : communication token, 'time' : actual time}
        
        You can store the returned dictionary and use it again over the *token* argument of the :class:`Client` class. 
        '''
        return self._connection.init_token()
    
    def init_queue(self):
        '''
        Fetch Grooveshark's queue id.
        Make sure to call :meth:`init_token()` first.
        
        :rtype: queue id
        
        You can store the returned queue id and use it again over the *queue_id* argument of the :class:`Client` class. 
        '''
        return self._connection.init_queue()
    
    def radio(self, radio):
        '''
        Get songs belong to a specific genre.
        
        :param radio: genre to listen to
        :rtype: a :class:`Radio` object
        
        Genres:
        
        +-------------------------------------+---------------------------------+
        | Constant                            | Genre                           |
        +=====================================+=================================+
        | :const:`RADIO_RAP`                  | Rap                             |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_R_AND_B`              | R&B                             |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_ROCK`                 | Rock                            |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_ALTERNATIVE`          | Alternative                     |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_METAL`                | Metal                           |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_HIP_HOP`              | Hip Hop                         |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_JAZZ`                 | Jazz                            |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_POP`                  | Pop                             |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_ELECTRONICA`          | Electronica                     |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_TRANCE`               | Trance                          |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_AMBIENT`              | Ambient                         |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_COUNTRY`              | Country                         |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_BLUEGRASS`            | Bluegrass                       |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_OLDIES`               | Oldies                          |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_PUNK`                 | Punk                            |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_FOLK`                 | Folk                            |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_INDIE`                | Indie                           |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_REGGAE`               | Reggae                          |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_EXPERIMENTAL`         | Experimental                    |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_LATIN`                | Latin                           |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_CLASSICAL`            | Classic                         |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_BLUES`                | Blues                           |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_CLASSIC_ROCK`         | Oldies                          |
        +-------------------------------------+---------------------------------+
        '''
        artists = self._connection.request('getArtistsForTagRadio', {'tagID' : radio},
                                           self._connection.header('getArtistsForTagRadio', 'jsqueue'))[1]
        return Radio(artists, radio, self._connection)
    
    def _parse_album(self, album):
        '''
        Parse search json-data and create an :class:`Album` object.
        '''
        if album['CoverArtFilename']:
            cover_url = '%sm%s' % (ALBUM_COVER_URL, album['CoverArtFilename'])
        else:
            cover_url = None
        return Album(album['AlbumID'], album['Name'], album['ArtistID'], album['ArtistName'], cover_url, self._connection)
    
    def _parse_playlist(self, playlist):
        '''
        Parse search json-data and create a list of :class:`Playlist` objects.
        '''
        return Playlist(playlist['PlaylistID'], playlist['Name'], playlist['UserID'],  playlist['Username'],
                        playlist['Variety'], playlist['NumArtists'], playlist['NumSongs'],
                        playlist['About'], playlist['Rank'], playlist['Score'], self._connection)
            
    def _parse_user(self, user):
        '''
        Parse search json-data and create a :class:`User` object.
        '''
        if user['Picture']:
            picture = 'http://beta.grooveshark.com/static/userimages/%s' % user['Picture']
        else:
            picture = None
        return User(user['UserID'], user['Username'], picture, user['City'], user['Sex'], user['Country'], self._connection)
    
    def search(self, query, type=SEARCH_TYPE_SONGS):
        '''
        Search for songs, artists, albums, playlists, users and events.
        
        :param query: search string
        :param radio: type to search for
        :rtype: a generator generates :class:`Song`, :class:`Artist`, :class:`Album`, :class:`Playlist` or :class:`User` objects
        
        Search Types:
               
        +---------------------------------+---------------------------------+
        | Constant                        | Meaning                         |
        +=================================+=================================+
        | :const:`SEARCH_TYPE_SONGS`      | Search for songs                |
        +---------------------------------+---------------------------------+
        | :const:`SEARCH_TYPE_ARTISTS`    | Search for artists              |
        +---------------------------------+---------------------------------+
        | :const:`SEARCH_TYPE_ALBUMS`     | Search for albums               |
        +---------------------------------+---------------------------------+
        | :const:`SEARCH_TYPE_PLAYLISTS`  | Search for playlists            |
        +---------------------------------+---------------------------------+
        | :const:`SEARCH_TYPE_USERS`      | Search for users                |
        +---------------------------------+---------------------------------+
        '''
        result = self._connection.request('getSearchResultsEx', {'query' : query, 'type' : type, 'guts' : 0, 'ppOverride' : False},
                                          self._connection.header('getSearchResultsEx'))[1]['result']
        if type == SEARCH_TYPE_SONGS:
            return (Song.from_response(song, self._connection) for song in result)
        elif type == SEARCH_TYPE_ARTISTS:
            return (Artist(artist['ArtistID'], artist['Name'], self._connection) for artist in result)
        elif type == SEARCH_TYPE_ALBUMS:
            return (self._parse_album(album) for album in result)
        elif type == SEARCH_TYPE_PLAYLISTS:
            return (self._parse_playlist(playlist) for playlist in result)
        elif type == SEARCH_TYPE_USERS:
            return (self._parse_user(user) for user in result)

    def popular(self, period=POPULAR_TYPE_DAILY):
        '''
        Get popular songs.
        
        :param period: time period 
        :rtype: a generator generates :class:`Song` objects
        
        Time periods:
        
        +---------------------------------+-------------------------------------+
        | Constant                        | Meaning                             |
        +=================================+=====================================+
        | :const:`POPULAR_TYPE_DAILY`     | Popular songs of this day           |
        +---------------------------------+-------------------------------------+
        | :const:`POPULAR_TYPE_MONTHLY`   | Popular songs of this month         |
        +---------------------------------+-------------------------------------+
        '''
        songs = self._connection.request('popularGetSongs', {'type' : period}, self._connection.header('popularGetSongs'))[1]['Songs']
        return (Song.from_response(song, self._connection) for song in songs)