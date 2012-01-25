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

from grooveshark.classes import *
from grooveshark.core.const import *
from grooveshark.core.connection import Connection

POPULAR_TYPE_DAILY = 'daily'
POPULAR_TYPE_MONTHLY = 'monthly'

SEARCH_TYPE_SONGS = 'Songs'
SEARCH_TYPE_ARTISTS = 'Artists'
SEARCH_TYPE_ALBUMS = 'Albums'

RADIO_KPOP = 1765
RADIO_CHINESE = 4266
RADIO_RAGGA = 4281
RADIO_DANCE = 71
RADIO_ORCHESTRA = 2760
RADIO_NEOFOLK = 1139
RADIO_POSTROCK = 422
RADIO_MEDITATION = 700
RADIO_SYNTHPOP = 163
RADIO_BHANGRA = 130
RADIO_SAMBA = 4285
RADIO_ACAPELLA = 4263
RADIO_TURKISH = 689
RADIO_JAZZBLUES = 4275
RADIO_SKA = 100
RADIO_SYMPHONICMETAL = 4287
RADIO_DANCEHALL = 269
RADIO_MPB = 819
RADIO_BEAT = 1475
RADIO_RNB = 877
RADIO_JAZZ = 43
RADIO_ACIDJAZZ = 3519
RADIO_UNDERGROUND = 468
RADIO_PSYCHOBILLY = 3909
RADIO_DESI = 2512
RADIO_WORLD = 313
RADIO_INDIEFOLK = 1221
RADIO_BANDA = 4264
RADIO_JPOP = 568
RADIO_PROGRESSIVE = 97
RADIO_BLACKMETAL = 4265
RADIO_SKAPUNK = 1110
RADIO_EMO = 131
RADIO_BLUESROCK = 1106
RADIO_DISCO = 899
RADIO_OPERA = 1535
RADIO_HARDSTYLE = 4274
RADIO_40S = 2837
RADIO_MINIMAL = 2177
RADIO_ROCK = 12
RADIO_ACOUSTIC = 105
RADIO_GOSPEL = 1489
RADIO_NUJAZZ = 3518
RADIO_CLASSICAL = 750
RADIO_HOUSE = 48
RADIO_DUBSTEP = 2563
RADIO_MATHROCK = 4277
RADIO_BLUES = 230
RADIO_VALLENATO = 89
RADIO_FOLK = 122
RADIO_CHRISTIANROCK = 4268
RADIO_90S = 9
RADIO_HEAVYMETAL = 1054
RADIO_TEJANO = 789
RADIO_ELECTRONICA = 67
RADIO_MOTOWN = 4278
RADIO_GOA = 2556
RADIO_SOFTROCK = 1311
RADIO_SOUTHERNROCK = 1298
RADIO_RB = 4282
RADIO_CHRISTMAS = 703
RADIO_DISNEY = 623
RADIO_VIDEOGAME = 115
RADIO_NOISE = 171
RADIO_CHRISTIAN = 439
RADIO_BASS = 585
RADIO_OLDIES = 102
RADIO_SINGERSONGWRITER = 923
RADIO_SMOOTHJAZZ = 3855
RADIO_70S = 588
RADIO_TECHNO = 47
RADIO_PAGODE = 3606
RADIO_POPROCK = 3468
RADIO_SCREAMO = 166
RADIO_CONTEMPORARYCHRISTIAN = 4270
RADIO_DOWNTEMPO = 153
RADIO_CLASSICCOUNTRY = 4269
RADIO_SOUNDTRACK = 72
RADIO_OI = 4280
RADIO_CHRISTIANMETAL = 4267
RADIO_COUNTRY = 80
RADIO_THRASHMETAL = 4289
RADIO_FUNKY = 398
RADIO_PUNKROCK = 1754
RADIO_ANIME = 120
RADIO_SWING = 1032
RADIO_CLASSICROCK = 3529
RADIO_POSTHARDCORE = 1332
RADIO_EXPERIMENTAL = 191
RADIO_INDUSTRIAL = 275
RADIO_AMERICANA = 922
RADIO_POP = 56
RADIO_JESUS = 1356
RADIO_ALTERNATIVEROCK = 1259
RADIO_MEDIEVAL = 2585
RADIO_TEXASCOUNTRY = 4288
RADIO_RAVE = 271
RADIO_ELECTRONIC = 123
RADIO_POWERMETAL = 4063
RADIO_CHANSON = 3692
RADIO_DNB = 273
RADIO_CRUNK = 748
RADIO_DUB = 3501
RADIO_GRIME = 268
RADIO_TANGO = 2868
RADIO_SCHLAGER = 3162
RADIO_DEATHMETAL = 4273
RADIO_CHILLOUT = 251
RADIO_MELODIC = 929
RADIO_REGGAETON = 940
RADIO_GRUNGE = 134
RADIO_INDIEPOP = 573
RADIO_RELAX = 1941
RADIO_CLUB = 1038
RADIO_POPPUNK = 1333
RADIO_HARDCORE = 245
RADIO_INDIEROCK = 1138
RADIO_FUNK = 397
RADIO_NEOSOUL = 4279
RADIO_TRIPHOP = 158
RADIO_JROCK = 434
RADIO_MERENGUE = 84
RADIO_SOUL = 520
RADIO_RUMBA = 3454
RADIO_PROGRESSIVEROCK = 4137
RADIO_EURODANCE = 4028
RADIO_FOLKROCK = 925
RADIO_ISLAND = 2294
RADIO_SERTANEJO = 4286
RADIO_METALCORE = 705
RADIO_50S = 1087
RADIO_VOCAL = 6
RADIO_INDIE = 136
RADIO_BLUEGRASS = 96
RADIO_JAZZFUSION = 4276
RADIO_DARKWAVE = 2139
RADIO_8BIT = 2145
RADIO_RAP = 3
RADIO_AMBIENT = 75
RADIO_FLAMENCO = 85
RADIO_BRITPOP = 534
RADIO_TRANCE = 69
RADIO_NUMETAL = 1103
RADIO_ROOTSREGGAE = 4284
RADIO_LOUNGE = 765
RADIO_80S = 55
RADIO_ELECTRO = 162
RADIO_BEACH = 912
RADIO_SURF = 1408
RADIO_REGGAE = 160
RADIO_60S = 266
RADIO_DCIMA = 4272
RADIO_ROCKSTEADY = 4283
RADIO_HIPHOP = 1
RADIO_ELECTROPOP = 893
RADIO_ROCKABILLY = 1086
RADIO_SALSA = 81
RADIO_PSYCHEDELIC = 1168
RADIO_CELTIC = 513
RADIO_METAL = 17
RADIO_CUMBIA = 4271
RADIO_JUNGLE = 248
RADIO_ZYDECO = 4290

