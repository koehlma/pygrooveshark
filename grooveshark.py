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
import re
import json
import hashlib
import uuid
import random
import time

__version__ = '0.0.3'
__all__ = ['Song', 'Artist', 'Album', 'Playlist', 'User', 'Event', 'Radio', 'Connection', 'Client']

CLIENTS = {'htmlshark' : '20101222.59',
           'jsqueue' : '20101222.59'}

REFERER = 'http://grooveshark.com/JSQueue.swf?20110405.03'

POPULAR_TYPE_DAILY = 'daily'
POPULAR_TYPE_MONTHLY = 'monthly'

SEARCH_TYPE_SONGS = 'Songs'
SEARCH_TYPE_ARTISTS = 'Artists'
SEARCH_TYPE_ALBUMS = 'Albums'
SEARCH_TYPE_PLAYLISTS = 'Playlists'
SEARCH_TYPE_USERS = 'Users'
SEARCH_TYPE_EVENTS = 'Events'

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

class Song(object):
    def __init__(self, data, connection):
        self._data = data
        self._connection = connection
        self.id = data['SongID']
        if 'Name' in data:
            self.name = data['Name']
        else:
            self.name = data['SongName']
        if 'Popularit' in data:
            self.popularity = data['Popularit']
        else:
            self.popularity = None
        self.album = data['AlbumName'], data['AlbumID']
        self.artist = data['ArtistName'], data['ArtistID']
        if 'TrackNum' in data:
            self.track = data['TrackNum']
        else:
            self.track = None
        if 'CoverArtFilename' in data:
            self.cover = 'http://beta.grooveshark.com/static/amazonart/m%s' % (data['CoverArtFilename'])
        elif 'CoverArtUrl' in data:
            self.cover = data['CoverArtUrl']
        else:
            self.cover = None
        self.duration = data['EstimateDuration']
    
    def __str__(self):
        return '%s - %s - %s' % (self.name, self.artist[0], self.album[0])
    
    def get_stream(self):
        stream_info = self._connection.get_stream_info(self.id)
        stream_key = stream_info['streamKey']
        stream_server = stream_info['ip']
        request = urllib2.Request('http://%s/stream.php' % (stream_server), data = 'streamKey=%s' % (stream_key),
                                  headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10'})
        response = urllib2.urlopen(request)
        return response, int(response.info().getheader('Content-Length'))
    
    def get_cover_raw(self):
        if self.cover:
            request = urllib2.Request(self.cover,
                                      headers =  {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10'})
            return urllib2.urlopen(request).read(), self.cover.split('.').pop()
        else:
            return None
    
    def get_artist(self):
        return Artist(self._connection.get_artist_by_id(self.artist[1]), self._connection)

    def get_album(self):
        return Album(self._connection.get_album_by_id(self.album[1]), self._connection)
    
class Artist(object):
    def __init__(self, data, connection):
        self._connection = connection
        self._data = data
        self.id = data['ArtistID']
        self.name = data['Name']

    def __str__(self):
        return self.name

    def get_similar(self):
        return [Artist(artist, self._connection) for artist in self._connection.get_artist_similar(self.id)]

    def get_songs(self):
        return [Song(song, self._connection) for song in self._connection.get_artist_songs(self.id)]

class Album(object):
    def __init__(self, data, connection):
        self._connection = connection
        self._data = data
        self.id = data['AlbumID']
        self.name = data['Name']
        self.artist = data['ArtistName'], data['ArtistID']
        if data['CoverArtFilename']:
            self.cover = self.cover = 'http://beta.grooveshark.com/static/amazonart/m%s' % (data['CoverArtFilename'])
        else:
            self.cover = None
    
    def __str__(self):
        return '%s - %s' % (self.name, self.artist[0])
    
    def get_songs(self):
        return [Song(song, self._connection) for song in self._connection.get_album_songs(self.id)]
    
    def get_cover_raw(self):
        if self.cover:
            request = urllib2.Request(self.cover,
                                      headers =  {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10'})
            return urllib2.urlopen(request).read(), self.cover.split('.').pop()
        else:
            return None

class Playlist(object):
    def __init__(self, data, connection):
        self._connection = connection
        self._data = data
        self.id = data['PlaylistID']
        self.name = data['Name']
        self.user = data['Username'], data['UserID']
        if 'Variety' in data:
            self.variety = data['Variety']
        else:
            self.variety = None
        if 'NumArtists' in data:
            self.num_artists = data['NumArtists']
        else:
            self.num_artists = None
        if 'NumSongs' in data:
            self.num_songs = data['NumSongs']
        else:
            self.num_songs = None
        if 'Rank' in data: 
            self.rank = data['Rank']
        else:
            self.rank = None
        if 'Score' in data:
            self.score = data['Score']
        else:
            self.score = None
        if 'Artists' in data:
            self.artists = data['Artists']
        else:
            self.artists = None
        self.about = data['About']
    
    def __str__(self):
        return '%s - %s' % (self.name, self.user[0])
    
    def get_songs(self):
        return [Song(song, self._connection) for song in self._connection.get_playlist_songs(self.id)]
    
    def get_user(self):
        return User(self._connection.get_user_by_id(self.user[1]), self._connection)
        
class User(object):
    def __init__(self, data, connection):
        self._connection = connection
        self._data = data
        self.id = data['UserID']
        self.name = data['Username']
        if 'NumFollowers' in data:
            self.num_followers = data['NumFollowers']
        else:
            self.num_followers = None
        if 'Name' in data:
            self.real_name = data['Name']
        else:
            self.real_name = None
        if data['Picture']:
            self.picture = 'http://beta.grooveshark.com/static/userimages/%s' % (data['Picture'])
        else:
            self.picture = None
        self.city = data['City']
        self.country = data['Country']
        self.sex = data['Sex']
    
    def __str__(self):
        return self.name
    
    def get_picture_raw(self):
        if self.picture:
            request = urllib2.Request(self.picture,
                                      headers =  {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10'})
            return urllib2.urlopen(request).read(), self.picture.split('.').pop()
        else:
            return None
    
    def get_playlists(self):
        playlists = []
        for playlist in self._connection.get_user_playlists(self.id):
            playlist['Username'] = self.name
            playlists.append(Playlist(playlist, self._connection))
        return playlists
    
    def get_favorites(self):
        return [Song(song, self._connection) for song in self._connection.get_user_favorites(self.id)]

class Event(object):
    def __init__(self, data, connection):
        self._connection = connection
        self._data = data
        self.name = data['EventName']
        self.artist = data['ArtistName']
        self.tickets_url = data['TicketsURL']
        self.city = data['City']
        self.rank = data['Rank']
    
    def __str__(self):
        return self.name

class Radio(object):
    def __init__(self, data, radio, connection):
        self._artists = [artist['ArtistID'] for artist in data]
        self._radio = radio
        self._connection = connection
        self._recent_artists = []
        self._songs_already_seen = []
    
    def _get_song(self):
        song = Song(self._connection.get_autoplay_song(self._artists, self._radio, self._recent_artists, self._songs_already_seen),
                    self._connection)
        self._recent_artists.append(song.artist[1])
        self._songs_already_seen.append(song.id)
        return song
        
    def get_songs(self):
        while True:
            yield self._get_song()

class Connection(object):
    def __init__(self, session=None, token=None, queue_id=None):
        self._user = str(uuid.uuid4()).upper()
        if session:
            self._session = session['id']
            self._secret = session['secret']
            self._country = session['country']
            self._user = session['user']
        if token:
            self._token = token['token']
            self._token_time = token['time']
        if queue_id:
            self._queue_id = queue_id
    
    def _random_hex(self):
        hex_set = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
        return ''.join([random.choice(hex_set) for i in range(6)])
    
    def _request_token(self, method):
        if time.time() - self._token_time > REFRESH_TOKEN:
            self.init_token()
        random_value = self._random_hex()
        return random_value + hashlib.sha1(method + ':' + self._token + ':quitStealinMahShit:' + random_value).hexdigest()
    
    def _json_request_header(self):
        return {'Cookie' : 'PHPSESSID=' + self._session, 'Content-Type' : 'application/json',
                'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10',
                'Content-Type' : 'application/json',
                'Referer' : REFERER}
    
    def _json_header(self, method, client = 'htmlshark'):
        return {'token' : self._request_token(method),
                'privacy' : 0,
                'uuid' : self._user,
                'clientRevision' : CLIENTS[client],
                'session' : self._session,
                'client' : client,
                'Country' : self._country}
    
    def _json_request(self, method, parameters, header):
        data = json.dumps({'parameters' : parameters,
                           'method' : method,
                           'header' : header})
        request = urllib2.Request('https://grooveshark.com/more.php?%s' % (method), data = data,
                                  headers = self._json_request_header())
        response = urllib2.urlopen(request)
        return response.info(), json.loads(response.read())['result']         
    
    def _get_session(self):
        request = urllib2.Request('http://grooveshark.com', headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10'})
        response = urllib2.urlopen(request)
        self._session = re.search('PHPSESSID=([a-z0-9]*)', response.info().getheader('Set-Cookie')).group(1)
        self._secret = hashlib.md5(self._session).hexdigest()
        config = json.loads(re.search(r'\<script type="text/javascript"\>window\.gsConfig = (\{.*\});\<\/script\>', response.read()).group(1))
        self._country = config['country']
    
    def _get_token(self):
        self._token = self._json_request('getCommunicationToken', {'secretKey' : self._secret},
                                         {'uuid' :self._user,
                                          'session' : self._session,
                                          'clientRevision' : CLIENTS['htmlshark'],
                                          'country' : self._country,
                                          'privacy' : 0,
                                          'client' : 'htmlshark'})[1]
        self._token_time = time.time()
    
        
    def _get_queue_id(self):
        self._queue_id = self._json_request('initiateQueue', None, self._json_header('initiateQueue', 'jsqueue'))[1] 
        
    def init_session(self):
        self._get_session()
        return {'id' : self._session, 'secret' : self._secret, 'country' : self._country, 'user' : self._user}
    
    def init_token(self):
        self._get_token()
        return {'token' : self._token, 'time' : self._token_time}
    
    def init_queue(self):
        self._get_queue_id()
        return self._queue_id 
    
    def get_popular_songs(self, type=POPULAR_TYPE_DAILY):
        return self._json_request('popularGetSongs', {'type' : type}, self._json_header('popularGetSongs'))[1]['Songs']
    
    
    def get_search_results(self, query, type=SEARCH_TYPE_SONGS):
        return self._json_request('getSearchResultsEx', {'query' : query, 'type' : type,
                                                         'guts':0, 'ppOverride' : False},
                                  self._json_header('getSearchResultsEx'))[1]['result']
    
    def get_album_by_id(self, id):
        return self._json_request('getAlbumByID', {'albumID' : id}, self._json_header('getAlbumByID'))[1]

    def get_album_songs(self, id):
        return self._json_request('albumGetSongs', {'albumID' : id, 'isVerified' : True, 'offset' : 0},
                                  self._json_header('albumGetSongs'))[1]['songs']
    
    def get_artist_by_id(self, id):
        return self._json_request('getArtistByID', {'artistID' : id}, self._json_header('getArtistByID'))[1]
                                  
    def get_artist_songs(self, id):
        return self._json_request('artistGetSongs', {'artistID' : id, 'isVerified' : True, 'offset' : 0},
                                  self._json_header('artistGetSongs'))[1]['songs']

    def get_artist_similar(self, id):
        return self._json_request('artistGetSimilarArtists', {'artistID' : id},
                                  self._json_header('artistGetSimilarArtists'))[1]['SimilarArtists']
    
    def get_stream_info(self, id):
        return self._json_request('getStreamKeyFromSongIDEx', {'songID' : id, 'country' : self._country,
                                                               'prefetch' : False, 'mobile' : False},
                                  self._json_header('getStreamKeyFromSongIDEx', 'jsqueue'))[1]
    
    def get_artists_for_tag_radio(self, radio):
        return self._json_request('getArtistsForTagRadio', {'tagID' : radio},
                                  self._json_header('getArtistsForTagRadio', 'jsqueue'))[1]
    
    def get_autoplay_song(self, artists, radio, recent_artists=[], songs_already_seen=[], frowns=[]):
        return self._json_request('autoplayGetSong', {'weightModifierRange' : [-9,9],
                                                      'seedArtists' : dict([(artist, 'p') for artist in artists]),
                                                      'tagID' : radio, 'recentArtists' : recent_artists, 
                                                      'songQueueID' : self._queue_id, 'secondaryArtistWeightModifier' : 0.75,
                                                      'country' : self._country, 'seedArtistWeightRange' : [110,130],
                                                      'songIDsAlreadySeen' : songs_already_seen, 'maxDuration' : 1500,
                                                      'minDuration' : 60, 'frowns' : frowns},
                                  self._json_header('autoplayGetSong', 'jsqueue'))[1]
    
    def get_playlist_songs(self, id):
        return self._json_request('playlistGetSongs', {'playlistID' : id},
                                  self._json_header('playlistGetSongs'))[1]['Songs']
    
    def get_user_by_id(self, id):
        return self._json_request('getUserByID', {'userID' : id},
                                  self._json_header('getUserByID'))[1]['User']
    
    def get_user_playlists(self, id):
        return self._json_request('userGetPlaylists', {'userID' : id},
                                  self._json_header('userGetPlaylists'))[1]['Playlists']
    
    def get_user_favorites(self, id):
        return self._json_request('getFavorites', {'userID' : id, 'ofWhat' : 'Songs'},
                                  self._json_header('getFavorites'))[1]

class Client(object):
    def __init__(self, session=None, token=None, queue_id=None):
        self._connection = Connection(session, token, queue_id)

    def init(self):
        return (self._connection.init_session(), self._connection.init_token(), self._connection.init_queue())
    
    def init_session(self):
        return self._connection.init_session()
    
    def init_token(self):
        return self._connection.init_token()
    
    def init_queue(self):
        return self._connection.init_queue()
    
    def radio(self, radio):
        return Radio(self._connection.get_artists_for_tag_radio(radio), radio, self._connection)
    
    def search(self, query, type=SEARCH_TYPE_SONGS):
        if type == SEARCH_TYPE_SONGS:
            return [Song(song, self._connection) for song in self._connection.get_search_results(query, type)]
        elif type == SEARCH_TYPE_ARTISTS:
            return [Artist(artist, self._connection) for artist in self._connection.get_search_results(query, type)]
        elif type == SEARCH_TYPE_ALBUMS:
            return [Album(album, self._connection) for album in self._connection.get_search_results(query, type)]
        elif type == SEARCH_TYPE_PLAYLISTS:
            return [Playlist(playlist, self._connection) for playlist in self._connection.get_search_results(query, type)]
        elif type == SEARCH_TYPE_USERS:
            return [User(user, self._connection) for user in self._connection.get_search_results(query, type)]
        elif type == SEARCH_TYPE_EVENTS:
            return [Event(event, self._connection) for event in self._connection.get_search_results(query, type)]
        else:
            return self._connection.get_search_results(query, type)
    
    def popular(self, type=POPULAR_TYPE_DAILY):
        return [Song(song, self._connection) for song in self._connection.get_popular_songs()]