# -*- coding:utf-8 -*-
#
# Copyright (C) 2012, Maximilian Köhl <linuxmaxi@googlemail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys

import contextlib
import hashlib
import json
import pickle
import random
import time
import uuid

if sys.version_info.major == 3:
    import urllib.request as urllib
else:
    import urllib2 as urllib

import grooveshark.const
from grooveshark.classes import *

__version__ = '3.0'
__project__ = 'Python Grooveshark'
__short_name__ = 'pygrooveshark'
__author__ = 'Maximilian Köhl'
__email__ = 'linuxmaxi@googlemail.com'
__website__ = 'http://www.github.com/koehlma/pygrooveshark'
__download_url__ = 'https://github.com/koehlma/pygrooveshark/tarball/master'
__source__ = 'https://github.com/koehlma/pygrooveshark/'
__vcs__ = 'git://github.com/koehlma/pygrooveshark.git'
__copyright__ = 'Copyright (C) 2012, Maximilian Köhl'
__desc_short__ = 'An unofficial Grooveshark API for Python.'
__desc_long__ = ('This is an unofficial Grooveshark API for Python. It supports'
                 'the popular songs list as well as searching for songs, albums,'
                 'artists and listening to radio stations. This also works in'
                 'Germany where Grooveshark officially is not available. It'
                 'supports Python 2 as well as Python 3.')

__all__ = ['Session', 'Client', 'Connection', 'GroovesharkError', 'RequestError', 'UnknownError']

class GroovesharkError(Exception): pass
class RequestError(GroovesharkError): pass
class UnknownError(GroovesharkError): pass

class Session():
    def __init__(self):
        self.user = str(uuid.uuid4())
        self.session = hashlib.md5(self.user.encode('utf-8')).hexdigest()
        self.secret = hashlib.md5(self.session.encode('utf-8')).hexdigest()
        self.country = grooveshark.const.COUNTRY
        self.queue = None
        self.token = None
        self.time = None
    
    def __repr__(self):
        return '<Session user="{}", sessions="{}", secret="{}", country="{}">'.format(self.user, self.session, self.secret, self.country)
    
    @classmethod
    def open(cls, filename):
        with open(filename, 'rb') as input:
            return pickle.load(input)
    
    def save(self, filename):
        with open(filename, 'wb') as output:
            pickle.dump(self, output)

class Connection():
    '''
    Lowlevel api communication.
    
    :param session: a :class:`Session` object with session information.
    :param proxies: dictionary mapping protocol to proxy.
    '''
    def __init__(self, session=None, proxies=None):
        self.session = Session() if session is None else session
        self.urlopen = urllib.build_opener(urllib.ProxyHandler(proxies)).open
    
    def _random_hex(self):
        '''
        Generates a random hex string.
        '''
        return ''.join([random.choice('0123456789abcdef') for i in range(6)])
    
    def _json_request_header(self):
        '''
        Generates json http request headers.
        '''
        return {'Cookie' : 'PHPSESSID=' + self.session.session, 'Content-Type' : 'application/json',
                'User-Agent' : grooveshark.const.USER_AGENT, 'Content-Type' : 'application/json'}
    
    def _get_token(self):
        '''
        Requests an communication token from grooveshark.
        '''
        self.session.token = self.request('getCommunicationToken', {'secretKey' : self.session.secret},
                                          {'uuid' :self.session.user,
                                           'session' : self.session.session,
                                           'clientRevision' : grooveshark.const.CLIENTS['htmlshark']['version'],
                                           'country' : self.session.country,
                                           'privacy' : 0,
                                           'client' : 'htmlshark'})[1]
        self.session.time = time.time()
    
    def _request_token(self, method, client):
        '''
        Generates a request token.
        '''
        if time.time() - self.session.time > grooveshark.const.TOKEN_TIMEOUT:
            self._get_token()
        random_value = self._random_hex()
        return random_value + hashlib.sha1((method + ':' + self.session.token + ':' + grooveshark.const.CLIENTS[client]['token'] + ':' + random_value).encode('utf-8')).hexdigest()
    
    def init(self):
        '''
        Initiate session, token and queue.
        '''
        return self.init_token(), self.init_queue()
        
    def init_token(self):
        '''
        Initiate token.
        '''
        self._get_token()
    
    def init_queue(self):
        '''
        Request queue id.
        '''
        self.session.queue = self.request('initiateQueue', None, self.header('initiateQueue', 'jsqueue'))[1]
    
    def request(self, method, parameters, header):
        '''
        Grooveshark api request.
        '''
        data = json.dumps({'parameters' : parameters, 'method' : method, 'header' : header})
        request = urllib.Request('https://grooveshark.com/more.php?%s' % (method),
                                         data=data.encode('utf-8'), headers=self._json_request_header())
        with contextlib.closing(self.urlopen(request)) as response:
            result = json.loads(response.read().decode('utf-8'))
            if 'result' in result:
                return response.info(), result['result']
            elif 'fault' in result:
                raise RequestError(result['fault']['message'], result['fault']['code'])
            else:
                raise UnknownError(result)
    
    def header(self, method, client='htmlshark'):
        '''
        Generates Grooveshark api json header.
        ''' 
        return {'token' : self._request_token(method, client),
                'privacy' : 0,
                'uuid' : self.session.user,
                'clientRevision' : grooveshark.const.CLIENTS[client]['version'],
                'session' : self.session.session,
                'client' : client,
                'country' : self.session.country}
        
