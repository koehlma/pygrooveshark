# -*- coding:utf-8 -*-

'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import urllib2
import re
import json
import hashlib
import uuid
import random
import time

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

COVER_SIZE_SMALL = 's'
COVER_SIZE_MEDIUM = 'm'

REFRESH_TOKEN = 240

class Song(object):
    def __init__(self, data, client):
        self.id = data['SongID']
        self.name = data['Name']
        self.popularity = data['Popularity']
        self.album = data['AlbumName'], data['AlbumID']
        self.artist = data['ArtistName'], data['ArtistID']
        self.track = data['TrackNum']
        self.cover = data['CoverArtFilename']
        self.duration = data['EstimateDuration']
        self._client = client
        self._data = data
    
    def __str__(self):
        return '%s - %s - %s - %s' % (self.id, self.name, self.artist[0], self.album[0])
    
    def get_stream(self):
        stream_info = self._client.get_stream_info(self.id)
        stream_key = stream_info['streamKey']
        stream_server = stream_info['ip']
        request = urllib2.Request('http://%s/stream.php' % (stream_server), data = 'streamKey=%s' % (stream_key),
                                  headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10'})
        response = urllib2.urlopen(request)
        return response, int(response.info().getheader('Content-Length'))
    
    def get_cover_raw(self, size=COVER_SIZE_MEDIUM):
        if self.cover:
            request = urllib2.Request('http://beta.grooveshark.com/static/amazonart/%s%s' % (size, self.cover),
                                      headers =  {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10'})
            return urllib2.urlopen(request).read(), self.cover.split('.').pop()
        else:
            return None
        
    def get_artist(self):
        return Artist(self._client.get_artist_by_id(self.artist[1]), self._client)

    def get_album(self):
        return Album(self._client.get_album_by_id(self.album[1]), self._client)
        
class Artist(object):
    def __init__(self, data, client):
        self.id = data['ArtistID']
        self.name = data['Name']
        self._client = client
        self._data = data

    def __str__(self):
        return '%s - %s' % (self.id, self.name)

    def get_similar(self):
        return [Artist(artist, self._client) for artist in self._client.get_artist_similar(self.id)]

    def get_songs(self):
        return [Song(song, self._client) for song in self._client.get_artist_songs(self.id)]

class Album(object):
    def __init__(self, data, client):
        self.id = data['AlbumID']
        self.name = data['Name']
        self.artist = data['ArtistName'], data['ArtistID']
        self.cover = data['CoverArtFilename']
        self._client = client
        self._data = data
    
    def __str__(self):
        return '%s - %s - %s' % (self.id, self.name, self.artist[0])
    
    def get_songs(self):
        return [Song(song, self._client) for song in self._client.get_album_songs(self.id)]
    
    def get_cover_raw(self, size=COVER_SIZE_MEDIUM):
        if self.cover:
            request = urllib2.Request('http://beta.grooveshark.com/static/amazonart/%s%s' % (size, self.cover),
                                      headers =  {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10'})
            return urllib2.urlopen(request).read(), self.cover.split('.').pop()
        else:
            return None

class ClientBase(object):
    def __init__(self):
        self._user = str(uuid.uuid4()).upper()
        
    def _random_hex(self):
        hex_set = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
        return ''.join([hex_set[random.randint(0, 15)] for i in range(6)])
    
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
    
    def init_session(self):
        request = urllib2.Request('http://grooveshark.com', headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10'})
        response = urllib2.urlopen(request)
        self._session = re.search('PHPSESSID=([a-z0-9]*)', response.info().getheader('Set-Cookie')).group(1)
        self._secret = hashlib.md5(self._session).hexdigest()
        config = json.loads(re.search(r'\<script type="text/javascript"\>window\.gsConfig = (\{.*\});\<\/script\>', response.read()).group(1))
        self._country = config['country']
    
    def init_token(self):
        data = json.dumps({'parameters' : {'secretKey' : self._secret},
                           'method' : 'getCommunicationToken',
                           'header' : {'uuid' :self._user,
                                       'session' : self._session,
                                       'clientRevision' : CLIENTS['htmlshark'],
                                       'country' : self._country,
                                       'privacy' : 0,
                                       'client' : 'htmlshark'}})
        request = urllib2.Request('https://grooveshark.com/more.php?getCommunicationToken', data = data,
                                  headers = self._json_request_header())
        response = urllib2.urlopen(request)
        self._token = json.loads(response.read())['result']
        self._token_time = time.time()
        
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
    
class Client(object):
    def __init__(self):
        self._client = ClientBase()
    
    def init(self):
        self._client.init_session()
        self._client.init_token()
    
    def init_session(self):
        self._client.init_session()
    
    def init_token(self):
        self._client.init_token()
    
    def search(self, query, type=SEARCH_TYPE_SONGS):
        if type == SEARCH_TYPE_SONGS:
            return [Song(song, self._client) for song in self._client.get_search_results(query, type)]
        elif type == SEARCH_TYPE_ARTISTS:
            return [Artist(artist, self._client) for artist in self._client.get_search_results(query, type)]
        elif type == SEARCH_TYPE_ALBUMS:
            return [Album(album, self._client) for album in self._client.get_search_results(query, type)]
        else:
            return self._client.get_search_results(query, type)
    
    def popular(self, type=POPULAR_TYPE_DAILY):
        return [Song(song, self._client) for song in self._client.get_popular_songs()]