class Client(object):
    '''
    A client for Grooveshark's API which supports:
        
    * radio (songs by genre)
    * search for songs, artists and albums
    * popular songs
    
    :param session: stored session information as returned by :meth:`init_session` method.
    :param token: stored token information as returned by :meth:`init_token` method.
    :param queue_id: stored queue id as returned by :meth:`init_queue` method.
    :param proxies: dictionary mapping protocol to proxy.
    '''
    def __init__(self, *args, **kwargs):
        self._connection = Connection(*args, **kwargs)

    def init(self):
        '''
        Fetch Grooveshark's session and token.
        
        :rtype: tuple: (:meth:`init_session()`, :meth:`init_token()`, :meth:`init_queue()`)        
        '''
        return (self._connection.init_session(), self._connection.init_token(), self._connection.init_queue())
    
    def init_session(self):
        '''
        Fetch Grooveshark's session.
        
        :rtype: tuple: (session, secret, country, user)        
        
        You can store the returned tuple and use it again over the *session* argument of the :class:`Client` class. 
        '''
        return self._connection.init_session()
    
    def init_token(self):
        '''
        Fetch Grooveshark's communication token.
        Make sure to call :meth:`init_session()` first.
        
        :rtype: tuple: (token, token_time)
        
        You can store the returned tuple and use it again over the *token* argument of the :class:`Client` class. 
        '''
        return self._connection.init_token()
    
    def init_queue(self):
        '''
        Initiate queue.
        Make sure to call :meth:`init_session()` and :meth:`init_token()` first.
        
        :rtype: queue_id
        
        You can store the returned queue_id and use it again over the *queue_id* argument of the :class:`Client` class. 
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
        | :const:`RADIO_RNB`                  | R&B                             |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_JAZZ`                 | Jazz                            |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_ROCK`                 | Rock                            |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_CLASSICAL`            | Classical                       |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_DUBSTEP`              | Dubstep                         |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_BLUES`                | Blues                           |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_FOLK`                 | Folk                            |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_ELECTRONICA`          | Electronica                     |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_CHRISTMAS`            | Christmas                       |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_OLDIES`               | Oldies                          |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_COUNTRY`              | Country                         |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_EXPERIMENTAL`         | Experimental                    |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_POP`                  | Pop                             |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_INDIE`                | Indie                           |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_BLUEGRASS`            | Bluegrass                       |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_RAP`                  | Rap                             |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_AMBIENT`              | Ambient                         |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_TRANCE`               | Trance                          |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_REGGAE`               | Reggae                          |
        +-------------------------------------+---------------------------------+
        | :const:`RADIO_METAL`                | Metal                           |
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
        #return Playlist(playlist['PlaylistID'], playlist['Name'], playlist['UserID'],  playlist['Username'],
        #                playlist['Variety'], playlist['NumArtists'], playlist['NumSongs'],
        #                playlist['About'], playlist['Rank'], playlist['Score'], self._connection)
            
    def _parse_user(self, user):
        '''
        Parse search json-data and create a :class:`User` object.
        '''
        #if user['Picture']:
        #    picture = 'http://beta.grooveshark.com/static/userimages/%s' % user['Picture']
        #else:
        #    picture = None
        #return User(user['UserID'], user['Username'], picture, user['City'], user['Sex'], user['Country'], self._connection)
    
    def search(self, query, type=SEARCH_TYPE_SONGS):
        '''
        Search for songs, artists and albums.
        
        :param query: search string
        :param radio: type to search for
        :rtype: a generator generates :class:`Song`, :class:`Artist` and :class:`Album` objects
        
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
        '''
        result = self._connection.request('getResultsFromSearch', {'query' : query, 'type' : type, 'guts' : 0, 'ppOverride' : False},
                                          self._connection.header('getResultsFromSearch'))[1]['result']
        if type == SEARCH_TYPE_SONGS:
            return (Song.from_response(song, self._connection) for song in result)
        elif type == SEARCH_TYPE_ARTISTS:
            return (Artist(artist['ArtistID'], artist['Name'], self._connection) for artist in result)
        elif type == SEARCH_TYPE_ALBUMS:
            return (self._parse_album(album) for album in result)

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