class Client(object):
    '''
    A client for Grooveshark's API which supports:
        
    * radio (songs by genre)
    * search for songs, artists and albums
    * popular songs
    
    :param session: a :class:`Session` object with session information.
    :param proxies: dictionary mapping protocol to proxy.
    '''
    
    DAILY = 'daily'
    MONTHLY = 'monthly'
    
    SONGS = 'Songs'
    ARTISTS = 'Artists'
    ALBUMS = 'Albums'
    
    def __init__(self, *args, **kwargs):
        self.connection = Connection(*args, **kwargs)

    def init(self):
        '''
        Fetch Grooveshark's token and queue id.
        
        :rtype: tuple: (:meth:`init_session()`, :meth:`init_token()`, :meth:`init_queue()`)        
        '''
        self.connection.init()
    
    def init_token(self):
        '''
        Fetch Grooveshark's communication token.
        '''
        return self.connection.init_token()
    
    def init_queue(self):
        '''
        Initiate queue.
        Make sure to call :meth:`init_token()` first.
        '''
        return self.connection.init_queue()
    
    def radio(self, radio):
        '''
        Get songs belong to a specific genre.
        
        :param radio: genre to listen to
        :rtype: a :class:`Radio` object
        
        Genres:
        
        This list is incomplete because there isn't a English translation for some genres.
        Please look at the sources for all possible Tags.
        
        +-------------------------------------+---------------------------------+
        | Constant                            | Genre                           |
        +=====================================+=================================+
        | :const:`Radio.GENRE_RNB`            | R and B                         |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_JAZZ`           | Jazz                            |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_ROCK`           | Rock                            |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_CLASSICAL`      | Classical                       |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_DUBSTEP`        | Dubstep                         |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_BLUES`          | Blues                           |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_FOLK`           | Folk                            |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_ELECTRONICA`    | Electronica                     |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_CHRISTMAS`      | Christmas                       |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_OLDIES`         | Oldies                          |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_COUNTRY`        | Country                         |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_EXPERIMENTAL`   | Experimental                    |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_POP`            | Pop                             |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_INDIE`          | Indie                           |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_BLUEGRASS`      | Bluegrass                       |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_RAP`            | Rap                             |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_AMBIENT`        | Ambient                         |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_TRANCE`         | Trance                          |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_REGGAE`         | Reggae                          |
        +-------------------------------------+---------------------------------+
        | :const:`Radio.GENRE_METAL`          | Metal                           |
        +-------------------------------------+---------------------------------+
        '''
        artists = self.connection.request('getArtistsForTagRadio', {'tagID' : radio},
                                          self.connection.header('getArtistsForTagRadio', 'jsqueue'))[1]
        return Radio(artists, radio, self.connection)
    
    def _parse_album(self, album):
        '''
        Parse search json-data and create an :class:`Album` object.
        '''
        if album['CoverArtFilename']:
            cover_url = '%sm%s' % (grooveshark.const.ALBUM_COVER_URL, album['CoverArtFilename'])
        else:
            cover_url = None
        return Album(album['AlbumID'], album['Name'], album['ArtistID'], album['ArtistName'], cover_url, self.connection)
       
    def search(self, query, type=SONGS):
        '''
        Search for songs, artists and albums.
        
        :param query: search string
        :param type: type to search for
        :rtype: a generator generates :class:`Song`, :class:`Artist` and :class:`Album` objects
        
        Search Types:
               
        +---------------------------------+---------------------------------+
        | Constant                        | Meaning                         |
        +=================================+=================================+
        | :const:`Client.SONGS`           | Search for songs                |
        +---------------------------------+---------------------------------+
        | :const:`Client.ARTISTS`         | Search for artists              |
        +---------------------------------+---------------------------------+
        | :const:`Client.ALBUMS`          | Search for albums               |
        +---------------------------------+---------------------------------+
        '''
        result = self.connection.request('getResultsFromSearch', {'query' : query, 'type' : type, 'guts' : 0, 'ppOverride' : False},
                                         self.connection.header('getResultsFromSearch'))[1]['result']
        if type == self.SONGS:
            return (Song.from_response(song, self.connection) for song in result)
        elif type == self.ARTISTS:
            return (Artist(artist['ArtistID'], artist['Name'], self.connection) for artist in result)
        elif type == self.ALBUMS:
            return (self._parse_album(album) for album in result)

    def popular(self, period=DAILY):
        '''
        Get popular songs.
        
        :param period: time period 
        :rtype: a generator generates :class:`Song` objects
        
        Time periods:
        
        +---------------------------------+-------------------------------------+
        | Constant                        | Meaning                             |
        +=================================+=====================================+
        | :const:`Client.DAILY`           | Popular songs of this day           |
        +---------------------------------+-------------------------------------+
        | :const:`Client.MONTHLY`         | Popular songs of this month         |
        +---------------------------------+-------------------------------------+
        '''
        songs = self.connection.request('popularGetSongs', {'type' : period}, self.connection.header('popularGetSongs'))[1]['Songs']
        return (Song.from_response(song, self.connection) for song in songs)